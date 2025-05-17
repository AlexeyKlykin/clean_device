import logging
from typing import List

from src.database_interface import DataBaseInterface
from src.query_scheme import AbstractTableQueryScheme, QuerySchemeForStockDevice
from src.scheme_for_validation import (
    AbstractTable,
    DataForQuery,
    MessageInput,
    RowValue,
    StockBrokenDeviceData,
    TableRow,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class BotHandlerException(Exception):
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return f"BotHandlerException, {0}".format(self.message)


class DatabaseQueryHandler:
    def __init__(self, db_name: str, query_handler: AbstractTableQueryScheme) -> None:
        self.db_name = db_name
        self.query_handler = query_handler

    @staticmethod
    def transform_dict_from_data_query(
        data_from_bot: MessageInput,
    ) -> List[DataForQuery]:
        lst_data_for_query = []
        for key, val in data_from_bot.items():
            if isinstance(key, tuple):
                lst_data_for_query.append(
                    DataForQuery(
                        prefix=key[0],
                        table_row=TableRow(key[1]),
                        row_value=RowValue(val),
                    )
                )
            else:
                lst_data_for_query.append(
                    DataForQuery(table_row=TableRow(key), row_value=RowValue(val))
                )

        return lst_data_for_query

    def database_get_search_by_row(
        self, extra_where_data: MessageInput
    ) -> List[StockBrokenDeviceData] | None:
        if isinstance(self.query_handler, QuerySchemeForStockDevice):
            query = self.query_handler.query_get_search_with_device(
                where_data=self.transform_dict_from_data_query(extra_where_data)
            )

            with DataBaseInterface(db_name=self.db_name) as conn:
                cursor = conn.row_factory_for_connection(query[1])
                stock_devices = conn.get_all(query=query[0], cursor=cursor)

                if stock_devices and all(
                    isinstance(item, StockBrokenDeviceData) for item in stock_devices
                ):
                    return stock_devices

                else:
                    logging.warning(
                        f"Не найдено не одного прибора в ремонте за эту дату {extra_where_data}"
                    )

    def database_update_item(
        self, extra_set_data: MessageInput, extra_where_data: MessageInput
    ):
        """метод обновляющий данные в базе"""

        query = self.query_handler.query_update(
            set_data=self.transform_dict_from_data_query(data_from_bot=extra_set_data),
            where_data=self.transform_dict_from_data_query(
                data_from_bot=extra_where_data
            ),
        )

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            conn.update(query=query[0], cursor=cursor)

    def database_set_item(self, extra_set_data: tuple):
        query = self.query_handler.query_set()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            conn.set(
                query=query[0],
                set_data=extra_set_data,
                cursor=cursor,
            )

    def database_get_items(
        self,
        extra_where_data: MessageInput | None = None,
    ) -> List[AbstractTable] | None:
        if extra_where_data:
            query = self.query_handler.query_get(
                where_data=self.transform_dict_from_data_query(extra_where_data)
            )

        else:
            query = self.query_handler.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get_all(query=query[0], cursor=cursor)

    def database_get_item(
        self,
        extra_where_data: MessageInput | None = None,
    ) -> AbstractTable | None:
        if extra_where_data:
            query = self.query_handler.query_get(
                where_data=self.transform_dict_from_data_query(extra_where_data)
            )

        else:
            query = self.query_handler.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get(query=query[0], cursor=cursor)
