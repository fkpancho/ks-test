from __future__ import print_function

import os.path
import time
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import requests
import psycopg2

import xml.etree.ElementTree as XML_ET

DEBUG = False

# ================================================================================================
# ================================================================================================
# ================================ TEST VARIABLES
if DEBUG:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '17QEW5pedoH2n5pP1Jsny7MZnJAWQnOMrWhSjTGZ2vO8'

    SAMPLE_RANGE_NAME = 'A:D'

    DB_NAME = 'test'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = '192.168.9.226'
    DB_TABLE = 'orders'
    DB_PORT = '5431'

    CBR_CURRENCY_API_URL = 'https://cbr.ru/scripts/XML_daily.asp'
    CURRENCY_XML_FIND_PATTERN = ".Valute[CharCode='USD']/Value"

    CLIENT_SECRET_FILE = 'client_secret_226730576997-ec5guc24o5fjat8mfq0bgt1sm48188ag.apps.googleusercontent.com.json'
    CLIENT_TOKEN_FILE = 'token.json'
# ================================================================================================
# ================================================================================================


# ================================================================================================
# ================================================================================================
# ================================ DOCKER VARIABLES
if not DEBUG:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = os.environ['SAMPLE_SPREADSHEET_ID']

    SAMPLE_RANGE_NAME = os.environ['SAMPLE_RANGE_NAME']

    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_PASSWORD']
    DB_HOST = os.environ['DB_HOST']
    DB_TABLE = os.environ['DB_TABLE']
    DB_PORT = os.environ['DB_PORT']

    CBR_CURRENCY_API_URL = os.environ['CBR_CURRENCY_API_URL']
    CURRENCY_XML_FIND_PATTERN = os.environ['CURRENCY_XML_FIND_PATTERN']

    CLIENT_SECRET_FILE = os.environ['CLIENT_SECRET_FILE']
    CLIENT_TOKEN_FILE = os.environ['CLIENT_TOKEN_FILE']


# ================================================================================================
# ================================================================================================

