import sqlite3
import logging
from abc import ABC, abstractmethod
from typing import Annotated, Dict, List, Tuple

from pydantic import BaseModel, ConfigDict, Field

from src.utils import modificate_date_to_str

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class DeviceCompany(BaseModel):
    model_config = ConfigDict(strict=True)

    company_name: Annotated[str, Field(min_length=4, description="Название компании")]
    producer_country: Annotated[
        str, Field(min_length=4, description="Страна производителя")
    ]
    description_company: Annotated[
        str, Field(min_length=6, description="Описание компании")
    ]


class DeviceType(BaseModel):
    model_config = ConfigDict(strict=True)

    type_title: Annotated[str, Field(min_length=4, description="Название типа прибора")]
    description_type: Annotated[
        str, Field(min_length=4, description="Описание типа прибора")
    ]


class DeviceInput(BaseModel):
    model_config = ConfigDict(strict=True)

    device_name: Annotated[str, Field(min_length=2, description="Название прибора")]
    company_id: Annotated[int, Field(gt=0, description="Идентификатор компании")]
    type_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор типа прибора")
    ]


class DeviceOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    device_name: Annotated[str, Field(min_length=2, description="Название прибора")]
    company_name: Annotated[str, Field(min_length=4, description="Название компании")]
    type_title: Annotated[str, Field(min_length=4, description="Тип прибора")]


class StockDevicesInput(BaseModel):
    model_config = ConfigDict(strict=True)

    stock_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор прибора на складе")
    ]
    device_id: Annotated[int, Field(gt=0, description="Идентификатор связи с прибором")]
    at_clean_date: str


class StockDevicesOutput(BaseModel):
    model_config = ConfigDict(strict=True)

    stock_device_id: Annotated[
        int, Field(gt=0, description="Идентификатор прибора на складе")
    ]
    device_name: Annotated[str, Field(min_length=2, description="Название прибора")]
    company_name: Annotated[str, Field(min_length=4, description="Название компании")]
    type_title: Annotated[str, Field(min_length=4, description="Название типа прибора")]
    at_clean_date: str


def company_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceCompany(**data)


def device_type_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceType(**data)


def device_input_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceInput(**data)


def device_output_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return DeviceOutput(**data)


def stock_device_input_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return StockDevicesInput(**data)


def stock_device_output_factory(cursor, row):
    data = {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return StockDevicesOutput(**data)


class AbstractInterface(ABC):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    @abstractmethod
    def insert(self, item: Dict[str, str]) -> bool:
        """метод для добавления данных в бд"""

    @abstractmethod
    def check_by_title(self, title: str) -> bool:
        """метод проверки наличия данных по названию"""

    @abstractmethod
    def deleting_record_by_title(self, title: str):
        """метод удаления данных по названию"""

    @abstractmethod
    def get(
        self, item: int
    ) -> StockDevicesOutput | DeviceOutput | DeviceType | DeviceCompany:
        """метод получения данных по id"""


class StockDevicesInterface(AbstractInterface):
    """Класс интерфейс для работы с данными таблицы приборов на складе"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.conn.row_factory = stock_device_input_factory
        self.table = "stock_device"

    # проверить тестами
    def get_all_stock_devices(self) -> List[int]:
        """метод получения всех названий приборов"""

        sql_query = "SELECT stock_device_id FROM {table}"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table))
            result = cursor.fetchall()
            return result

        except sqlite3.Error as err:
            raise err

    def get(self, item: int) -> StockDevicesOutput:
        sql_query = """select sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.at_clean_date
from {table} sd
left join device d on d.device_id = sd.device_id
left join device_company dc on dc.company_id = d.company_id
left join device_type dt on dt.type_device_id = d.type_device_id
where sd.stock_device_id = '{stock_device_id}'"""
        self.conn.row_factory = stock_device_output_factory
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, stock_device_id=item))
            res = cursor.fetchone()
            return res

        except sqlite3.Error as err:
            raise err

    def insert(self, item: Dict[str, str]) -> bool:
        sql_query = "INSERT INTO {table}(stock_device_id, device_id, at_clean_date) VALUES (?, ?, ?)"
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                sql_query.format(table=self.table),
                (
                    int(item["stock_device_id"]),
                    int(item["device_id"]),
                    item["at_clean_date"],
                ),
            )
            return True

        except sqlite3.IntegrityError:
            logger.warning(
                f"Нельзя повторно добавлять {item} одни и теже данные в таблицу"
            )
            return False

        except ValueError:
            logger.warning(
                f"Данные {item['company_id']} или {item['type_device_id']} не могут быть переведены в int"
            )
            return False

    # ждет проверки тестами
    def update_device_date(self, device_id: int):
        """метод обновления существующего прибора"""

        sql_query = """UPDATE TABLE {table} 
SET at_clean_date = {clean_date}
WHERE stock_device_id = {device_id}"""
        self.conn.row_factory = stock_device_input_factory
        cursor = self.conn.cursor()
        clean_data = modificate_date_to_str()

        try:
            cursor.execute(
                sql_query.format(
                    table=self.table, clean_data=clean_data, device_id=device_id
                )
            )

        except sqlite3.Error as err:
            raise err

    # ждет проверки тестами
    def check_device_by_id(self, device_id: int) -> bool:
        """метод проверки наличия прибора по id"""

        sql_query = """SELECT stock_device_id 
FROM {table} sd 
WHERE sd.stock_device_id = '{device_id}'"""
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_id=device_id))
            result = cursor.fetchone()

            if result:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def check_by_title(self, title: str) -> bool:
        sql_query = """SELECT stock_device_id, device_id, at_clean_date 
FROM {table} sd 
left join device d on d.device_id = sd.device_id 
WHERE d.device_name = '{device_name}'"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_name=title))
            result = cursor.fetchone()

            if result:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def deleting_record_by_title(self, title: str):
        sql_query = "DELETE FROM {table} WHERE stock_device_id = '{stock_device_id}'"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                sql_query.format(table=self.table, stock_device_id=int(title))
            )

        except sqlite3.Error as err:
            raise err


