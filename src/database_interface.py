import sqlite3
import logging
from typing import Callable, Generator, Generic, List, TypeVar

from src.scheme_for_validation import AbstractTable


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class DataBaseInterfaceException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.value = args[1]
        else:
            self.message = None
            self.value = None

    def __str__(self):
        logger.warning(DataBaseInterfaceException)
        if self.message:
            return "DataResolveInterfaceException, {0} {1}".format(
                self.message, self.value
            )
        else:
            return "DataResolveInterfaceException вызвана для класса обработки данных"


Table = TypeVar("Table", covariant=True, bound=AbstractTable)


class DataBaseInterface(Generic[Table]):
    """Класс для работы с базой данных приборов"""

    __slots__ = ("db_name", "conn")

    def __init__(self, db_name: str):
        self.db_name = db_name

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            return self

        except ConnectionError as err:
            raise err

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                self.conn.close()

        except DataBaseInterfaceException:
            raise DataBaseInterfaceException(exc_type, exc_val, exc_tb)

    def row_factory_for_connection(self, scheme: Callable) -> sqlite3.Cursor:
        self.conn.row_factory = scheme
        cursor = self.conn.cursor()
        return cursor

    @staticmethod
    def get(query: str, cursor: sqlite3.Cursor) -> Table:
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result

        except DataBaseInterfaceException as err:
            raise err

        finally:
            cursor.close()

    @staticmethod
    def get_many(query: str, cursor: sqlite3.Cursor) -> Generator[List[Table]]:
        try:
            cursor.execute(query)
            while True:
                result = cursor.fetchmany(5)
                if result:
                    yield result
                else:
                    break

        except DataBaseInterfaceException as err:
            raise err

        finally:
            cursor.close()

    @staticmethod
    def get_all(query: str, cursor: sqlite3.Cursor) -> List[Table]:
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

        except DataBaseInterfaceException as err:
            raise err

        finally:
            cursor.close()

    def set(self, query: str, set_data: tuple, cursor: sqlite3.Cursor):
        try:
            cursor.execute(query, set_data)
            self.conn.commit()

        except DataBaseInterfaceException as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def update(self, query: str, cursor: sqlite3.Cursor):
        try:
            cursor.execute(query)
            self.conn.commit()

        except DataBaseInterfaceException as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def set_many(self, query: str, set_data: List[tuple], cursor: sqlite3.Cursor):
        try:
            cursor.executemany(query, set_data)
            self.conn.commit()

        except DataBaseInterfaceException as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def fill_in_the_table(self, fp_lst: List[str], create_table_list: List[str]):
        [self.conn.execute(item) for item in create_table_list]
        self.conn.commit()

        for fp in fp_lst:
            with open(fp, "r") as file:
                self.conn.executescript(file.read())
        self.conn.commit()

    def clean_table(self, table_list: List[str]):
        for table in table_list:
            self.conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            self.conn.execute("DELETE FROM '%s'" % table)
            self.conn.commit()
