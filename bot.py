# 6104124209:AAGMpC-9xLsFEfEo447esiRjrlhLiofVnF8
import logging
import random
import pymorphy2
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import asyncio
import datetime
import time
import sqlite3
from flask import Flask
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def time_of_day():
    tod_dict = {0: 'ночь', 1: 'ночь', 2: 'ночь',
                    3: 'утро', 4: 'утро', 5: 'утро',
                    6: 'утро', 7: 'утро', 8: 'утро',
                    9: 'день', 10: 'день', 11: 'день',
                    12: 'день', 13: 'день', 14: 'день',
                    15: 'день', 16: 'день', 17: 'день',
                    18: 'вечер', 19: 'вечер', 20: 'вечер',
                    21: 'вечер', 22: 'вечер', 23: 'вечер'}
    dt = datetime.datetime.now()
    h = dt.hour
    if h in tod_dict:
        tod = tod_dict[h]
        return tod

    
def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


global_init("users_tg.db")


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mood = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/motivation', '/picture'],
                  ['/set_timer', '/dialog', '/rating']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
POSITIVE = ['здоров', 'хорош', 'прекрасн', 'отличн',
            'превосходн', 'замечательн', 'лучше']
NEGATIVE = ['плох', 'ужасн', 'не очень']
NORMAL = ['так себе', 'ничего', 'нормальн', 'ни то ни сё', 'ни то ни се']
WEATHER1 = ['солн', 'тепл', 'тёпл', 'жар']
WEATHER2 = ['пасмур', 'холод', 'дожд', 'сыро', 'облачно']

TIMER = 5 * 60



def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context):
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    context.user_data['rating'] = 10
    user1.rating = 10    
    if not context.user_data:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
    chat_id = update.message.chat_id
    await update.effective_message.reply_text('Вы устанавливаете таймер на 5 минут')
    global TIMER
    TIMER = 5 * 60
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
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    context.user_data['rating'] = 10
    user1.rating = 10    
    if not context.user_data:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)
    
    
async def dialog(update, context):
    chat_id = update.message.chat_id
    if time_of_day() == 'день' or time_of_day() == 'вечер':
        await update.message.reply_text(
            f'''Добрый {time_of_day()}! Вы можете поговорить со мной
Вы можете прервать разговор, послав команду /stop.
Как у Вас дела?''')
    elif time_of_day() == 'утро':
        await update.message.reply_text(
            f'''Доброе утро! Вы можете поговорить со мной
Вы можете прервать разговор, послав команду /stop.
Как у Вас дела?''')
    else:
        await update.message.reply_text(
            "Привет. Вы можете поговорить со мной\n"
            "Вы можете прервать разговор, послав команду /stop.\n"
            "Как у Вас дела?")
    return 1


async def stop(update, context):
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    context.user_data['rating'] = 10
    user1.rating = 10
    if not context.user_data:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def first_response(update, context):
    things = update.message.text.lower()
    context.user_data['mood'] = update.message.text
    context.user_data['rating'] = 10
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    user1.rating = 10
    if not context.user_data:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
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
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    context.user_data['rating'] = 10
    user1.rating = 10
    if not context.user_data:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
    inf = update.message.text
    logger.info(inf)
    await update.message.reply_text('''Понятно. Спасибо за беседу! Теперь Вы можете задать вопрос боту.
Примечание: так как данный бот создан для мотивации, то и вопросы ему лучше следует задавать на подобную тему, например, о целях, усехе, здоровье и тд''')
    await update.message.reply_text("Хотите задать боту вопрос?")
    return 12


async def res1(update, context):
    txt = update.message.text.lower()
    if 'да' in txt:
        await update.message.reply_text('Можете задавать:')
        return 7
    elif 'нет' in txt:
        await update.message.reply_text("Всего доброго!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Извините, не понимаю")
        return ConversationHandler.END


async def question(update, context):
    a = update.message.text.lower()
    if 'деньг' in a or 'финанс' in a or 'заработ' in a:
        await update.message.reply_text('Работайте старательно и усердно, тогда у вас всё получится')
    elif 'здоров' in a:
        await update.message.reply_text('Регулярно занимайтесь спортом и правильно питайтесь')
    elif 'счаст' in a or 'радос' in a:
        await update.message.reply_text('''Мыслите позитивно и
составьте список занятий, которые делают вас счастливым.
Потом внесите эти пункты в ежедневное расписание''')
    elif 'пробле' in a or 'трудно' in a or 'неудач' in a:
        await update.message.reply_text(random.choice(['Практикуйте позитивный внутренний диалог',
                                                       'Действуйте осознанно',
                                                       'Предствляйте свой успех',
        'Подумайте, что вам нужно предпринять, какие конкретные шаги приблизят вас к намеченным целям']))
    elif 'мечт' in a or 'цель' or 'целей' in a or 'желани' in a or 'цели' in a or 'успеш' or 'успех' in a:
        await update.message.reply_text(random.choice(['Каждый день делайте что-то, что приближает вас к цели', 'Внедряйте полезные привычки каждый день и  ставьте себе высокие цели.']))
    else:
        await update.message.reply_text('Ивините, не понимаю')
    await update.message.reply_text("Спасибо за вопрос. Хотите оценить бота?")
    return 8


