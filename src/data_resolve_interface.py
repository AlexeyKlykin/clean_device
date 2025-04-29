import sqlite3
import logging
from typing import Callable, List, Tuple
from abc import ABC, abstractmethod

from src.query_interface import AbstractInterfaceQuery
from src.schema_for_validate import AbstractTable, RowValue, StockDeviceData, TableRow

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class AbstractInterfaceConnectDB(ABC):
    @abstractmethod
    def get_all_data(self) -> List[AbstractTable]: ...

    @abstractmethod
    def get_once_data(self, row: str, val: str) -> AbstractTable | int | str: ...

    @abstractmethod
    def set_data(self, set_data: tuple): ...

    @abstractmethod
    def set_many_data(self, set_data: List[tuple]): ...

    @abstractmethod
    def update_data(
        self,
        set_data: Tuple[TableRow, RowValue],
        one_data: Tuple[TableRow, RowValue],
        two_data: Tuple[TableRow, RowValue] | None = None,
    ): ...

    @abstractmethod
    def get_repr_stock_data(
        self, stock_device_id: int, stock_device_name: str
    ) -> StockDeviceData: ...

    @abstractmethod
    def get_to_retrieve_all_broken_devices_at_date(
        self,
        clean_date: Tuple[TableRow, RowValue],
    ) -> list: ...

    @abstractmethod
    def mark_device(
        self,
        stock_device_id: Tuple[TableRow, RowValue],
        device_id: Tuple[TableRow, RowValue],
        mark: str,
    ): ...


class InterfaceConnectDB(AbstractInterfaceConnectDB):
    def __init__(
        self,
        conn: sqlite3.Connection,
        row_factory: Callable,
        query: AbstractInterfaceQuery,
    ) -> None:
        self.conn = conn
        self.conn.row_factory = row_factory
        self.query = query

    # тест
    def mark_device(
        self,
        stock_device_id: Tuple[TableRow, RowValue],
        device_id: Tuple[TableRow, RowValue],
        mark: str,
    ):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                self.query.query_mark_device(
                    stock_device_id=self.query.transform_tuple(stock_device_id),
                    device_id=self.query.transform_tuple(device_id),
                    mark=mark,
                )
            )
            cursor.close()

        except Exception as err:
            logger.warning(err)
            raise err

    # тест
    def get_to_retrieve_all_broken_devices_at_date(
        self,
        clean_date: Tuple[TableRow, RowValue],
    ) -> list:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                self.query.query_to_retrieve_all_broken_devices_at_date(
                    clean_date=self.query.transform_tuple(clean_date),
                )
            )
            res = cursor.fetchall()
            cursor.close()
            return res

        except Exception as err:
            raise err

    def get_repr_stock_data(
        self, stock_device_id: int, stock_device_name: str
    ) -> StockDeviceData:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                self.query.query_get_stock_device(
                    stock_device_id=stock_device_id, device_name=stock_device_name
                )
            )
            res = cursor.fetchone()
            cursor.close()
            return res

        except Exception as err:
            raise err

    def get_all_data(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(self.query.query_get_all())

            res = cursor.fetchall()
            cursor.close()
            return res

        except Exception as err:
            raise err

    def get_once_data(self, row: str, val: str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                self.query.query_get_data_by_value(
                    where_data=self.query.gen_data(row=row, val=val)
                )
            )
            res = cursor.fetchone()
            cursor.close()
            return res

        except Exception as err:
            raise err

    def set_data(self, set_data: tuple):
        try:
            cursor = self.conn.cursor()
            cursor.execute(self.query.query_set(), set_data)
            cursor.close()

        except Exception as err:
            raise err

    def set_many_data(self, set_data: List[tuple]):
        try:
            cursor = self.conn.cursor()
            cursor.executemany(self.query.query_set(), [item for item in set_data])
            cursor.close()

        except Exception as err:
            raise err

    def update_data(
        self,
        set_data: Tuple[TableRow, RowValue],
        one_data: Tuple[TableRow, RowValue],
        two_data: Tuple[TableRow, RowValue] | None = None,
    ):
        try:
            cursor = self.conn.cursor()

            if two_data:
                cursor.execute(
                    self.query.query_update_data_by_two_arg(
                        raw_set_data=self.query.gen_data(
                            row=set_data[0], val=set_data[1]
                        ),
                        raw_where_data_one=self.query.gen_data(
                            row=one_data[0], val=one_data[1]
                        ),
                        raw_where_data_two=self.query.gen_data(
                            row=two_data[0], val=two_data[1]
                        ),
                    )
                )

            else:
                cursor.execute(
                    self.query.query_update(
                        raw_set_data=self.query.gen_data(
                            row=set_data[0], val=set_data[1]
                        ),
                        raw_where_data=self.query.gen_data(
                            row=one_data[0], val=one_data[1]
                        ),
                    )
                )
            cursor.close()

        except Exception as err:
            raise err