def read_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.

    :return: result, http_error
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(CLIENT_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(CLIENT_TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(CLIENT_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return {}, None

        res = {}
        # [1:] because we don't need Google Sheets header
        for row in values[1:]:
            # if row is empty, don't worry
            try:
                res[int(row[1])] = tuple(row)
            except IndexError:
                pass
    except HttpError as err:
        print(err)
        return {}, err

    return res, None


def get_usd_rate():
    usd_value_float = float(XML_ET.fromstring(requests.get(CBR_CURRENCY_API_URL).text)
                            .find(CURRENCY_XML_FIND_PATTERN)
                            .text.replace(",", "."))
    return usd_value_float


def _create_db():
    print(f'_create_db(): Получаю подключение к корневой БД postgres...')
    print(f'_create_db(): dbname = postgres')
    print(f'_create_db(): user = postgres')
    print(f'_create_db(): host = {DB_HOST}')
    print(f'_create_db(): password = postgres')
    try:
        conn = psycopg2.connect(
            database='postgres',
            user='postgres',
            password='postgres',
            host=DB_HOST,
            port=DB_PORT
        )
    except psycopg2.OperationalError as error:
        print(f'_create_db(): Не удалось подключиться к корневой БД PostgreSQL. Ошибка: {str(error)}')
        time.sleep(600)
        exit(1)

    print(f'_create_db(): Подключение получено. Создаю таблицу...')
    query = f'create database {DB_NAME}'

    with conn.cursor() as cursor:
        print(f'_create_db(): Готовимся cursor.execute()...')
        cursor.execute(query)
        print(f'_create_db(): cursor.execute() выполнено...')

    conn.commit()
    cursor.close()
    conn.close()
    print(f'_create_db(): БД создана.')


def _init_db_conn():
    # print(f'_init_db_conn(): Стартовое подключение к БД. Буду создавать БД {DB_NAME}')
    # with psycopg2.connect(
    #         database='postgres',
    #         user='postgres',
    #         password='postgres',
    #         host=DB_HOST,
    #         port='5432'
    # ) as conn:
    #     print(f'_init_db_conn(): Подключение получено. Создаю БД...')
    #     query = f'create database {DB_NAME}'
    #
    #     conn.autocommit = True
    #
    #     with conn.cursor() as cursor:
    #         cursor.execute(query)

    print(f'_init_db_conn(): Ну чо, БД появилась?...')
    # time.sleep(600)

    return psycopg2.connect(dbname=DB_NAME,
                            user=DB_USER,
                            host=DB_HOST,
                            password=DB_PASSWORD)


def _get_db_conn():
    print('_get_db_conn(): Возвращаю подключение к БД: ')
    print(f'_get_db_conn(): dbname = {DB_NAME}')
    print(f'_get_db_conn(): user = {DB_USER}')
    print(f'_get_db_conn(): host = {DB_HOST}')
    print(f'_get_db_conn(): password = {DB_PASSWORD}')
    try:
        print('_get_db_conn(): Первая попытка...')
        conn = psycopg2.connect(dbname=DB_NAME,
                                user=DB_USER,
                                host=DB_HOST,
                                password=DB_PASSWORD)
        print('_get_db_conn(): Первая попытка удачная!')
        return conn
    except psycopg2.OperationalError as error:
        print(f'_get_db_conn(): Ошибка! {str(error)}')
        if f"database \"{DB_NAME}\" does not exist" in str(error):
            print(f'_get_db_conn(): Нет БД {DB_NAME}. Создаю...')
            _create_db()
            return psycopg2.connect(dbname=DB_NAME,
                                    user=DB_USER,
                                    host=DB_HOST,
                                    password=DB_PASSWORD)
        else:
            print(f'_get_db_conn(): Разбирайся, короче')
            # time.sleep(600)
            exit(1)


def _format_psql_table_create_query():
    return f'CREATE TABLE IF NOT EXISTS {DB_TABLE} ( \
                nubmer integer NOT NULL, \
                order_number integer NOT NULL, \
                cost_usd integer NOT NULL DEFAULT 0, \
                delivery_date date NOT NULL, \
                cost_rub integer NOT NULL DEFAULT 0, \
                PRIMARY KEY (order_number) \
                )'


def _create_table_if_not_exists(conn):
    print(f'_create_table_if_not_exists(): Создаю таблицу {DB_TABLE}, если она ещё не создана..')
    cur = conn.cursor()
    query = _format_psql_table_create_query()
    cur.execute(query)
    cur.close()
    conn.commit()
    print(f'_create_table_if_not_exists(): Готово.')





def get_orders_from_db(conn):
    print(f'get_orders_from_db(): Начинаю работать.')
    # conn = _init_db_conn()
    # conn = _create_db()

    # conn = _get_db_conn()

    _create_table_if_not_exists(conn)

    cur = conn.cursor()
    query = f'select * from {DB_TABLE}'

    cur.execute(query)
    data = cur.fetchall()
    cur.close()

    print(f'get_orders_from_db(): Заказы из БД получены.')

    return {row[1]: row for row in data}


def _format_psql_insert_order_query(orders):
    usd_rate = get_usd_rate()
    values = ", ".join([f"({int(order[0])}," \
                        f" {int(order[1])}," \
                        f" {int(order[2])}," \
                        f" \'{_format_gsheets_date_to_psql(order[3])}\'," \
                        f" {int(usd_rate * int(order[2]))})"
                        for order in orders])

    return f'insert into {DB_TABLE} values {values}'


def _create_orders(conn, orders):
    if not orders:
        return

    cur = conn.cursor()
    try:
        query = _format_psql_insert_order_query(orders)
    except ValueError:
        cur.close()
        return
    cur.execute(query)
    cur.close()
    conn.commit()


def _delete_orders(conn, orders):
    if not orders:
        return

    cur = conn.cursor()

    query = f'delete from {DB_TABLE} where order_number in {tuple(orders)}'

    cur.execute(query)
    cur.close()
    conn.commit()


def _format_psql_update_query(order):
    return f"update {DB_TABLE} set cost_usd = {int(order[1])}," \
           f" delivery_date = \'{order[2]}\'," \
           f" cost_rub = {int(order[3])} " \
           f"where order_number = {order[0]}"


def _update_orders(conn, orders):
    if not orders:
        return

    for order in orders:
        cur = conn.cursor()
        query = _format_psql_update_query(order)
        cur.execute(query)
        cur.close()
        conn.commit()


def update_db(new_orders, deleted_orders, updated_orders):
    conn = _get_db_conn()

    _create_orders(conn, new_orders)

    _update_orders(conn, updated_orders)

    _delete_orders(conn, deleted_orders)


def _format_gsheets_date_to_psql(date):
    return f'{date.split(".")[2]}-{date.split(".")[1]}-{date.split(".")[0]}'


def _not_equal_cost(new, old):
    return int(new) != int(old)


def _not_equal_delivery_date(new, old):
    date_new = datetime.date(int(new.split('.')[2]),
                             int(new.split('.')[1]),
                             int(new.split('.')[0]))

    return date_new != old


def _orders_are_not_equal(new, old):
    if _not_equal_cost(new[2], old[2]):
        return True

    if _not_equal_delivery_date(new[3], old[3]):
        return True


def _format_updated_order(order, usd_rate):
    """
    Приводит инфомацию об изменившемся заказе к готовому к вставке виду
    :return:
    """
    return (int(order[1]),
            int(order[2]),
            _format_gsheets_date_to_psql(order[3]),
            int(int(order[2]) * usd_rate))


def _get_updated_orders(common_orders, new_orders, old_orders):
    """
    Сравнивает заказы, имеющиеся и в БД, и в Google Sheets.

    Формирует список кортежей для UPDATE БД
    номер_заказа: (стоимость в usd, дата доставки, стоимость в руб.) - без лишней информации о номере заказа и т.п.

    :param common_orders:
    :param new_orders:
    :return: list of tuples (order_number, cost_usd, delivery_date, cost_rub)
    """
    updated_orders = []
    # 1. получить курс USD
    usd_rate = get_usd_rate()

    # 2. по каждому из совпадающих заказов сравнить - есть ли изменения
    for common_order_number in common_orders:
        if _orders_are_not_equal(new_orders[common_order_number], old_orders[common_order_number]):
            updated_orders.append(_format_updated_order(new_orders[common_order_number], usd_rate))

    return updated_orders


def compare_orders(new_data, old_data):
    """

    :param new_data:
    :param old_data:
    :return: new: list of orders, which was added to Google Sheets
                deleted: set of order numbers, which was deleted from Google Sheets
                updated: dict of orders
    """
    new_data_keys = set(new_data.keys())
    old_data_keys = set(old_data.keys())

    # 1. deleted orders
    deleted = old_data_keys.difference(new_data_keys)

    # 2. new orders
    new_orders_numbers = new_data_keys.difference(old_data_keys)
    new = [new_data[new_order_number] for new_order_number in new_orders_numbers]

    # 3. common orders
    common_orders_numbers = set.intersection(new_data_keys, old_data_keys)
    updated = _get_updated_orders(common_orders_numbers, new_data, old_data)
    return new, deleted, updated


def wait_for_db_init():
    try:
        conn = psycopg2.connect(dbname=DB_NAME,
                                user=DB_USER,
                                host=DB_HOST,
                                password=DB_PASSWORD)
        print('wait_for_db_init(): Ого, БД сразу инициализирована! Круто.')
        return conn
    except psycopg2.OperationalError as error:
        print(f'wait_for_db_init(): Ошибка! {str(error)}')
        if f"Connection refused" in str(error):
            print(f'wait_for_db_init(): БД пока не инициализировалась. Ждём 10 сек.')
            return None
        else:
            print(f'wait_for_db_init(): Другая ошибка.')
            exit(1)


def main():
    """

    1. Получили old значения из БД

    --- while true

            2. Получили new значения из xlsx файла

            3. Сравнили new и old

            4.1 Если есть изменения - внесли их в БД
                old = new

            4.2 Нет изменений - дальше по циклу


    :return:
    """
    conn = None
    while not conn:
        time.sleep(10)
        conn = wait_for_db_init()


    print(f'main.py(): Начало работы. Получаем актуальные данные из БД..')
    old_data = get_orders_from_db(conn)

    while True:
        print('\n--- Watch to Google Sheets...')
        new_data, network_error = read_sheet()
        if network_error:
            continue

        orders_to_insert, orders_to_delete, orders_to_update = compare_orders(new_data, old_data)
        update_db(orders_to_insert, orders_to_delete, orders_to_update)
        old_data = new_data
        print('--- End. sleeping...')
        time.sleep(5)


if __name__ == '__main__':
    main()
