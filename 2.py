# Импортируем необходимые классы.
import logging
from datetime import datetime
from random import sample
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from list_words import get_list_words
from word_class import Word
from kkeyboard import create_keyboard

WORDS = get_list_words()  ### Получаем список слов с которыми будет работать

#
# reply_keyboard = [sample(WORDS, 4)]
#
# keya = [['/address', '/phone'],
#                   ['/site', '/work_time']]
#
# print(reply_keyboard)
#
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

keybord2 = [['/dice', '/timer']]

markup_2 = ReplyKeyboardMarkup(keybord2, one_time_keyboard=True)
# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Определяем функцию-обработчик сообщений.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    reply_keyboard = [sample(WORDS, 4)]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я бот созданные для тренировки правил ударения." + '\n' + help_command(),
    reply_markup=markup)


async def task(context):
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'Тренировка закончена')


async def start_training(update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    try:
        due = int(context.args[0])
        if due <= 0:
            await update.effective_message.reply_text("Тренировка не может проходить без слов")
            return
        elif due > 20:
            await update.effective_message.reply_text("Выбрано больше 20 слов для тренировки :(")
            return
        text = 'Тренировка началась'
        await update.effective_message.reply_text(text)
        words = sample(WORDS, due)
        for i in range(due):
            text = f'Поставьте ударение в слове "{words[i].lower().capitalize()}"'
            await update.effective_message.reply_text(text)
            word = Word(words[i])
            all_variants = word.get_all_variants()
            keyboard_variants = create_keyboard(all_variants)
            print(keyboard_variants)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Вы не ввели параметр таймера. Попробуйте еще раз")


async def help(update, context):
    await update.message.reply_text(help_command())


def help_command():
    """Отправляет сообщение когда получена команда /help"""
    return '''/admin - помежет тебе узнать имена создателей этого проекта.
/work_time - укажет время работы нашего бота.
/address - поможет узнать адрес нашего офиса.
/phone - поможет позвонить админам и пожаловаться на проект :)
/play - запустит вам игру Ударялка'''


# Зарегистрируем их в приложении перед
# регистрацией обработчика текстовых сообщений.
# Первым параметром конструктора CommandHandler я
# вляется название команды.

async def admin(update, contest):
    await update.message.reply_text(f'Это проект Анкудинова Степана и Дудича Михаила')


# Напишем соответствующие функции.

async def address(update, context):
    await update.message.reply_text(
        "У нас пока нет офиса, но если вы дадите нам денег, он обязательно появится :)")


async def phone(update, context):
    await update.message.reply_text("Телефон: +7(908)736-44-78\nТелефон: +7(986)758-45-60")


async def work_time(update, context):
    await update.message.reply_text(
        "Время работы: Мы не работаем, пока нам не платят")


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token('5922594006:AAEmSgUMEcYYl7IO0qGr_RvaLYsoWDwoUY4').build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # Регистрируем обработчик в приложении.
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("play", start_training))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("address", address))
    application.add_handler(CommandHandler("phone", phone))
    application.add_handler(CommandHandler("work_time", work_time))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("close", close_keyboard))
    # Запускаем приложение.
    application.run_polling()


# Добавим необходимый объект из модуля telegram.ext


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
