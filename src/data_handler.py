from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, TypeVar

from src.database_interface import DataBaseInterface
from src.query_scheme import AbstractTableQueryScheme
from src.scheme_for_validation import AbstractTable, DataForQuery, RowValue, TableRow


RowKey = TypeVar("RowKey", Tuple[str, str], str)


class AbstractApiBotHandler(ABC):
    @abstractmethod
    def database_get_items(
        self,
        extra_where_data: Dict[RowKey, str] | None = None,
    ) -> List[AbstractTable] | None: ...

    @abstractmethod
    def database_get_item(
        self,
        extra_where_data: Dict[RowKey, str] | None = None,
    ) -> AbstractTable | None: ...

    @abstractmethod
    def database_set_item(self, extra_set_data: tuple): ...

    @abstractmethod
    def database_update_item(
        self,
        extra_set_data: Dict[RowKey, str],
        extra_where_data: Dict[RowKey, str],
    ): ...


class ApiBotHandler(AbstractApiBotHandler):
    def __init__(
        self,
        db_name: str,
        query_handler: AbstractTableQueryScheme,
    ) -> None:
        self.db_name = db_name
        self.query_handler = query_handler

    @staticmethod
    def transform_dict_from_data_query(
        data_from_bot: Dict[RowKey, str],
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

    def database_update_item(self, extra_set_data, extra_where_data):
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

    def database_set_item(self, extra_set_data):
        query = self.query_handler.query_set()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            conn.set(
                query=query[0],
                set_data=extra_set_data,
                cursor=cursor,
            )

    def database_get_items(self, extra_where_data=None):
        if extra_where_data:
            query = self.query_handler.query_get(
                where_data=self.transform_dict_from_data_query(extra_where_data)
            )

        else:
            query = self.query_handler.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get_all(query=query[0], cursor=cursor)

    def database_get_item(self, extra_where_data=None):
        if extra_where_data:
            query = self.query_handler.query_get(
                where_data=self.transform_dict_from_data_query(extra_where_data)
            )

        else:
            query = self.query_handler.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get(query=query[0], cursor=cursor)

