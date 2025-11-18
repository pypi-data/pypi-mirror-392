"""PostgreSQL database operations."""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List, Optional


class DatabaseError(Exception):
    """Database operation error."""

    pass


def create_connection(
    dbname: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: Optional[str] = None
) -> psycopg2.extensions.connection:
    """Create database connection.

    Args:
        dbname: Database name
        host: Database host
        port: Database port
        user: Database user
        password: Database password (optional)

    Returns:
        Database connection

    Raises:
        DatabaseError: If connection fails
    """
    try:
        conn_params = {
            "dbname": dbname,
            "host": host,
            "port": port,
            "user": user,
        }
        if password:
            conn_params["password"] = password

        return psycopg2.connect(**conn_params)
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to connect to database: {str(e)}")


def ensure_database_exists(
    dbname: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: Optional[str] = None
) -> None:
    """Ensure database exists, create if it doesn't.

    Args:
        dbname: Database name to create
        host: Database host
        port: Database port
        user: Database user
        password: Database password (optional)

    Raises:
        DatabaseError: If database creation fails
    """
    try:
        conn_params = {
            "dbname": "postgres",
            "host": host,
            "port": port,
            "user": user,
        }
        if password:
            conn_params["password"] = password

        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,)
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(dbname)
                )
            )

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to ensure database exists: {str(e)}")


def create_table_from_headers(
    conn: psycopg2.extensions.connection,
    table_name: str,
    headers: List[str]
) -> None:
    """Create table with columns from CSV headers.

    Args:
        conn: Database connection
        table_name: Name of table to create
        headers: List of column names from CSV

    Raises:
        DatabaseError: If table creation fails
    """
    try:
        cursor = conn.cursor()

        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {}").format(
                sql.Identifier(table_name)
            )
        )

        columns = [
            sql.SQL("{} TEXT").format(sql.Identifier(header))
            for header in headers
        ]

        create_query = sql.SQL("CREATE TABLE {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(columns)
        )

        cursor.execute(create_query)
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Failed to create table: {str(e)}")


def get_row_count(
    conn: psycopg2.extensions.connection,
    table_name: str
) -> int:
    """Get count of rows in table.

    Args:
        conn: Database connection
        table_name: Name of table

    Returns:
        Number of rows in table

    Raises:
        DatabaseError: If query fails
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}").format(
                sql.Identifier(table_name)
            )
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to get row count: {str(e)}")
