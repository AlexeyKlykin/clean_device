import logging
from abc import ABC, abstractmethod
from typing import (
    Dict,
    Tuple,
)

from src.schema_for_validate import RowValue, TableRow

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
    def gen_data(row: str, val: str) -> Dict[TableRow, RowValue]:
        return {TableRow(row): RowValue(val)}

    @staticmethod
    def transform_tuple(data: Tuple[TableRow, RowValue]) -> str:
        return f"{data[0]}='{data[1]}'"

    @staticmethod
    def transform_data(data: Dict[TableRow, RowValue]) -> str:
        lst_set_data = [f"{key}='{val}'" for key, val in data.items()]
        return ", ".join(lst_set_data)

    @abstractmethod
    def query_get_all(self) -> str: ...

    @abstractmethod
    def query_set(self) -> str: ...

    @abstractmethod
    def query_update(
        self,
        raw_set_data: Dict[TableRow, RowValue],
        raw_where_data: Dict[TableRow, RowValue],
    ) -> str: ...

    @abstractmethod
    def query_get_data_by_value(
        self,
        where_data: Dict[TableRow, RowValue],
        rows: Dict[TableRow, RowValue] | None = None,
    ) -> str: ...

    @abstractmethod
    def query_get_stock_device(self, stock_device_id: int, device_name: str) -> str: ...

    @abstractmethod
    def query_update_data_by_two_arg(
        self,
        raw_set_data: Dict[TableRow, RowValue],
        raw_where_data_one: Dict[TableRow, RowValue],
        raw_where_data_two: Dict[TableRow, RowValue],
    ) -> str: ...

    @abstractmethod
    def query_to_retrieve_all_broken_devices_at_date(self, clean_date: str) -> str: ...

    @abstractmethod
    def query_mark_device(
        self, stock_device_id: str, device_id: str, mark: str
    ) -> str: ...


class QueryInterface(AbstractInterfaceQuery):
    def __init__(self, table) -> None:
        self.table = table

    @property
    def table_name(self) -> str:
        return self.table.table_name()

    @property
    def table_rows(self) -> str:
        return ", ".join(self.table.table_rows())

    @property
    def count_rows(self) -> int:
        return len(self.table.table_rows())

    # тест
    def query_mark_device(self, stock_device_id: str, device_id: str, mark: str):
        query = """UPDATE {table} SET stock_device_status = '{mark}'
WHERE {stock_device_id} and {device_id}
"""
        return query.format(
            table=self.table_name,
            stock_device_id=stock_device_id,
            device_id=device_id,
            mark=mark,
        )

    # тест
    def query_to_retrieve_all_broken_devices_at_date(self, clean_date: str) -> str:
        query = """SELECT sd.stock_device_id, d.device_name, sd.at_clean_date
FROM {table} sd
LEFT JOIN device d ON d.device_id = sd.device_id
WHERE {clean_date} and sd.stock_device_status = '0'
"""
        return query.format(
            table=self.table_name,
            clean_date=clean_date,
        )

    def query_get_stock_device(self, stock_device_id: int, device_name: str) -> str:
        query = """SELECT sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.at_clean_date
FROM stock_device sd
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
WHERE sd.stock_device_id = '{stock_device_id}' and d.device_name = '{device_name}'
"""
        return query.format(
            stock_device_id=str(stock_device_id), device_name=device_name
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
        raw_set_data: Dict[TableRow, RowValue],
        raw_where_data: Dict[TableRow, RowValue],
    ) -> str:
        query = "UPDATE {table_name} SET {set_data} WHERE {where_data}"
        return query.format(
            table_name=self.table_name,
            set_data=self.transform_data(raw_set_data),
            where_data=self.transform_data(raw_where_data),
        )

    def query_update_data_by_two_arg(
        self,
        raw_set_data: Dict[TableRow, RowValue],
        raw_where_data_one: Dict[TableRow, RowValue],
        raw_where_data_two: Dict[TableRow, RowValue],
    ) -> str:
        query = "UPDATE {table_name} SET {set_data} WHERE {one_data} and {two_data}"

        return query.format(
            table_name=self.table_name,
            set_data=self.transform_data(raw_set_data),
            one_data=self.transform_data(raw_where_data_one),
            two_data=self.transform_data(raw_where_data_two),
        )

    def query_get_data_by_value(
        self,
        where_data: Dict[TableRow, RowValue],
        rows: Dict[TableRow, RowValue] | None = None,
    ) -> str:
        query = "SELECT {rows} FROM {table_name} WHERE {where_data}"
        if rows:
            return query.format(
                rows=self.transform_data(rows),
                table_name=self.table_name,
                where_data=self.transform_data(where_data),
            )
        else:
            return query.format(
                rows=self.table_rows,
                table_name=self.table_name,
                where_data=self.transform_data(where_data),
            )
