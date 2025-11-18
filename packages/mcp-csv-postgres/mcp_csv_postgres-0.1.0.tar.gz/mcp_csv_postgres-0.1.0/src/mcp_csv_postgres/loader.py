"""CSV loading operations using PostgreSQL COPY."""

import csv
from pathlib import Path
from typing import Optional

import psycopg2
from psycopg2 import sql
from tqdm import tqdm

from .database import DatabaseError


def load_csv_with_copy(
    conn: psycopg2.extensions.connection,
    file_path: Path,
    table_name: str,
    delimiter: str,
    row_count: int,
    show_progress: bool = True
) -> int:
    """Load CSV file into PostgreSQL table using COPY command.

    Args:
        conn: Database connection
        file_path: Path to CSV file
        table_name: Name of target table
        delimiter: CSV delimiter character
        row_count: Total number of rows (for progress bar)
        show_progress: Whether to show progress bar

    Returns:
        Number of rows loaded

    Raises:
        DatabaseError: If load operation fails
    """
    try:
        cursor = conn.cursor()

        with open(file_path, 'r', encoding='utf-8') as f:
            if show_progress:
                progress_bar = tqdm(
                    total=row_count,
                    desc=f"Loading {file_path.name}",
                    unit=" rows"
                )

            reader = csv.reader(f, delimiter=delimiter)
            next(reader)

            copy_query = sql.SQL("COPY {} FROM STDIN WITH (FORMAT CSV, DELIMITER {})").format(
                sql.Identifier(table_name),
                sql.Literal(delimiter)
            )

            class ProgressReader:
                """Wrapper to track progress during COPY."""

                def __init__(self, file_obj, progress_bar):
                    self.file_obj = file_obj
                    self.progress_bar = progress_bar
                    self.bytes_read = 0

                def read(self, size=-1):
                    data = self.file_obj.read(size)
                    if data and self.progress_bar:
                        newlines = data.count('\n')
                        if newlines > 0:
                            self.progress_bar.update(newlines)
                    return data

                def readline(self):
                    line = self.file_obj.readline()
                    if line and self.progress_bar:
                        self.progress_bar.update(1)
                    return line

            f.seek(0)
            next(csv.reader(f, delimiter=delimiter))

            if show_progress:
                reader_wrapper = ProgressReader(f, progress_bar)
            else:
                reader_wrapper = f

            cursor.copy_expert(
                sql=copy_query.as_string(conn),
                file=reader_wrapper
            )

            conn.commit()

            if show_progress:
                progress_bar.close()

        cursor.close()

        from .database import get_row_count
        loaded_count = get_row_count(conn, table_name)
        return loaded_count

    except psycopg2.Error as e:
        conn.rollback()
        if show_progress:
            progress_bar.close()
        raise DatabaseError(f"Failed to load CSV: {str(e)}")
    except Exception as e:
        conn.rollback()
        if show_progress and 'progress_bar' in locals():
            progress_bar.close()
        raise DatabaseError(f"Failed to load CSV: {str(e)}")


def load_csv(
    file_path: str,
    dbname: str = "csvimports",
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: Optional[str] = None,
    table_name: Optional[str] = None,
    show_progress: bool = True
) -> dict:
    """Load CSV file into PostgreSQL database.

    Args:
        file_path: Path to CSV file
        dbname: Database name (default: csvimports)
        host: Database host
        port: Database port
        user: Database user
        password: Database password (optional)
        table_name: Table name (optional, derived from filename if not provided)
        show_progress: Whether to show progress bar

    Returns:
        Dictionary with load results:
        - success: bool
        - table_name: str
        - rows_loaded: int
        - database: str

    Raises:
        ValidationError: If CSV validation fails
        DatabaseError: If database operation fails
    """
    from .validator import validate_csv, get_table_name
    from .database import ensure_database_exists, create_connection, create_table_from_headers

    metadata = validate_csv(file_path)

    ensure_database_exists(dbname, host, port, user, password)

    conn = create_connection(dbname, host, port, user, password)

    final_table_name = table_name or metadata["table_name"]

    create_table_from_headers(conn, final_table_name, metadata["headers"])

    rows_loaded = load_csv_with_copy(
        conn,
        Path(file_path),
        final_table_name,
        metadata["delimiter"],
        metadata["row_count"],
        show_progress
    )

    conn.close()

    return {
        "success": True,
        "table_name": final_table_name,
        "rows_loaded": rows_loaded,
        "database": dbname
    }
