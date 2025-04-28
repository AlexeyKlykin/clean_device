import sqlite3
import logging
from abc import ABC, abstractmethod
from typing import (
    Annotated,
    Callable,
    Dict,
    Generator,
    List,
    NewType,
    Tuple,
)
from pydantic import BaseModel, ConfigDict, Field

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


## Валидация
# валидация таблицы
class AbstractTable(BaseModel):
    model_config = ConfigDict(strict=True)

    @classmethod
    def table_rows(cls) -> List[str]:
        return list(cls.__dict__["__annotations__"].keys())

    @staticmethod
    def table_name() -> str:
        return "stock_device"


class StockDeviceData(AbstractTable):
    stock_device_id: Annotated[int, Field(gt=0)]
    device_name: Annotated[str, Field(min_length=3)]
    company_name: Annotated[str, Field(min_length=3)]
    type_title: Annotated[str, Field(min_length=3)]
    at_clean_date: str


class OutputDeviceTypeTable(AbstractTable):
    type_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор типа прибора")
    ]
    type_title: Annotated[str, Field(min_length=3, description="Название типа прибора")]
    type_description: Annotated[
        str, Field(min_length=4, description="Описание типа прибора")
    ]

    @staticmethod
    def table_name() -> str:
        return "device_type"


class DeviceTypeTable(AbstractTable):
    type_title: Annotated[str, Field(min_length=3, description="Название типа прибора")]
    type_description: Annotated[
        str, Field(min_length=4, description="Описание типа прибора")
    ]

    @staticmethod
    def table_name() -> str:
        return "device_type"


class OutputDeviceCompanyTable(AbstractTable):
    company_id: Annotated[int, Field(gt=0, description="Идентификатор компании")]
    company_name: Annotated[str, Field(min_length=4, description="Название компании")]
    producer_country: Annotated[
        str, Field(min_length=4, description="Страна производителя")
    ]
    description_company: Annotated[
        str, Field(min_length=6, description="Описание компании")
    ]

    @staticmethod
    def table_name() -> str:
        return "device_company"


class DeviceCompanyTable(AbstractTable):
    company_name: Annotated[str, Field(min_length=4, description="Название компании")]
    producer_country: Annotated[
        str, Field(min_length=4, description="Страна производителя")
    ]
    description_company: Annotated[
        str, Field(min_length=6, description="Описание компании")
    ]

    @staticmethod
    def table_name() -> str:
        return "device_company"


class OutputDeviceTable(AbstractTable):
    device_id: Annotated[int, Field(gt=0, description="Идентификатор прибора")]
    device_name: Annotated[str, Field(min_length=2, description="Название прибора")]
    company_id: Annotated[int, Field(gt=0, description="Идентификатор компании")]
    type_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор типа прибора")
    ]

    @staticmethod
    def table_name() -> str:
        return "device"


class DeviceTable(AbstractTable):
    device_name: Annotated[str, Field(min_length=2, description="Название прибора")]
    company_id: Annotated[int, Field(gt=0, description="Идентификатор компании")]
    type_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор типа прибора")
    ]

    @staticmethod
    def table_name() -> str:
        return "device"


class StockDeviceTable(AbstractTable):
    stock_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор прибора на складе")
    ]
    device_id: Annotated[int, Field(gt=0, description="Идентификатор связи с прибором")]
    at_clean_date: str

    @staticmethod
    def table_name() -> str:
        return "stock_device"


TableRow = NewType("TableRow", str)
RowValue = NewType("RowValue", str)


# фабрики
def output_device_type_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return OutputDeviceTypeTable(**data)


def device_type_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceTypeTable(**data)


def output_company_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return OutputDeviceCompanyTable(**data)


def company_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceCompanyTable(**data)


def output_device_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return OutputDeviceTable(**data)


def device_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceTable(**data)


def stock_device_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return StockDeviceTable(**data)


def repr_stock_device_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return StockDeviceData(**data)


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


## Работа с данными(бизнес логика)
class AbstractInterfaceConnectDB(ABC):
    @abstractmethod
    def get_all_data(self) -> Generator[List[AbstractTable]]: ...

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

            while True:
                res = cursor.fetchmany(5)
                if res:
                    yield res

                else:
                    cursor.close()
                    break

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
