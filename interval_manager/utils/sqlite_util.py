"""Utility module containing sqlite3 related functions"""
from typing import Tuple, Union

import sqlite3

DATABASE_LINK = "intervals.db"


def query_time_from_uuid(interval_id: str) -> Tuple[int, int, int, str]:
    """Queries start/end/remain time with provided interval_id,
    returns (start_time, end_time, remain_time, webhook_url) tuple
    """
    con = sqlite3.connect(DATABASE_LINK)
    cur = con.cursor()

    cur.execute(
        f"""SELECT start_time, end_time, remain_time, webhook_url 
        FROM intervals WHERE uuid='{interval_id}'
        """)

    query_result = cur.fetchone()

    con.commit()
    con.close()

    return query_result


def update_table_with_uuid(
        interval_id: str,
        end_time: int,
        remain_time: int) -> None:

    """Update the row with provided uuid to have the provided end_time &
    remain_time
    """

    con = sqlite3.connect(DATABASE_LINK)
    cur = con.cursor()

    cur.execute(
        f"""UPDATE intervals 
        SET end_time = {end_time}, remain_time = {remain_time}
        WHERE uuid='{interval_id}'
           """)

    con.commit()
    con.close()
