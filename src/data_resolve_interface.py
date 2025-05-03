import sqlite3
import logging
from typing import Dict, List, Type
from abc import ABC, abstractmethod

from src.query_interface import QueryInterface
from src.schema_for_validation import (
    AbstractTable,
    FabricRowFactory,
    RowValue,
    TableRow,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class AbstractDatabaseTableHandlerInterface(ABC):
    @abstractmethod
    def set_item(self, set_data: tuple): ...

    @abstractmethod
    def set_items(self, set_data_lst: List[tuple]): ...

    @abstractmethod
    def get_item(self, where_data: Dict[TableRow, RowValue]) -> AbstractTable: ...

    @abstractmethod
    def get_items(
        self,
        where_data: Dict[TableRow, RowValue] | None = None,
    ) -> List[AbstractTable]: ...

    @abstractmethod
    def update_item(
        self, set_data: Dict[TableRow, RowValue], where_data: Dict[TableRow, RowValue]
    ): ...

    @abstractmethod
    def change_device_status(
        self,
        where_data: Dict[TableRow, RowValue],
        set_data: Dict[TableRow, RowValue],
    ): ...


class DatabaseTableHandlerInterface(AbstractDatabaseTableHandlerInterface):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._schema = None
        self._query = QueryInterface()
        self.conn = conn
        self.row_fabric = FabricRowFactory()

    @property
    def schema(self):
        if self._schema:
            return self._schema
        else:
            raise Exception("Не передана схема")

    @schema.setter
    def schema(self, schema: Type[AbstractTable]):
        self._schema = schema
        self.row_fabric.choice_row_factory = self.schema
        self.conn.row_factory = self.row_fabric.choice_row_factory
        self._query.table = schema

    def change_device_status(
        self, where_data: Dict[TableRow, RowValue], set_data: Dict[TableRow, RowValue]
    ):
        cursor = self.conn.cursor()

        try:
            query = self._query.query_update(
                set_data=set_data,
                where_data=where_data,
            )
            cursor.execute(query)
            self.conn.commit()

        except sqlite3.OperationalError as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def set_item(self, set_data):
        cursor = self.conn.cursor()

        try:
            query = self._query.query_set()
            cursor.execute(query, set_data)
            self.conn.commit()

        except Exception as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def set_items(self, set_data_lst):
        cursor = self.conn.cursor()

        try:
            query = self._query.query_set()
            cursor.executemany(query, set_data_lst)
            self.conn.commit()

        except Exception as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()

    def get_item(self, where_data) -> AbstractTable:
        cursor = self.conn.cursor()

        try:
            match self.conn.row_factory.__name__:
                case "output_device_type_factory" | "output_company_factory":
                    query = self._query.query_get_data_by_value(where_data=where_data)
                    cursor.execute(query)
                    return cursor.fetchone()

                case "output_device_factory":
                    query = self._query.query_show_devices(where_data=where_data)
                    cursor.execute(query)
                    return cursor.fetchone()

                case "repr_stock_device_factory":
                    query = self._query.query_show_stock_devices(where_data=where_data)
                    cursor.execute(query)
                    return cursor.fetchone()

                case _:
                    logger.warning(
                        f"{self.conn.row_factory} не может быть передан в качестве фабрики строк"
                    )
                    raise

        except sqlite3.OperationalError as err:
            logger.warning("Скорее всего вернулость пустое значение")
            raise err

        except Exception as err:
            raise err

        finally:
            cursor.close()

    def get_items(self, where_data=None) -> List[AbstractTable]:
        cursor = self.conn.cursor()

        try:
            match self.conn.row_factory.__name__:
                case "output_device_type_factory" | "output_company_factory":
                    query = self._query.query_get_all()
                    cursor.execute(query)
                    return cursor.fetchall()

                case "output_device_factory":
                    query = self._query.query_show_all_devices()
                    try:
                        cursor.execute(query)
                        return cursor.fetchall()

                    except sqlite3.OperationalError as err:
                        raise err

                case "output_broken_device_factory":
                    if where_data:
                        query = self._query.query_show_all_broken_stock_devices_at_date(
                            where_data=where_data
                        )
                        cursor.execute(query)
                        return cursor.fetchall()

                    else:
                        raise ValueError("Не переданы аргументы строки и их значение")

                case _:
                    logger.warning(
                        f"{self.conn.row_factory} не может быть передан в качестве фабрики строк"
                    )
                    raise

        except sqlite3.OperationalError as err:
            logger.warning("Скорее всего вернулось пустое значение")
            raise err

        except Exception as err:
            raise err

        finally:
            cursor.close()

    def update_item(self, set_data, where_data):
        cursor = self.conn.cursor()

        try:
            query = self._query.query_update(set_data=set_data, where_data=where_data)
            cursor.execute(query)
            self.conn.commit()

        except Exception as err:
            self.conn.rollback()
            raise err

        finally:
            cursor.close()
