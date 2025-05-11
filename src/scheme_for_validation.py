"""
Модуль служит для валидации схемы работы с данными
"""

import inspect
from typing import Annotated, Callable, List, Literal, NewType, Type
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


type Lamp = Literal["LED", "FIL"]
type Status = Literal["0", "1"]


class SchemeForValidationException(Exception):
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return "SchemeForValidationException, {0}".format(self.message)


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
    max_lamp_hours: Annotated[
        int,
        Field(
            lt=6000,
            ge=0,
            description="Количество часов работы лампы",
            alias="sd.max_lamp_hours",
        ),
    ] = 0
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
    stock_device_status: Annotated[Status, Field(alias="sd.stock_device_status")]
    max_lamp_hours: Annotated[
        int,
        Field(
            lt=6000,
            ge=0,
            description="Количество часов работы лампы",
            alias="sd.max_lamp_hours",
        ),
    ] = 0
    at_clean_date: Annotated[str, Field(min_length=7, alias="sd.at_clean_date")]

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
    max_lamp_hours: Annotated[
        int,
        Field(
            lt=6000,
            ge=0,
            description="Количество часов работы лампы",
            alias="sd.max_lamp_hours",
        ),
    ] = 0
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
    lamp_type: Annotated[
        Lamp,
        Field(
            description="Тип лампы с выбором из двух возможных вариантов",
            alias="dt.lamp_type",
        ),
    ] = "LED"

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
    lamp_type: Annotated[
        Lamp,
        Field(
            description="Тип лампы с выбором из двух возможных вариантов",
            alias="dt.lamp_type",
        ),
    ] = "LED"

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


class DataForQuery(BaseModel):
    """
    Данные переданные в запросе в место после WHERE
    # where_data = {TableRow("sd.at_clean_date"): RowValue("30-4-2025")}
                    ||
    # where_data = WhereDataForQuery(table_row="at_clean_date", row_value="30-4-2025")
    # where_data.model_dump() - # {TableRow("sd.at_clean_date"): RowValue("30-4-2025")}
    """

    prefix: Annotated[
        str | None,
        Field(
            max_length=3,
            description="Префикс применяемый для сокращения имени таблицы перед именем столбца",
        ),
    ] = None
    table_row: Annotated[TableRow, Field(min_length=4, description="Называние колонки")]
    row_value: Annotated[
        RowValue, Field(min_length=1, description="Данные для колонки")
    ]

    @model_validator(mode="after")
    def table_row_prefix(self):
        if self.prefix:
            self.table_row = TableRow(f"{self.prefix}.{self.table_row}")

        return self

    @computed_field
    @property
    def build(self) -> str:
        return f"{self.table_row}='{self.row_value}'"


# фабрики
class FabricRowFactory:
    def __init__(self):
        self.scheme_validate = None

    @property
    def choice_row_factory(self) -> Callable:
        if self.scheme_validate:
            match self.scheme_validate.class_name():
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
                    raise ValueError(f"{self.scheme_validate} нет соответствий")
        else:
            raise SchemeForValidationException("Не передана схема")

    @choice_row_factory.setter
    def choice_row_factory(self, scheme: Type[AbstractTable]):
        self.scheme_validate = scheme

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
