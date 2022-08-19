import requests
import xml.etree.ElementTree as XmlEt
import os

CBR_CURRENCY_API_URL = os.environ['CBR_CURRENCY_API_URL']
CBR_CURRENCY_XML_FIND_PATTERN = os.environ['CBR_CURRENCY_XML_FIND_PATTERN']


def get_usd_rate():
    """ Gets USD currency from CBR API

    :return: float value of USD currency
    """
    usd_value_float = float(XmlEt.fromstring(requests.get(CBR_CURRENCY_API_URL).text)
                            .find(CBR_CURRENCY_XML_FIND_PATTERN)
                            .text.replace(",", "."))
    return usd_value_float