class DeviceInterface(AbstractInterface):
    """Класс интерфейс для работы с данными таблицы приборов"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.conn.row_factory = device_input_factory
        self.table = "device"

    # проверить тестами
    def get_all_devices(self) -> List[Tuple[str, int]]:
        """метод получения всех названий приборов"""

        sql_query = "SELECT device_id, device_name FROM {table}"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table))
            result = cursor.fetchall()
            return result

        except sqlite3.Error as err:
            raise err

    def get(self, item: int) -> DeviceOutput:
        sql_query = """SELECT d.device_name, dc.company_name, dt.type_title 
FROM {table} d 
left join device_company dc on dc.company_id = d.company_id 
left join device_type dt on dt.type_device_id = d.type_device_id
where d.device_id = '{device_id}'
"""
        self.conn.row_factory = device_output_factory
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_id=item))
            res = cursor.fetchone()
            return res

        except sqlite3.Error as err:
            raise err

    def get_id_by_name(self, device_name: str) -> int:
        """метод получения id по имени"""

        sql_query = """SELECT device_id 
FROM {table} 
WHERE device_name = '{device_name}'
"""
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_name=device_name))
            res = cursor.fetchone()
            return res[0]

        except sqlite3.Error as err:
            raise err

    def insert(self, item: Dict[str, str]) -> bool:
        sql_query = "INSERT INTO {table}(device_name, company_id, type_device_id) VALUES (?, ?, ?)"
        self.conn.row_factory = device_input_factory
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                sql_query.format(table=self.table),
                (
                    item["device_name"],
                    int(item["company_id"]),
                    int(item["type_device_id"]),
                ),
            )
            return True

        except sqlite3.IntegrityError:
            logger.warning(
                f"Нельзя повторно добавлять {item} одни и теже данные в таблицу"
            )
            return False

        except ValueError:
            logger.warning(
                f"Данные {item['company_id']} или {item['type_device_id']} не могут быть переведены в int"
            )
            return False

    def check_by_title(self, title: str) -> bool:
        sql_query = """SELECT device_name, company_id, type_device_id 
FROM {table} 
WHERE device_name = '{device_name}'
"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_name=title))
            result = cursor.fetchone()

            if result:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def deleting_record_by_title(self, title: str):
        sql_query = "DELETE FROM {table} WHERE device_name = '{device_name}'"
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, device_name=title))

        except sqlite3.Error as err:
            raise err


