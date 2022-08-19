import requests
import datetime
import os


TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
TG_REMINDER_FREQUENCY_SECONDS = os.environ['TG_REMINDER_FREQUENCY_SECONDS']


def _send_telegram_message(message, chat_ids):
    """ Sends message to all chats, opened with bot.
        Directly calls the Telegram API

    :param message:
    :param chat_ids:
    :return:
    """
    for chat_id in chat_ids:
        api_call = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
        requests.get(api_call)


def get_chat_ids():
    """ Receives list of chat id's, opened with bot.

    :return:
    """
    chat_ids = set()
    updates_url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates'
    updates = requests.get(updates_url).json()
    for result in updates['result']:
        if 'message' in result.keys():
            if not result['message']['chat']['id'] in chat_ids:
                chat_ids.add(result['message']['chat']['id'])
    return chat_ids


def send_notifications_delivery_passed(orders, already_notified):
    """ Describes sending notifications process.

    1. Receiving a list of chats, to which messages will be sent
    2. Sending messages

    :param orders:
    :param already_notified:
    :return:
    """
    notified_orders = set()
    chat_ids = get_chat_ids()

    for order, order_value in orders.items():
        if _delivery_date_passed(order_value[3]):
            notified_orders.add(order)
            # if time to notify again about orders, which are already notified, has not yet come, continue
            if order in already_notified:
                continue

            msg = f'Не соблюден срок поставки заказа: {order} ({order_value[3]})'
            _send_telegram_message(msg, chat_ids)

    return notified_orders


def _delivery_date_passed(date):
    """ Checks if delivery date passed.
    Transforms date in Google Sheet's format to datetime and compares it
    with today

    :param date: Google Sheet format date
    :return: True, if order delivery date in Google Sheets is passed
    """
    order_date = datetime.date(int(date.split('.')[2]),
                             int(date.split('.')[1]),
                             int(date.split('.')[0]))

    if order_date < datetime.date.today():
        return True


def time_to_send_msg_to_telegram(remind_start):
    """ Checks if it's time to send messages about orders that have already been reminded

    Messages about orders sends not once time.
    At the end of period, described in TG_REMINDER_FREQUENCY_SECONDS env variable, ks-test
    will again send messages about all orders with delivery date passed even if they have already
    been reported.

    This function decides if the waiting period passed

    :param remind_start:
    :return: True, if the waiting period passed
    """
    remind_now = datetime.datetime.now()
    seconds = (remind_now - remind_start).seconds
    if seconds > int(TG_REMINDER_FREQUENCY_SECONDS):
        return True
