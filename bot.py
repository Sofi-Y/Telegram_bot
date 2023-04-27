# 6104124209:AAGMpC-9xLsFEfEo447esiRjrlhLiofVnF8
import logging
import random
import pymorphy2
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import asyncio
import sqlite3
import inspect
import datetime

def funcname():
    return inspect.stack()[1][3]


# Подключение к БД
con = sqlite3.connect("users_db.db")

# Создание курсора
cur = con.cursor()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/motivation', '/picture'],
                  ['/set_timer', '/dialog']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
POSITIVE = ['здоров', 'хорош', 'прекрасн', 'отличн',
            'превосходн', 'замечательн', 'лучше']
NEGATIVE = ['плох', 'ужасн', 'не очень']
NORMAL = ['так себе', 'ничего', 'нормальн', 'ни то ни сё', 'ни то ни се']
WEATHER1 = ['солн', 'тепл', 'тёпл', 'жар']
WEATHER2 = ['пасмур', 'холод', 'дожд', 'сыро', 'облачно']

TIMER = 5 * 60

@bot.message_handler(content_types=['photo'])
def photo_id(message):
    photo = max(message.photo, key=lambda x: x.height)
    print('ok')
    

def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context, a=5 * 60):
    aa = funcname()
    chat_id = update.message.chat_id
    await update.effective_message.reply_text('Вы устанавливаете таймер на 5 минут')
    if a:
        global TIMER
        TIMER = int(args[0])        
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'Вернусь через {TIMER}с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'{TIMER}c. прошли!')
    

async def unset(update, context):
    chat_id = update.message.chat_id
    aa = funcname()
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)
    
    
async def dialog(update, context):
    aa = funcname()
    chat_id = update.message.chat_id
    await update.message.reply_text(
        "Привет. Вы можете поговорить со мной\n"
        "Вы можете прервать разговор, послав команду /stop.\n"
        "Как у Вас дела?")
    return 1


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def first_response(update, context):
    things = update.message.text.lower()
    context.user_data['mood'] = update.message.text
    global POSITIVE
    global NEGATIVE
    global NORMAL
    for x in POSITIVE:
        if x in things:
            await update.message.reply_text(
                f"Так держать!!!")
    for x in NEGATIVE:
        if x in things:
            await update.message.reply_text(
                f"В следующий раз будет лучше! Это точно😊")
    for x in NORMAL:
        if x in things:
            await update.message.reply_text(
                f"Спасибо за ответ!")
    logger.info(things)
    await update.message.reply_text(
        f"Какая погода у вас в городе?")
    return 2



async def second_response(update, context):
    things = update.message.text.lower()
    context.user_data['mood'] = update.message.text
    global POSITIVE
    global NEGATIVE
    global NORMAL
    for x in POSITIVE:
        if x in things:
            await update.message.reply_text(
                f"Ясненько")
    for x in WEATHER1:
        if x in things:
            await update.message.reply_text(
                f"Ясненько")
    for x in NEGATIVE:
        if x in things:
            await update.message.reply_text(
                f"У природы нет плохой погоды")
    for x in NORMAL:
        if x in things:
            await update.message.reply_text(
                f"Спасибо за ответ!")
    for x in WEATHER2:
        if x in things:
            await update.message.reply_text(
                f"разная бывает погода...")
    logger.info(things)
    await update.message.reply_text(
        f"Как вы поживаете?")
    return 3


async def third_response(update, context):
    inf = update.message.text
    logger.info(inf)
    await update.message.reply_text("Понятно. Спасибо за беседу! Всего доброго!")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('dialog', dialog)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_response)]
       },
    fallbacks=[CommandHandler('stop', stop)]
   )


async def start(update, context):
    user = update.effective_user
    aa = funcname()
    chat_id = update.message.chat_id   
    await update.message.reply_text(
        '''Добрый день! Если вам нужна мотивация,
    нажмите /motivation. Если красивая картинка - /picture
    или можете просто поговорить с ботом, написав /dialog или задать таймер для медитации на 5 минут,
    отправив /set_timer''',
        reply_markup=markup
    )

async def picture(update, context):
    aa = funcname()
    chat_id = update.message.chat_id
    pic = random.choice(['img/1.jpg', 'img/2.jpg', 'img/3.jpg',
                         'img/4.jpg', 'img/5.jpg'])
    await context.bot.send_photo(update.message.chat_id, photo=open(pic, 'rb'))


async def help_command(update, context):
    chat_id = update.message.chat_id
    aa = funcname()
    global con
    global cur
    cur.execute('''INSERT INTO users(id,action,time) VALUES(chat_id,aa,datetime.datetime.now()''')
    await update.message.reply_text('''Если вам нужна мотивация,
    нажмите /motivation. Если красивая картинка - /picture
    или можете просто поговорить с ботом, написав /dialog или задать таймер для медитации на 5 минут,
    отправив /set_timer''')
    await update.message.reply_text(f'Записи о пользователях:{context.user_data}')
    
    
async def motivation(update, context):
    aa = funcname()
    chat_id = update.message.chat_id
    a = random.choice(['Не считай дни, извлекай из них пользу',
                       'Усердно работайте, мечтайте по-крупному',
                       'Мечтатели - это спасители мира',
                       'Один из важных ключей к успеху - уверенность в себе. Важный ключ к уверенности в себе - подготовка',
                       'С новым днем приходит новая сила и новые мысли',
                       'Победа - это еще не все, главное это постоянное желание побеждать',
                       'Неудача никогда не одолеет меня, если моя решимость добиться успеха достаточно сильна'])
    await update.message.reply_text(a)


def main():
    application = Application.builder().token('6104124209:AAGMpC-9xLsFEfEo447esiRjrlhLiofVnF8').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("picture", picture))
    application.add_handler(CommandHandler("motivation", motivation))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("task", task))    
    application.add_handler(conv_handler)
    application.run_polling()

    
if __name__ == '__main__':
    main()

con.close()