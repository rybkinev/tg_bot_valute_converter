from telebot import TeleBot, types

import settings
import extensions

bot = TeleBot(settings.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    text = """Добро пожаловать!! 
Я могу конвертировать валюту по курсу на текущий день. 
Список доступных валют можно посмотреть в меню

Формат сообщения для конвертации:
<валюта, цену которой он хочет узнать> <валюта, в которой надо узнать цену первой валюты> <количество первой валюты>
Например: рубль евро 100
"""
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def handle_values(message):
    valutes = ['- ' + i for i in settings.CURRENCIES.keys()]
    text = 'Доступные валюты для конвертации:\n' + "\n".join(valutes)
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    """
    < имя валюты, цену которой он хочет узнать > - base
    < имя валюты, в которой надо узнать цену первой валюты > - quote
    < количество первой валюты > - amount
    """
    try:
        parse = extensions.CurrencyRates(message.text)
        result = parse.get_price()
    except extensions.IncorrectMessageError:
        bot.send_message(message.chat.id, 'Неверно написано сообщение. За помощью обратитесь к справке')
    except extensions.AmountIsNotDigitError:
        bot.send_message(message.chat.id, 'Неверно указана сумма для перевода. Ожидается число')
    except extensions.IncorrectValuteError as e:
        bot.send_message(message.chat.id, str(e))
    except extensions.RatesNotAvailableError:
        bot.send_message(message.chat.id, 'Не удалось получить курс валют, сервис не доступен. Попробуйте позже')
    else:
        bot.send_message(message.chat.id, result)


if __name__ == '__main__':
    bot.set_my_commands([
        types.BotCommand("/help", "Помощь"),
        types.BotCommand('/values', 'Список доступных валют')
    ])
    bot.infinity_polling()
