from src.db_app import DBSqlite


def test_work_connect_db_sqlite():
    """тест: работы DBSqlite"""

    sql_query_select = "SELECT name FROM sqlite_master WHERE type='table'"

    with DBSqlite("clean_device_test.db") as conn:
        conn.execute(sql_query_select)
        cursor = conn.cursor()
        cursor.execute(sql_query_select)
        res = cursor.fetchall()

        assert res == [
            ("stock_device",),
            ("device",),
            ("sqlite_sequence",),
            ("device_company",),
            ("device_type",),
        ]