async def res(update, context):
    txt = update.message.text.lower()
    if 'нет' in txt:
        await update.message.reply_text("Всего доброго!")
        return ConversationHandler.END
    if 'да' in txt:
        await update.message.reply_text("Вот:")
        return 4
    else:
        await update.message.reply_text('Извините, не понимаю')
        return ConversationHandler.END


async def fourth_response(update, context):
    await update.message.reply_text('''Теперь Вы можете оценить бота,
отправив число от 1 до 10''')
    return 5


async def fifth_response(update, context):
    r = int(update.message.text)
    name1 = update.message.from_user.username
    user1 = User()
    user1.name = name1
    user1.rating = int(r)
    context.user_data['rating'] = int(r)
    if not context.user_data['mood']:
        user1.mood = 'по умолчанию прекрасно'
    else:
        user1.mood = context.user_data['mood']
    db_sess = create_session()
    db_sess.add(user1)
    db_sess.commit()
    con = sqlite3.connect("users_tg.db")
    cur = con.cursor()
    name1 = update.message.from_user.username
    result = cur.execute("""SELECT rating FROM users""").fetchall()
    s = []
    for x in result:
        s.append(int(x[0]))
    N = sum(s) / len(s)
    await update.message.reply_text(f'''Спасибо за отзыв!
Средняя оценка бота {N} из 10''')
    return ConversationHandler.END
    

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('dialog', dialog)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_response)],
        4: [MessageHandler(filters.TEXT & ~filters.COMMAND, fourth_response)],
        5: [MessageHandler(filters.TEXT & ~filters.COMMAND, fifth_response)],
        7: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
        8: [MessageHandler(filters.TEXT & ~filters.COMMAND, res)],
        12: [MessageHandler(filters.TEXT & ~filters.COMMAND, res1)]
       },
    fallbacks=[CommandHandler('stop', stop)]
   )


async def start(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id
    await update.message.reply_text(
        '''Добрый день! Если вам нужна мотивация,
нажмите /motivation. Если красивая картинка - /picture
или можете просто поговорить с ботом, написав /dialog или задать таймер для медитации на 5 минут,
отправив /set_timer''',
        reply_markup=markup
    )

async def picture(update, context):
    chat_id = update.message.chat_id
    pic = random.choice(['img/1.jpg', 'img/2.jpg', 'img/3.jpg',
                         'img/4.jpg', 'img/5.jpg'])
    await context.bot.send_photo(update.message.chat_id, photo=open(pic, 'rb'))


async def help_command(update, context):
    con = sqlite3.connect("users_tg.db")
    cur = con.cursor()
    name1 = update.message.from_user.username
    result = cur.execute("""SELECT mood FROM users
                WHERE name = ?""", (name1, )).fetchone()
    res = cur.execute("""SELECT mood FROM users
                WHERE name = ?""", (name1, )).fetchall()
    n = len(res)
    if result:
        elem = result[0]
        chat_id = update.message.chat_id
        await update.message.reply_text(f'''Ого! Вы уже не первый раз используете этот бот ({n} раз).
Когда вы заходили, ваше настроение было {elem}. Очень ждём вас снова.''')
    await update.message.reply_text('''Если вам нужна мотивация,
нажмите /motivation. Если красивая картинка - /picture
или можете просто поговорить с ботом, написав /dialog или задать таймер для медитации на 5 минут,
отправив /set_timer''')
    con.close()
    
    
async def motivation(update, context):
    con = sqlite3.connect("users_tg.db")
    cur = con.cursor()
    name1 = update.message.from_user.username
    result = cur.execute("""SELECT mood FROM users
                WHERE name = ?""", (name1, )).fetchone()
    res = cur.execute("""SELECT mood FROM users
                WHERE name = ?""", (name1, )).fetchall()
    n = len(res)
    if result:
        elem = result[0]
        chat_id = update.message.chat_id
        await update.message.reply_text(f'''Ого! Вы уже не первый раз используете этот бот ({n} раз).
Когда вы заходили, ваше настроение было {elem}. Очень ждём вас снова.''')
    chat_id = update.message.chat_id
    a = random.choice(['Не считай дни, извлекай из них пользу',
                       'Усердно работайте, мечтайте по-крупному',
                       'Мечтатели - это спасители мира',
                       'Один из важных ключей к успеху - уверенность в себе. Важный ключ к уверенности в себе - подготовка',
                       'С новым днем приходит новая сила и новые мысли',
                       'Победа - это еще не все, главное это постоянное желание побеждать',
                       'Неудача никогда не одолеет меня, если моя решимость добиться успеха достаточно сильна'])
    await update.message.reply_text('А вот и мотивация!')
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
