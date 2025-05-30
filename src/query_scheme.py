from abc import abstractmethod
import logging
import json
import os
import sqlite3
from typing import Callable, Dict, List, Protocol, Tuple, Type, IO, Literal, TypeVar

from src.scheme_for_validation import (
    AbstractTable,
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    FabricRowFactory,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    StockBrokenDeviceData,
    StockDeviceData,
    StockDeviceTable,
    TableRow,
    DataForQuery,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

CREATE_TABLE_DEVICE_COMPANY = """CREATE TABLE IF NOT EXISTS device_company
    (company_id integer primary key AUTOINCREMENT,
    company_name text not null unique,
    producer_country text not null,
    description_company text)
"""

CREATE_TABLE_DEVICE_TYPE = """CREATE TABLE IF NOT EXISTS device_type
    (type_device_id integer primary key AUTOINCREMENT,
    type_title text not null unique,
    type_description text,
    lamp_type text default 'LED')
"""

CREATE_TABLE_DEVICE = """CREATE TABLE IF NOT EXISTS device
    (device_id integer primary key AUTOINCREMENT,
    device_name text not null,
    company_id integer not null,
    type_device_id integer not null,
    foreign key(company_id) references device_company(company_id),
    foreign key(type_device_id) references device_type(type_device_id))
"""

CREATE_TABLE_STOCK_DEVICE = """CREATE TABLE IF NOT EXISTS stock_device
    (stock_device_id integer not null,
    device_id integer not null,
    at_clean_date text not null,
    max_lamp_hours integer default 0,
    stock_device_status BOOLEAN DEFAULT 1,
    primary key (stock_device_id, device_id),
    foreign key(device_id) references device(device_id))
"""

type Mode = Literal["r", "rb", "w", "wb"]


class TempJS:
    def __init__(self, fp: str, mode: Mode):
        self.fp = fp
        self.mode: Mode = mode

    def __enter__(self) -> IO:
        self.file = open(self.fp, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.file:
                self.file.close()

        except Exception:
            raise Exception(exc_type, exc_val, exc_tb)


class ApiTempJS:
    def __init__(self, fp: str) -> None:
        self.fp = fp

    def write(self, data: Dict[str, str]):
        try:
            with TempJS(self.fp, "w") as js:
                json.dump(obj=data, fp=js)
        except IOError as err:
            raise err

    def read(self) -> Dict[str, str]:
        try:
            with TempJS(self.fp, "r") as js:
                data = json.load(js)
                return data

        except IOError as err:
            raise err

    def clean(self):
        if os.path.exists(self.fp):
            os.remove(self.fp)
        else:
            logger.warning(f"{self.fp} неверный путь к файлу")


class DBSqlite:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            return self.conn

        except ConnectionError as err:
            raise err

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                self.conn.close()

        except Exception:
            raise Exception(exc_type, exc_val, exc_tb)


class QueryException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.value = args[1]

        else:
            self.message = None
            self.value = None

    def __str__(self):
        logger.warning(QueryException)

        if self.message:
            return "QueryException, {0} {1}".format(self.message, self.value)

        else:
            return "QueryException вызвана для класса запросов"


class TableHandler:
    @classmethod
    def table_alias(cls, scheme: Type[AbstractTable]):
        """вспомогательный метод
        для преобразования названия строк таблицы для запроса"""

        return ", ".join(scheme.table_alias())

    @classmethod
    def transform_where_data(cls, data: DataForQuery | List[DataForQuery]) -> str:
        """метод для преобразования данных
        в строку условия поиска - row1=value1 and row2=value2"""

        if isinstance(data, DataForQuery):
            return data.build

        return " and ".join([item.build for item in data])

    @classmethod
    def gen_set_value(cls, scheme: Type[AbstractTable]):
        """метод для генерации строковых значений
        типа (?, ?, ?) в запросе"""

        return ", ".join("?" * len(scheme.table_rows()))

    @classmethod
    def transform_set_data(cls, data: DataForQuery | List[DataForQuery]) -> str:
        """метод преобразования данных в строку условия вставки данных типа
        row1=val1, row2=val2"""
        if isinstance(data, DataForQuery):
            return data.build

        return ", ".join([item.build for item in data])

    @classmethod
    def transform_rows(cls, lst_rows: List[TableRow]):
        return ", ".join(lst_rows)

    @classmethod
    def table_rows(cls, scheme: Type[AbstractTable]):
        return ", ".join(scheme.table_rows())

    @classmethod
    def request_row_factory(cls, scheme: Type[AbstractTable]):
        fabric = FabricRowFactory()
        fabric.choice_row_factory = scheme
        return fabric.choice_row_factory


class AbstractTableQueryScheme(Protocol):
    @abstractmethod
    def query_get(
        self,
        where_data: DataForQuery | List[DataForQuery] | None = None,
    ) -> Tuple[str, Callable]:
        """строковый запрос для получения данных из таблицы"""

    @abstractmethod
    def query_set(self) -> Tuple[str, Callable]:
        """строковый запрос для вставки данных в таблицу"""

    @abstractmethod
    def query_update(
        self,
        where_data: DataForQuery | List[DataForQuery],
        set_data: DataForQuery | List[DataForQuery],
    ) -> Tuple[str, Callable]:
        """строковый запрос для обновления данных в таблице"""


TableScheme = TypeVar("TableScheme", bound=AbstractTableQueryScheme, contravariant=True)


class QuerySchemeForStockDevice:
    """Класс формирования запросов для таблицы приборов на складе"""

    def query_get_search_with_device(self, where_data) -> Tuple[str, Callable]:
        """строковый запрос для получения данных о приборах со статусом"""
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
WHERE {where_data}"""
        return query.format(
            rows=TableHandler.table_alias(StockBrokenDeviceData),
            table=StockBrokenDeviceData.table_name(),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(StockBrokenDeviceData)

    def query_get_search_with_device_company(self, where_data) -> Tuple[str, Callable]:
        """строковый запрос для получения данных о приборах со статусом"""
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_company dc ON dc.company_id = d.company_id
WHERE {where_data}"""
        return query.format(
            rows=TableHandler.table_alias(StockBrokenDeviceData),
            table=StockBrokenDeviceData.table_name(),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(StockBrokenDeviceData)

    def query_get_search_with_device_type(self, where_data) -> Tuple[str, Callable]:
        """строковый запрос для получения данных о приборах со статусом"""
        query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
WHERE {where_data}"""
        return query.format(
            rows=TableHandler.table_alias(StockBrokenDeviceData),
            table=StockBrokenDeviceData.table_name(),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(StockBrokenDeviceData)

    def query_get(self, where_data=None) -> Tuple[str, Callable]:
        if where_data:
            query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
WHERE {where_data}
"""
            return query.format(
                rows=TableHandler.table_alias(StockDeviceData),
                table=StockDeviceData.table_name(),
                where_data=TableHandler.transform_where_data(where_data),
            ), TableHandler.request_row_factory(StockDeviceData)

        else:
            query = """SELECT {rows}
FROM {table}
LEFT JOIN device d ON d.device_id = sd.device_id
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
"""
            return query.format(
                rows=TableHandler.table_alias(StockDeviceData),
                table=StockDeviceData.table_name(),
            ), TableHandler.request_row_factory(StockDeviceData)

    def query_set(self) -> Tuple[str, Callable]:
        query = "INSERT OR IGNORE INTO {table} ({rows}) VALUES ({set_values})"
        return query.format(
            table=StockDeviceTable.table_name(),
            rows=TableHandler.table_rows(StockDeviceTable),
            set_values=TableHandler.gen_set_value(StockDeviceTable),
        ), TableHandler.request_row_factory(StockDeviceTable)

    def query_update(self, where_data, set_data) -> Tuple[str, Callable]:
        query = "UPDATE {table} SET {set_data} WHERE {where_data}"
        return query.format(
            table=StockDeviceTable.table_name(),
            set_data=TableHandler.transform_set_data(set_data),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(StockDeviceTable)


class QuerySchemeForDevice:
    """Класс формирования запросов для таблицы приборов"""

    def query_get(self, where_data=None) -> Tuple[str, Callable]:
        if where_data:
            query = """SELECT {rows}
FROM {table}
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
WHERE {where_data}
"""
            return query.format(
                rows=TableHandler.table_alias(OutputDeviceTable),
                table=OutputDeviceTable.table_name(),
                where_data=TableHandler.transform_where_data(where_data),
            ), TableHandler.request_row_factory(OutputDeviceTable)

        else:
            query = """SELECT {rows}
FROM {table}
LEFT JOIN device_company dc ON dc.company_id = d.company_id
LEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id
"""
            return query.format(
                rows=TableHandler.table_rows(OutputDeviceTable),
                table=DeviceTable.table_name(),
            ), TableHandler.request_row_factory(OutputDeviceTable)

    def query_set(self) -> Tuple[str, Callable]:
        query = "INSERT INTO {table} ({rows}) VALUES ({set_values})"
        return query.format(
            table=DeviceTable.table_name(),
            rows=TableHandler.table_rows(DeviceTable),
            set_values=TableHandler.gen_set_value(DeviceTable),
        ), TableHandler.request_row_factory(DeviceTable)

    def query_update(self, where_data, set_data) -> Tuple[str, Callable]:
        query = "UPDATE {table} SET {set_data} WHERE {where_data}"
        return query.format(
            table=DeviceTable.table_name(),
            set_data=TableHandler.transform_set_data(set_data),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(DeviceTable)


class QuerySchemeForDeviceCompany:
    """Класс формирования запросов для таблицы компании производителя приборов"""

    def query_get(self, where_data=None) -> Tuple[str, Callable]:
        if where_data:
            query = """SELECT {rows} 
FROM {table}
WHERE {where_data}
"""
            return query.format(
                rows=TableHandler.table_rows(OutputDeviceCompanyTable),
                table=OutputDeviceCompanyTable.table_name(),
                where_data=TableHandler.transform_where_data(where_data),
            ), TableHandler.request_row_factory(OutputDeviceCompanyTable)

        else:
            query = "SELECT {rows} FROM {table}"
            return query.format(
                rows=TableHandler.table_rows(OutputDeviceCompanyTable),
                table=OutputDeviceCompanyTable.table_name(),
            ), TableHandler.request_row_factory(OutputDeviceCompanyTable)

    def query_set(self):
        query = "INSERT INTO {table} ({rows}) VALUES ({set_values})"
        return query.format(
            table=DeviceCompanyTable.table_name(),
            rows=TableHandler.table_rows(DeviceCompanyTable),
            set_values=TableHandler.gen_set_value(DeviceCompanyTable),
        ), TableHandler.request_row_factory(DeviceCompanyTable)

    def query_update(self, where_data, set_data) -> Tuple[str, Callable]:
        query = "UPDATE {table} SET {set_data} WHERE {where_data}"
        return query.format(
            table=DeviceCompanyTable.table_name(),
            set_data=TableHandler.transform_set_data(set_data),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(DeviceCompanyTable)


class QuerySchemeForDeviceType:
    """Класс формирования запросов для таблицы типов приборов"""

    def query_get(self, where_data=None) -> Tuple[str, Callable]:
        if where_data:
            query = """SELECT {rows} 
FROM {table}
WHERE {where_data}
"""
            return query.format(
                rows=TableHandler.table_rows(OutputDeviceTypeTable),
                table=OutputDeviceTypeTable.table_name(),
                where_data=TableHandler.transform_where_data(where_data),
            ), TableHandler.request_row_factory(OutputDeviceTypeTable)

        else:
            query = "SELECT {rows} FROM {table}"
            return query.format(
                rows=TableHandler.table_rows(OutputDeviceTypeTable),
                table=DeviceTypeTable.table_name(),
            ), TableHandler.request_row_factory(OutputDeviceTypeTable)

    def query_set(self) -> Tuple[str, Callable]:
        query = "INSERT INTO {table} ({rows}) VALUES ({set_values})"
        return query.format(
            table=DeviceTypeTable.table_name(),
            rows=TableHandler.table_rows(DeviceTypeTable),
            set_values=TableHandler.gen_set_value(DeviceTypeTable),
        ), TableHandler.request_row_factory(DeviceTypeTable)

    def query_update(self, where_data, set_data) -> Tuple[str, Callable]:
        query = "UPDATE {table} SET {set_data} WHERE {where_data}"
        return query.format(
            table=DeviceTypeTable.table_name(),
            set_data=TableHandler.transform_set_data(set_data),
            where_data=TableHandler.transform_where_data(where_data),
        ), TableHandler.request_row_factory(DeviceTypeTable)
