import json

import requests

__all__ = [
    'CurrencyRates',
    'RatesNotAvailableError',
    'IncorrectMessageError',
    'IncorrectValuteError',
    'AmountIsNotDigitError'
]

import settings


class RatesNotAvailableError(Exception):
    """
    Исключение когда не удалось получить курс валют с сайта
    """
    pass


class IncorrectMessageError(Exception):
    """
    Передано некорректное сообщение
    """
    pass


class IncorrectValuteError(Exception):
    """
    Некорректная валюта
    """
    pass


class AmountIsNotDigitError(Exception):
    pass


class Common:

    def __init__(self):
        self.rates = self._get_rates()

    @staticmethod
    def source_url():
        return "https://www.cbr-xml-daily.ru/daily_json.js"

    @staticmethod
    def _decode_rates(response):
        return response.json().get('Valute', {})

    def _get_rates(self):
        response = requests.get(Common.source_url())
        if response.status_code != 200:
            raise RatesNotAvailableError()
        return self._decode_rates(response)

    def _get_rate(self, valute):
        return self.rates.get(valute, {}).get('Value', None)


class CurrencyRates(Common):

    def __init__(self, message_text):

        params = message_text.split()

        if len(params) != 3:
            raise IncorrectMessageError()
        base, quote, amount = params

        self.base = settings.CURRENCIES.get(base, None)
        self.quote = settings.CURRENCIES.get(quote, None)
        try:
            self.amount = float(amount)
        except:
            raise AmountIsNotDigitError()

        if not self.quote:
            raise IncorrectValuteError(f'В справочнике не найдена валюта "{quote}". '
                                       f'Список доступных можно посмотреть в меню')
        elif not self.base:
            raise IncorrectValuteError(f'В справочнике не найдена валюта "{base}". '
                                       f'Список доступных можно посмотреть в меню')

        super(CurrencyRates, self).__init__()

    @staticmethod
    def _rounding(number):
        return round(number, 4)

    def get_price(self):

        if self.base == self.quote:
            return float(self.amount)

        rate_base = self._get_rate(self.base)
        rate_quote = self._get_rate(self.quote)

        if rate_base is None:
            return self._rounding(self.amount / rate_quote)
        elif rate_quote is None:
            return self._rounding(self.amount * rate_base)

        return self._rounding((rate_base / rate_quote) * self.amount)
