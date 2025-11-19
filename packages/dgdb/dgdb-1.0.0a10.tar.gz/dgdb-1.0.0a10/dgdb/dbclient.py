"""
Database Client (dgdb) - A flexible SQLAlchemy-based database client
"""

import logging
import os
from contextlib import contextmanager
from string import Template
from time import perf_counter, sleep
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Generator,
)

import sqlalchemy.exc
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import (
    DatabaseError,
    ResourceClosedError,
    ProgrammingError,
    SQLAlchemyError,
    OperationalError,
    DisconnectionError,
)
from sqlalchemy.engine.base import Connection as SQLAlchemyConnection

from .db_connection_config import DBConnectionConfig
from .common_vars import ConnectionFields, SQLSource


class DBConnectionError(Exception):
    """Custom exception for database connection issues."""
    pass


class DBClient:
    """Database client for managing connections and executing queries."""

    def __init__(
            self,
            db_conn: dict[str, Any] | DBConnectionConfig,
            future: bool = True,
            do_initialize: bool = True,
            auto_reconnect: bool = True,
            reconnect_attempts: int = 3,
            reconnect_delay: float = 5.0,
            *args,
            **kwargs,
    ):
        """Initialize the database client."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.args = args
        self.kwargs = kwargs
        self.future = future
        self.auto_reconnect = auto_reconnect
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay

        # Validate and store connection config
        if isinstance(db_conn, dict):
            self.db_conn = DBConnectionConfig(**db_conn)
        else:
            self.db_conn = db_conn

        # Connection attributes
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None

        if do_initialize:
            self.create_engine()

    def get_conn_str(self) -> str:
        """Generate connection string from configuration."""
        if self.db_conn.dialect == "mssql+pytds":
            from sqlalchemy.dialects import registry
            registry.register("mssql.pytds", "sqlalchemy_pytds.dialect", "MSDialect_pytds")

        if self.db_conn.db_host and self.db_conn.db_port:
            if "oracle" in self.db_conn.dialect.lower() and ".orcl" in self.db_conn.db_name:
                return (
                    f"{self.db_conn.dialect}://{self.db_conn.db_user}:{self.db_conn.db_pass}@"
                    f"{self.db_conn.db_host}:{self.db_conn.db_port}/?service_name={self.db_conn.db_name}"
                )
            return (
                f"{self.db_conn.dialect}://{self.db_conn.db_user}:{self.db_conn.db_pass}@"
                f"{self.db_conn.db_host}:{self.db_conn.db_port}/{self.db_conn.db_name}"
            )
        return f"{self.db_conn.dialect}://{self.db_conn.db_user}:{self.db_conn.db_pass}@{self.db_conn.db_name}"

    def create_engine(self) -> None:
        """Create SQLAlchemy engine with connection pooling."""
        connect_str = self.get_conn_str()
        if not self.kwargs.get("pool_pre_ping"):
            self.kwargs["pool_pre_ping"] = True
        if not self.kwargs.get("pool_recycle"):
            self.kwargs["pool_recycle"] = 3600
        if not self.kwargs.get("pool_size"):
            self.kwargs["pool_size"] = 5
        if not self.kwargs.get("max_overflow"):
            self.kwargs["max_overflow"] = 0
        try:
            self.engine = create_engine(
                connect_str,
                future=self.future,
                *self.args,
                **self.kwargs,
            )
            self.logger.info(f"Created engine for {self.db_conn.dialect}")
        except sqlalchemy.exc.ArgumentError as e:
            self.logger.error(f"Failed to create engine: {str(e)}")
            self.engine = create_engine(connect_str, future=True, *self.args, **self.kwargs)

    def create_metadata(self) -> None:
        """Initialize SQLAlchemy metadata."""
        if not self.metadata:
            self.metadata = MetaData()
            self.logger.debug("Initialized database metadata")

    def set_conn(self) -> None:
        """Create connection for SQLAlchemy."""
        self.create_engine()
        self.create_metadata()
        self.logger.info("Initialized SQLAlchemy engine")

    def close_conn(self) -> None:
        """Close connection and dispose engine."""
        if self.engine:
            try:
                self.engine.dispose()
            except Exception as e:
                self.logger.warning(f"Error disposing engine: {str(e)}")
            finally:
                self.engine = None

        self.logger.info("Disposed engine")

    def reconnect(self) -> None:
        """Reconnect to the database."""
        self.logger.info("Attempting to reconnect to database...")
        self.close_conn()
        sleep(self.reconnect_delay)
        self.set_conn()
        self.logger.info("Reconnected to database successfully")

    def ensure_connection(self) -> None:
        """Ensure database connection is alive, reconnect if necessary."""
        if not self.auto_reconnect:
            return

        try:
            self.check_connection_status()
        except (DBConnectionError, OperationalError, DisconnectionError) as e:
            self.logger.warning(f"Connection lost: {str(e)}. Attempting to reconnect...")
            self.reconnect()

    def check_connection_status(self) -> None:
        """Verify database connection is alive."""
        try:
            if not self.engine:
                raise DBConnectionError("Engine not initialized")

            # Используем временное соединение для проверки
            with self.engine.connect() as test_conn:
                if "oracle" in self.db_conn.dialect.lower():
                    result = test_conn.execute(text("select dummy from dual"))
                else:
                    result = test_conn.execute(text("select 'X' as dummy"))

                row = result.mappings().first()
                if not row or row.get("dummy") != "X":
                    raise DBConnectionError("Connection test failed")

        except Exception as e:
            self.logger.warning(f"Connection check failed: {str(e)}")
            raise DBConnectionError(f"Database connection is not alive: {str(e)}")

    @staticmethod
    def get_sql(filename: SQLSource, encoding: str = "utf-8") -> str:
        """Read SQL from file."""
        with open(filename, "r", encoding=encoding) as file:
            return file.read()

    @contextmanager
    def session_scope(self) -> Generator[SQLAlchemyConnection, None, None]:
        """Provide transactional scope around series of operations.

        Использует одно соединение на всю транзакцию.
        """
        conn = None
        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                self.ensure_connection()

                # Создаем соединение для этой транзакции
                conn = self.engine.connect()
                transaction = conn.begin()

                try:
                    yield conn
                    transaction.commit()
                    self.logger.debug("Transaction committed")
                    break
                except Exception as e:
                    transaction.rollback()
                    self.logger.error(f"Transaction rolled back: {str(e)}")

                    if "has been rolled back" in str(e) and attempt < self.reconnect_attempts:
                        self.logger.warning(f"Transaction error, retrying (attempt {attempt + 1})...")
                        self.reconnect()
                        continue
                    raise

            except (OperationalError, DisconnectionError, DBConnectionError) as e:
                self.logger.warning(f"Database error in session (attempt {attempt}): {str(e)}")
                if attempt < self.reconnect_attempts:
                    self.reconnect()
                    continue
                raise
            finally:
                if conn:
                    conn.close()
                    self.logger.debug("Session closed")

    def get_data(
            self,
            sql: SQLSource,
            params: Optional[Dict] = None,
            encoding: str = "utf-8",
            print_script: bool = False,
            max_attempts: int = 5,
            **kwargs,
    ) -> List[Dict]:
        """Execute query and return results as list of dictionaries.

        Для автономных запросов - создает временное соединение.
        """
        for attempt in range(1, max_attempts + 1):
            try:
                self.ensure_connection()
                script = self._prepare_script(sql, encoding, **kwargs)

                if print_script:
                    print(script)

                # Для автономных запросов создаем временное соединение
                with self.engine.connect() as conn:
                    return self._execute_query(conn, script, params, attempt, max_attempts)

            except (OperationalError, DisconnectionError, DBConnectionError) as e:
                self.logger.warning(f"Connection error (attempt {attempt}/{max_attempts}): {str(e)}")
                if attempt < max_attempts:
                    self.reconnect()
                    sleep(self.reconnect_delay)
                    continue
                raise

    def get_data_with_connection(
            self,
            conn: SQLAlchemyConnection,
            sql: SQLSource,
            params: Optional[Dict] = None,
            encoding: str = "utf-8",
            print_script: bool = False,
            **kwargs,
    ) -> List[Dict]:
        """Execute query using existing connection.

        Используется внутри транзакций.
        """
        script = self._prepare_script(sql, encoding, **kwargs)

        if print_script:
            print(script)

        return self._execute_query(conn, script, params, 1, 1)

    def get_data_row(
            self,
            sql: SQLSource,
            index: int = 0,
            params: Optional[Dict] = None,
            encoding: str = "utf-8",
            print_script: bool = False,
            max_attempts: int = 5,
            **kwargs,
    ) -> Optional[Dict]:
        """Get single row from query results."""
        result = self.get_data(sql, params, encoding, print_script, max_attempts, **kwargs)
        return result[index] if result and len(result) > index else None

    def get_data_row_with_connection(
            self,
            conn: SQLAlchemyConnection,
            sql: SQLSource,
            index: int = 0,
            params: Optional[Dict] = None,
            encoding: str = "utf-8",
            print_script: bool = False,
            **kwargs,
    ) -> Optional[Dict]:
        """Get single row using existing connection."""
        result = self.get_data_with_connection(conn, sql, params, encoding, print_script, **kwargs)
        return result[index] if result and len(result) > index else None

    def run_script(
            self,
            sql: SQLSource,
            encoding: str = "utf-8",
            print_script: bool = False,
            max_attempts: int = 5,
            **kwargs,
    ) -> None:
        """Execute SQL script without returning results."""
        self.get_data(sql, None, encoding, print_script, max_attempts, **kwargs)

    def run_script_with_connection(
            self,
            conn: SQLAlchemyConnection,
            sql: SQLSource,
            encoding: str = "utf-8",
            print_script: bool = False,
            **kwargs,
    ) -> None:
        """Execute SQL script using existing connection."""
        self.get_data_with_connection(conn, sql, None, encoding, print_script, **kwargs)

    def _prepare_script(self, sql: SQLSource, encoding: str, **kwargs) -> str:
        """Prepare SQL script from file or string with template substitution."""
        if os.path.exists(sql):
            script_t = Template(self.get_sql(sql, encoding))
        else:
            script_t = Template(str(sql))
        return script_t.safe_substitute(**kwargs)

    def _execute_query(
            self,
            conn: SQLAlchemyConnection,
            script: str,
            params: Optional[Dict],
            attempt: int,
            max_attempts: int
    ) -> List[Dict]:
        """Execute SQL script."""
        result = []
        start_time = perf_counter()

        try:
            self.logger.debug(f"Executing query (attempt {attempt}/{max_attempts})")
            res = conn.execute(text(script), params or {})

            try:
                result = [dict(row) for row in res.mappings()]
            except ResourceClosedError:
                result = []

            self.logger.debug(f"Query executed in {perf_counter() - start_time:.2f}s")

        except ProgrammingError as ex:
            self.logger.error(f"SQL Error: {str(ex)}")
            raise
        except DatabaseError as ex:
            self.logger.warning(f"Database error (attempt {attempt}): {str(ex)}")

            if "has been rolled back" in str(ex) and attempt < max_attempts:
                self.logger.info("Transaction rolled back, reconnecting and retrying...")
                self.reconnect()
                raise DBConnectionError("Transaction rolled back, need to retry") from ex

            if attempt == max_attempts:
                self.logger.error(f"Max attempts reached. Last error: {str(ex)}")
                raise
            else:
                raise DBConnectionError(f"Database error: {str(ex)}") from ex

        return result

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                self.ensure_connection()
                self.create_metadata()

                # Используем временное соединение
                with self.engine.connect() as conn:
                    return self.engine.dialect.has_table(conn, table_name)

            except (OperationalError, DisconnectionError, DBConnectionError) as e:
                self.logger.warning(f"Connection error checking table (attempt {attempt}): {str(e)}")
                if attempt < self.reconnect_attempts:
                    self.reconnect()
                    continue
                raise

    def get_table(self, table_name: str) -> Table:
        """Get SQLAlchemy Table object."""
        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                self.ensure_connection()
                self.create_metadata()
                return Table(table_name, self.metadata, autoload_with=self.engine)
            except (OperationalError, DisconnectionError, DBConnectionError) as e:
                self.logger.warning(f"Connection error getting table (attempt {attempt}): {str(e)}")
                if attempt < self.reconnect_attempts:
                    self.reconnect()
                    continue
                raise


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    config = {
        "dialect": "postgresql",
        "db_user": "user",
        "db_pass": "password",
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "testdb"
    }

    client = DBClient(config, auto_reconnect=True, reconnect_attempts=3, reconnect_delay=5)

    try:
        # Способ 1: Использование session_scope (рекомендуется для транзакций)
        with client.session_scope() as session:
            # Все операции используют одно соединение
            result = session.execute(text("SELECT 1 AS test"))
            print(result.scalar())

            data = client.get_data_with_connection(
                session,
                "SELECT * FROM users WHERE id = :id",
                params={"id": 1}
            )
            print(data)

        # Способ 2: Автономные запросы (каждое в своем временном соединении)
        data = client.get_data("SELECT * FROM users WHERE id = :id", params={"id": 1})
        print(data)

        # Способ 3: Проверка существования таблицы
        exists = client.table_exists("users")
        print(f"Table exists: {exists}")

    except Exception as e:
        print(f"Operation failed: {e}")
    finally:
        client.close_conn()