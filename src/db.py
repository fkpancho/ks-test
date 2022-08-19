import psycopg2
import os
from . import cbr


DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_TABLE = os.environ['DB_TABLE']
DB_PORT = os.environ['DB_PORT']


def _generate_sql_create_table_query():
    return f'CREATE TABLE IF NOT EXISTS {DB_TABLE} ( \
                nubmer integer NOT NULL, \
                order_number integer NOT NULL, \
                cost_usd integer NOT NULL DEFAULT 0, \
                delivery_date date NOT NULL, \
                cost_rub integer NOT NULL DEFAULT 0, \
                PRIMARY KEY (order_number) \
                )'


def _create_table_if_not_exists(conn):
    """ Performs create table sql query

    :param conn:
    :return:
    """
    cur = conn.cursor()
    query = _generate_sql_create_table_query()
    cur.execute(query)
    cur.close()
    conn.commit()


def _generate_orders_sql_insert_query(orders):
    """ Generates SQL INSERT query
    which inserts new orders in db

    :param orders:
    :return:
    """
    usd_rate = cbr.get_usd_rate()
    values = ", ".join([f"({int(order[0])}," \
                        f" {int(order[1])}," \
                        f" {int(order[2])}," \
                        f" \'{_format_gsheets_date_to_psql(order[3])}\'," \
                        f" {int(usd_rate * int(order[2]))})"
                        for order in orders])

    return f'insert into {DB_TABLE} values {values}'


def create_orders(conn, orders):
    """ Executes inserting new orders to db

    :param conn:
    :param orders:
    :return:
    """
    if not orders:
        return

    cur = conn.cursor()
    try:
        query = _generate_orders_sql_insert_query(orders)
    except ValueError:
        cur.close()
        return
    cur.execute(query)
    cur.close()
    conn.commit()


def delete_orders(conn, orders):
    """ Executes deleting new orders to db

    :param conn:
    :param orders:
    :return:
    """
    if not orders:
        return

    cur = conn.cursor()

    query = f'delete from {DB_TABLE} where order_number in %s'

    cur.execute(query, (tuple(orders),))
    cur.close()
    conn.commit()


def _generate_sql_update_query(order):
    return f"update {DB_TABLE} set cost_usd = {int(order[1])}," \
           f" delivery_date = \'{order[2]}\'," \
           f" cost_rub = {int(order[3])} " \
           f"where order_number = {order[0]}"


def update_orders(conn, orders):
    if not orders:
        return

    for order in orders:
        cur = conn.cursor()
        query = _generate_sql_update_query(order)
        cur.execute(query)
        cur.close()
        conn.commit()


def wait_for_db_init():
    try:
        conn = psycopg2.connect(dbname=DB_NAME,
                                user=DB_USER,
                                host=DB_HOST,
                                password=DB_PASSWORD)
        return conn
    except psycopg2.OperationalError as error:
        if f"Connection refused" in str(error):
            return None
        else:
            print(f'wait_for_db_init(): Error while waiting connection: {str(error)}')
            exit(1)


def get_orders_from_db(conn):
    """ Selects orders from db and creates table, if it didn't exist

    :param conn:
    :return:
    """
    _create_table_if_not_exists(conn)

    cur = conn.cursor()
    query = f'select * from {DB_TABLE}'

    cur.execute(query)
    data = cur.fetchall()
    cur.close()

    return {row[1]: row for row in data}


def format_updated_order(order, usd_rate):
    """ Brings information about the changed order to a form ready for insertion

    :return:
    """
    return (int(order[1]),
            int(order[2]),
            _format_gsheets_date_to_psql(order[3]),
            int(int(order[2]) * usd_rate))


def _format_gsheets_date_to_psql(date):
    """ Date in Google Sheets in DD.MM.YYYY format.
        Date in PostgreSQL needs YYYY-MM-DD format.

        This function creates PostgreSQL date format from Google Sheets format.

    :param date:
    :return:
    """
    return f'{date.split(".")[2]}-{date.split(".")[1]}-{date.split(".")[0]}'
