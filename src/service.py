import datetime


def _not_equal_cost(new, old):
    """ Compares old cost and new cost of changed order

    :param new:
    :param old:
    :return: True, if cost differs, False otherwise
    """
    return int(new) != int(old)


def _not_equal_delivery_date(new, old):
    """ Compares old delivery date and new delivery date of changed order

        :param new:
        :param old:
        :return: True, if delivery date differs, False otherwise
        """
    date_new = datetime.date(int(new.split('.')[2]),
                             int(new.split('.')[1]),
                             int(new.split('.')[0]))

    return date_new != old


def orders_are_not_equal(new_order_data, old_order_data):
    """ Execute orders compare functions.

    Checks options:
        1. cost changes
        2. delivery date changes

    :param new_order_data:
    :param old_order_data:
    :return: True, if at least one option differs between old and new order data
    """
    if _not_equal_cost(new_order_data[2], old_order_data[2]):
        return True

    if _not_equal_delivery_date(new_order_data[3], old_order_data[3]):
        return True
