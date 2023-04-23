import logging

from telegram import Poll, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, PollHandler

from random import choice

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


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        "6260730894:AAGwAXctln7jY9cQPEx-X6RZSqOQDqFKX_Y").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("address", address))
    application.add_handler(CommandHandler("phone", phone))
    application.add_handler(CommandHandler("work_time", work_time))
    application.add_handler(PollHandler(receive_quiz_answer))

    application.run_polling()


if __name__ == "__main__":
    main()
