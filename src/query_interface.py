import logging
from abc import ABC, abstractmethod
from typing import (
    Dict,
    List,
    Tuple,
    Type,
)

from src.schema_for_validation import AbstractTable, RowValue, TableRow

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


## Формирование запросов
class AbstractInterfaceQuery(ABC):
    @property
    @abstractmethod
    def table_name(self) -> str: ...

    @property
    @abstractmethod
    def table_rows(self) -> str: ...

    @property
    @abstractmethod
    def count_rows(self) -> int: ...

    @staticmethod
    def gen_data(row: str, val: str) -> Tuple[TableRow, RowValue]:
        return TableRow(row), RowValue(val)

    @staticmethod
    def transform_list_rows(lst_rows: List[TableRow]):
        return ", ".join(lst_rows)

    @staticmethod
    def transform_tuple(data: Tuple[TableRow, RowValue]) -> str:
        return f"{data[0]}='{data[1]}'"

    @staticmethod
    def transform_set_data(data: Dict[TableRow, RowValue]) -> str:
        lst_set_data = [f"{key}='{val}'" for key, val in data.items()]
        return ", ".join(lst_set_data)

    @staticmethod
    def transform_where_data(data: Dict[TableRow, RowValue]) -> str:
        lst_set_data = [f"{key}='{val}'" for key, val in data.items()]
        return " and ".join(lst_set_data)

    @abstractmethod
    def query_get_all(self) -> str: ...

    @abstractmethod
    def query_set(self) -> str: ...

    @abstractmethod
    def query_update(
        self,
        set_data: Dict[TableRow, RowValue],
        where_data: Dict[TableRow, RowValue],
    ) -> str: ...

    @abstractmethod
    def query_get_data_by_value(self, where_data: Dict[TableRow, RowValue]) -> str: ...

    @abstractmethod
    def query_show_stock_devices(self, where_data: Dict[TableRow, RowValue]) -> str: ...

    @abstractmethod
    def query_show_devices(self, where_data: Dict[TableRow, RowValue]) -> str: ...

    @abstractmethod
    def query_show_all_broken_stock_devices_at_date(
        self, where_data: Dict[TableRow, RowValue]
    ) -> str: ...


class QueryInterface(AbstractInterfaceQuery):
    def __init__(self) -> None:
        self._table = None

    @property
    def table_alias(self) -> str:
        return ", ".join(self.table.table_alias())

    @property
    def table(self) -> Type[AbstractTable]:
        if self._table:
            return self._table
        else:
            raise Exception("Не передана схема таблицы")

    @table.setter
    def table(self, table: Type[AbstractTable]):
        self._table = table

    @property
    def table_name(self) -> str:
        return self.table.table_name()

    @property
    def table_rows(self) -> str:
        return ", ".join(self.table.table_rows())

    @property
    def count_rows(self) -> int:
        return len(self.table.table_rows())

    def query_show_all_broken_stock_devices_at_date(self, where_data) -> str:
        query = """SELECT {rows} 
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
WHERE {where_data} and sd.stock_device_status = '0'
"""
        return query.format(
            rows=self.table_alias,
            table=self.table_name,
            where_data=self.transform_where_data(where_data),
        )

    def query_show_stock_devices(self, where_data) -> str:
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
WHERE {where_data}
"""
        return query.format(
            rows=self.table_alias,
            table=self.table_name,
            where_data=self.transform_where_data(where_data),
        )

    def query_show_devices(self, where_data) -> str:
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device_company as dc ON dc.company_id = d.company_id
LEFT JOIN device_type as dt ON dt.type_device_id = d.type_device_id
WHERE {where_data}"""
        return query.format(
            rows=self.table_alias,
            table=self.table_name,
            where_data=self.transform_where_data(where_data),
        )

    def query_show_all_devices(self) -> str:
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device_company as dc ON dc.company_id = d.company_id
LEFT JOIN device_type as dt ON dt.type_device_id = d.type_device_id
"""
        return query.format(
            rows=self.table_alias,
            table=self.table_name,
        )

    def query_get_all(self) -> str:
        query = "SELECT {rows} FROM {table_name}"
        return query.format(rows=self.table_rows, table_name=self.table_name)

    def query_set(self) -> str:
        query = "INSERT INTO {table_name}({rows}) VALUES ({values})"
        return query.format(
            table_name=self.table_name,
            rows=self.table_rows,
            values=", ".join("?" * self.count_rows),
        )

    def query_update(
        self,
        set_data,
        where_data,
    ) -> str:
        query = "UPDATE {table_name} SET {set_data} WHERE {where_data}"
        return query.format(
            table_name=self.table_name,
            set_data=self.transform_set_data(set_data),
            where_data=self.transform_where_data(where_data),
        )

    def query_get_data_by_value(
        self,
        where_data,
    ) -> str:
        query = "SELECT {rows} FROM {table_name} WHERE {where_data}"
        return query.format(
            rows=self.table_rows,
            table_name=self.table_name,
            where_data=self.transform_where_data(where_data),
        )