class DeviceTypeInterface(AbstractInterface):
    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.conn.row_factory = device_type_factory
        self.table = "device_type"

    # проверить тестами
    def get_all_type(self) -> List[str]:
        """метод получения всех названий приборов"""

        sql_query = "SELECT type_title FROM {table}"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table))
            result = cursor.fetchall()
            return result

        except sqlite3.Error as err:
            raise err

    def get(self, item: int) -> DeviceType:
        sql_query = """SELECT dt.type_title, dt.description_type 
FROM {table} dt
where dt.type_device_id = '{type_id}'
"""
        self.conn.row_factory = device_type_factory
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, type_id=item))
            res = cursor.fetchone()
            return res

        except sqlite3.Error as err:
            raise err

    def check_by_id(self, type_id: int) -> bool:
        """метод проверки наличия данных по id"""

        sql_query = (
            "SELECT type_title FROM {table} WHERE type_device_id = '{type_device}'"
        )
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, type_device=type_id))
            res = cursor.fetchone()

            if res:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def insert(self, item: Dict[str, str]) -> bool:
        sql_query = "INSERT INTO {table}(type_title, description_type) VALUES (?, ?)"
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                sql_query.format(table=self.table), [item for item in item.values()]
            )
            return True

        except sqlite3.IntegrityError:
            logger.warning("Нельзя повторно добавлять одни и теже данные в таблицу")
            return False

    def check_by_title(self, title: str) -> bool:
        sql_query = """SELECT type_title, description_type 
FROM {table} 
WHERE type_title = '{type_title}'
"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, type_title=title))
            result = cursor.fetchone()

            if result:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def deleting_record_by_title(self, title: str):
        sql_query = "DELETE FROM {table} WHERE type_title = '{type_title}'"
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, type_title=title))

        except sqlite3.Error as err:
            raise err


class DeviceCompanyInterface(AbstractInterface):
    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__(conn)
        self.conn.row_factory = company_factory
        self.table = "device_company"

    # проверить тестами
    def get_id_by_name(self, company_name: str) -> int:
        """метод возвращает id компании производителя по имени"""

        sql_query = "SELECT company_id FROM {table} WHERE company_name = {company_name}"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                sql_query.format(table=self.table, company_name=company_name)
            )
            result = cursor.fetchone()
            return result

        except sqlite3.Error as err:
            raise err

    # проверить тестами
    def get_all_company(self) -> List[str]:
        """метод получения всех названий приборов"""

        sql_query = "SELECT company_name FROM {table}"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table))
            result = cursor.fetchall()
            return result

        except sqlite3.Error as err:
            raise err

    def get(self, item: int) -> DeviceCompany:
        sql_query = """SELECT dc.company_name, dc.producer_country, dc.description_company 
FROM {table} dc
where dc.company_id = '{company_id}'
"""
        self.conn.row_factory = company_factory
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, company_id=item))
            res = cursor.fetchone()
            return res

        except sqlite3.Error as err:
            raise err

    def check_by_id(self, company_id: int) -> bool:
        """метод проверки наличия данных по id компании"""
        sql_query = "SELECT company_name FROM {table} WHERE company_id = '{company_id}'"
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, company_id=company_id))
            res = cursor.fetchone()

            if res:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def insert(self, item: Dict[str, str]) -> bool:
        sql_query = """INSERT INTO {table}
(company_name, producer_country, description_company) 
VALUES (?, ?, ?)"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                sql_query.format(table=self.table), [item for item in item.values()]
            )
            return True

        except sqlite3.IntegrityError:
            logger.warning("Нельзя повторно добавлять одни и теже данные в таблицу")
            return False

    def check_by_title(self, title: str) -> bool:
        sql_query = """SELECT company_name, producer_country, description_company 
FROM {table} 
WHERE company_name = '{company_name}'
"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, company_name=title))
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False

        except sqlite3.Error as err:
            raise err

    def deleting_record_by_title(self, title: str):
        sql_query = "DELETE FROM {table} WHERE company_name = '{company_name}'"
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_query.format(table=self.table, company_name=title))

        except sqlite3.Error as err:
            raise err
