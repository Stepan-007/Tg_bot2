import logging

from telegram import Poll, Update
from telegram.ext import Application, CommandHandler, ContextTypes, PollHandler

from random import choice
import sqlite3
from pymorphy2 import MorphAnalyzer

from list_words import get_list_words
from word_class import Word

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

WORDS = get_list_words()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(help_command())
    con = sqlite3.connect('db/words_tgbot.db')
    cur = con.cursor()
    res = cur.execute(
        f'select * from MainTable where user_id = {update.effective_user.id}').fetchall()
    if len(res) == 0:
        for word in WORDS:
            cur.execute(
                f'insert into MainTable(user_id, word) values({update.effective_user.id}, "{word}")')
        con.commit()


def help_command():
    """Отправляет сообщение когда получена команда /help"""
    return '''/admin - поможет тебе узнать имена создателей этого проекта.
/work_time - укажет время работы нашего бота.
/address - поможет узнать адрес нашего офиса.
/phone - поможет позвонить админам и пожаловаться на проект :)
/quiz - команда, при введении которой открывается возможность поставить ударение в слове"'''


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


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a predefined poll"""
    word = Word(choice(WORDS))
    questions = word.get_all_variants()
    message = await update.effective_message.reply_poll(
        f'Поставьте ударение в слове "{word.get_right_variant().lower().capitalize()}"',
        questions, type=Poll.QUIZ,
        correct_option_id=questions.index(word.get_right_variant()),
        explanation=f'Правильный ответ: {word.get_right_variant()}'
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)
    print(update.effective_user.id)


async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    word = args[0]

    RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    VOWELS = 'А, Е, И, О, У, Ы, Э, Ю, Я'.split(', ')

    con = sqlite3.connect('db/words_tgbot.db')
    cur = con.cursor()
    user_words = list(map(lambda row: row[0], cur.execute(
        f'select word from MainTable where user_id = {update.effective_user.id}').fetchall()))

    # если пользователь не ввёл слово, которое надо добавить
    if len(args) == 0:
        await update.message.reply_text('Вы не ввели слово, которое надо добавить')
    # если пользователь ввёл сразу несколько слов для добавления
    elif len(args) > 1:
        await update.message.reply_text('Добавлять можно только по одному слову за раз')
    # если слово уже есть в списке
    elif word in user_words:
        await update.message.reply_text('Это слово уже есть в списке')
    # если в слове встречаются символы не из русского алфавита
    elif not all(map(lambda let: let in RUSSIAN_ALPHABET, word.lower())):
        await update.message.reply_text(
            'Необходимо написать слово только буквами русского алфавита без ' \
            'дополнительных знаков и разделителей')
    # если в слове нет букв, выделенных верхним регистром (ударной буквы)
    elif word.lower() == word:
        await update.message.reply_text('Необходимо выделить верхним регистром букву,' \
                                        'на которую падает ударение')
    # если в слове больше одной буквы, выделенной верхним регистром
    elif len([letter for letter in word if letter.isupper()]) > 1:
        await update.message.reply_text('Необходимо выделить капсом ОДНУ букву' \
                                        ', на которую падает ударение')
    # если выделенная верхним регистром ударная буква оказалась согласной
    elif [letter for letter in word if letter.isupper()][0] not in VOWELS:
        await update.message.reply_text('Необходимо выделить капсом ГЛАСНУЮ букву, ' \
                                        'на которую падает ударение.')
    # если есть "ё" в слове и оно не выделено как ударное
    elif 'ё' in word:
        await update.message.reply_text('Ошибка. Буква "ё" всегда ударная')
    # если слова не существует
    elif str(MorphAnalyzer().parse(word)[0].methods_stack[0][0]) == 'FakeDictionary()':
        await update.message.reply_text(
            'Скорее всего, такого слова не существует. Попробуйте другое')
    # если в слове одна гласная
    elif sum([word.lower().count(vowel.lower()) for vowel in VOWELS]) == 1:
        await update.message.reply_text('В этом слове одна гласная, она же и будет ударной. ' \
                                        'Нет смысла добавлять такое слово')
    else:
        # добавляем слово в список. Если в слове есть буква "Ё", меняем её на "Е"
        await update.message.reply_text('Слово будет успешно добавлено, когда Миша сделает так, чтобы слово добавлялось в БД')


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        "6260730894:AAGwAXctln7jY9cQPEx-X6RZSqOQDqFKX_Y").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("address", address))
    application.add_handler(CommandHandler("phone", phone))
    application.add_handler(CommandHandler("work_time", work_time))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(PollHandler(receive_quiz_answer))

    application.run_polling()


if __name__ == "__main__":
    main()
