from typing import Annotated, List, NewType
from pydantic import BaseModel, ConfigDict, Field


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


class StockBrockenDeviceData(AbstractTable):
    stock_device_id: Annotated[int, Field(gt=0)]
    device_name: Annotated[str, Field(min_length=3)]
    at_clean_date: str


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
def output_brocket_device_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return StockBrockenDeviceData(**data)


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
