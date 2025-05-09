"""
Модуль служит для валидации схемы работы с данными
"""

import inspect
from typing import Annotated, Callable, List, NewType, Type, TypeVar
from pydantic import BaseModel, ConfigDict, Field


class SchemaForValidationException(Exception):
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return "SchemaForValidationException, {0}".format(self.message)


class AbstractTable(BaseModel):
    model_config = ConfigDict(strict=True, validate_by_name=True)

    @classmethod
    def class_mro(cls):
        return inspect.getmro(cls)[0]

    @classmethod
    def table_rows(cls) -> List[str]:
        return [item for item in inspect.get_annotations(cls).keys()]

    @classmethod
    def table_alias(cls) -> List[str]:
        meta_lst = [item for item in inspect.get_annotations(cls).values()]
        alias_lst = [
            item.__dict__["__metadata__"][0].alias
            for item in meta_lst
            if item.__dict__["__metadata__"][0].alias
        ]
        return alias_lst

    @staticmethod
    def table_name() -> str:
        return "stock_device as sd"

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__


Table = TypeVar("Table", covariant=True, bound=AbstractTable)


class StockDeviceTable(AbstractTable):
    stock_device_id: Annotated[
        int,
        Field(
            gt=0,
            description="Идентификатор прибора на складе",
            alias="sd.stock_device_id",
        ),
    ]
    device_id: Annotated[
        int,
        Field(gt=0, description="Идентификатор связи с прибором", alias="sd.device_id"),
    ]
    at_clean_date: Annotated[str, Field(min_length=7, alias="sd.at_clean_date")]

    @staticmethod
    def table_name() -> str:
        return "stock_device as sd"


class StockDeviceTableStatus(AbstractTable):
    stock_device_id: Annotated[
        int,
        Field(
            gt=0,
            description="Идентификатор прибора на складе",
            alias="sd.stock_device_id",
        ),
    ]
    device_id: Annotated[
        int,
        Field(gt=0, description="Идентификатор связи с прибором", alias="sd.device_id"),
    ]
    at_clean_date: Annotated[str, Field(min_length=7, alias="sd.at_clean_date")]
    stock_device_status: Annotated[bool, Field(alias="sd.stock_device_status")]

    @staticmethod
    def table_name() -> str:
        return "stock_device as sd"


class StockBrokenDeviceData(AbstractTable):
    stock_device_id: Annotated[int, Field(gt=0, alias="sd.stock_device_id")]
    device_name: Annotated[str, Field(min_length=3, alias="d.device_name")]
    at_clean_date: Annotated[str, Field(min_length=7, alias="sd.at_clean_date")]

    @staticmethod
    def table_name() -> str:
        return "stock_device as sd"


class StockDeviceData(AbstractTable):
    stock_device_id: Annotated[int, Field(gt=0, alias="sd.stock_device_id")]
    device_name: Annotated[str, Field(min_length=3, alias="d.device_name")]
    company_name: Annotated[str, Field(min_length=3, alias="dc.company_name")]
    type_title: Annotated[str, Field(min_length=3, alias="dt.type_title")]
    at_clean_date: Annotated[str, Field(min_length=7, alias="sd.at_clean_date")]

    @staticmethod
    def table_name() -> str:
        return "stock_device as sd"


class OutputDeviceTypeTable(AbstractTable):
    type_device_id: Annotated[
        int,
        Field(
            gt=0, description="Идентификатор типа прибора", alias="dt.type_device_id"
        ),
    ]
    type_title: Annotated[
        str,
        Field(min_length=3, description="Название типа прибора", alias="dt.type_title"),
    ]
    type_description: Annotated[
        str,
        Field(
            min_length=4,
            description="Описание типа прибора",
            alias="dt.type_description",
        ),
    ]

    @staticmethod
    def table_name() -> str:
        return "device_type as dt"


class DeviceTypeTable(AbstractTable):
    type_title: Annotated[
        str,
        Field(min_length=3, description="Название типа прибора", alias="dt.type_title"),
    ]
    type_description: Annotated[
        str,
        Field(
            min_length=4,
            description="Описание типа прибора",
            alias="dt.type_description",
        ),
    ]

    @staticmethod
    def table_name() -> str:
        return "device_type as dt"


