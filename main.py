from __future__ import print_function

import os.path
import time
import datetime

import src.db as db
import src.sheets as sheets
import src.telegram as tg
import src.cbr as cbr
import src.service as service


MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS = os.environ['MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS']



def update_db(conn, new_orders, deleted_orders, updated_orders):
    """ Calls CRUD operation on orders

    :param conn:
    :param new_orders:
    :param deleted_orders:
    :param updated_orders:
    :return:
    """
    db.create_orders(conn, new_orders)

    db.update_orders(conn, updated_orders)

    db.delete_orders(conn, deleted_orders)


def _get_updated_orders(common_orders, new_orders, old_orders):
    """ Compares common orders between PostgreSQL and Google Sheets

    Generates list of tuples which will be use in UPDATE sql query
    order_number: (cost_usd, delivery_date, cost_rub) - without extra order information

    :param common_orders:
    :param new_orders:
    :return: list of tuples (order_number, cost_usd, delivery_date, cost_rub)
    """
    updated_orders = []
    usd_rate = cbr.get_usd_rate()

    for common_order_number in common_orders:
        if service.orders_are_not_equal(new_orders[common_order_number], old_orders[common_order_number]):
            updated_orders.append(db.format_updated_order(new_orders[common_order_number], usd_rate))

    return updated_orders


def compare_orders(new_data, old_data):
    """ Compares order list between PostgreSQL and Google Sheets

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


def main():
    conn = None
    while not conn:
        conn = db.wait_for_db_init()

        if not conn:
            time.sleep(10)


    actual_db_data = db.get_orders_from_db(conn)

    orders_delivery_passed_already_notified = set()

    telegram_remind_start_time = datetime.datetime.now()

    while True:
        print('\nPerforming query to Google Sheets...')

        # Google Sheets
        new_order_data, network_error = sheets.read_sheet()
        if network_error:
            continue

        # Telegram
        orders_notified = tg.send_notifications_delivery_passed(new_order_data, orders_delivery_passed_already_notified)

        # Get orders difference
        orders_to_insert, orders_to_delete, orders_to_update = compare_orders(new_order_data, actual_db_data)

        # Save difference to PostgreSQL
        update_db(conn, orders_to_insert, orders_to_delete, orders_to_update)


        actual_db_data = new_order_data
        orders_delivery_passed_already_notified = orders_notified
        next_query_time = datetime.datetime.now() + datetime.timedelta(seconds=int(MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS))
        print(f'Done. Next query in {MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS} seconds: {next_query_time}')


        # Check telegram notification period
        if tg.time_to_send_msg_to_telegram(telegram_remind_start_time):
            telegram_remind_start_time = datetime.datetime.now()
            orders_delivery_passed_already_notified = set()

        # Wait for next query to Google Sheets
        time.sleep(int(MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS))


if __name__ == '__main__':
    main()