class OutputDeviceCompanyTable(AbstractTable):
    company_id: Annotated[
        int, Field(gt=0, description="Идентификатор компании", alias="dc.company_id")
    ]
    company_name: Annotated[
        str,
        Field(min_length=4, description="Название компании", alias="dc.company_name"),
    ]
    producer_country: Annotated[
        str,
        Field(
            min_length=4,
            description="Страна производителя",
            alias="dc.producer_country",
        ),
    ]
    description_company: Annotated[
        str,
        Field(
            min_length=6,
            description="Описание компании",
            alias="dc.description_company",
        ),
    ]

    @staticmethod
    def table_name() -> str:
        return "device_company as dc"


class DeviceCompanyTable(AbstractTable):
    company_name: Annotated[
        str,
        Field(min_length=4, description="Название компании", alias="dc.company_name"),
    ]
    producer_country: Annotated[
        str,
        Field(
            min_length=4,
            description="Страна производителя",
            alias="dc.producer_country",
        ),
    ]
    description_company: Annotated[
        str,
        Field(
            min_length=6,
            description="Описание компании",
            alias="dc.description_company",
        ),
    ]

    @staticmethod
    def table_name() -> str:
        return "device_company as dc"


class OutputDeviceTable(AbstractTable):
    device_id: Annotated[
        int, Field(gt=0, description="Идентификатор прибора", alias="d.device_id")
    ]
    device_name: Annotated[
        str, Field(min_length=2, description="Название прибора", alias="d.device_name")
    ]
    company_name: Annotated[
        str,
        Field(
            min_length=2, description="Идентификатор компании", alias="dc.company_name"
        ),
    ]
    type_title: Annotated[
        str,
        Field(
            min_length=2,
            description="Идентификатор типа прибора",
            alias="dt.type_title",
        ),
    ]

    @staticmethod
    def table_name() -> str:
        return "device as d"


class DeviceTable(AbstractTable):
    device_name: Annotated[
        str, Field(min_length=2, description="Название прибора", alias="d.device_name")
    ]
    company_id: Annotated[
        int, Field(gt=0, description="Идентификатор компании", alias="d.company_id")
    ]
    type_device_id: Annotated[
        int,
        Field(gt=0, description="Идентификатор типа прибора", alias="d.type_device_id"),
    ]

    @staticmethod
    def table_name() -> str:
        return "device as d"


TableRow = NewType("TableRow", str)
RowValue = NewType("RowValue", str)


# фабрики
class FabricRowFactory:
    def __init__(self):
        self.schema_validate = None

    @property
    def choice_row_factory(self) -> Callable:
        if self.schema_validate:
            match self.schema_validate.class_name():
                case "StockBrokenDeviceData":
                    return self.output_broken_device_factory

                case "OutputDeviceTypeTable":
                    return self.output_device_type_factory

                case "DeviceTypeTable":
                    return self.device_type_factory

                case "OutputDeviceCompanyTable":
                    return self.output_company_factory

                case "DeviceCompanyTable":
                    return self.company_factory

                case "OutputDeviceTable":
                    return self.output_device_factory

                case "DeviceTable":
                    return self.device_factory

                case "StockDeviceTable":
                    return self.stock_device_factory

                case "StockDeviceData":
                    return self.repr_stock_device_factory

                case "StockDeviceTableStatus":
                    return self.stock_device_status_factory

                case _:
                    raise ValueError(f"{self.schema_validate} нет соответствий")
        else:
            raise SchemaForValidationException("Не передана схема")

    @choice_row_factory.setter
    def choice_row_factory(self, schema: Type[AbstractTable]):
        self.schema_validate = schema

    @staticmethod
    def output_broken_device_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return StockBrokenDeviceData(**data)

    @staticmethod
    def output_device_type_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return OutputDeviceTypeTable(**data)

    @staticmethod
    def device_type_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return DeviceTypeTable(**data)

    @staticmethod
    def output_company_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return OutputDeviceCompanyTable(**data)

    @staticmethod
    def company_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return DeviceCompanyTable(**data)

    @staticmethod
    def output_device_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return OutputDeviceTable(**data)

    @staticmethod
    def device_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return DeviceTable(**data)

    @staticmethod
    def stock_device_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return StockDeviceTable(**data)

    @staticmethod
    def repr_stock_device_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return StockDeviceData(**data)

    @staticmethod
    def stock_device_status_factory(cursor, row):
        data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return StockDeviceTableStatus(**data)
