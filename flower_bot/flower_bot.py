import telebot 
from telebot import types
import logging
import psycopg2
from consts import token
from models import Flower, session, User, Order

bot = telebot.TeleBot(token)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет, я бот цветочного магазина!')

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, 'Как я могу вам помочь?')

@bot.message_handler(commands=['show_flowers'])
def show_flowers(message):
    flowers = session.query(Flower).all()
    for flower in flowers:
        bot.reply_to(message, f'Название: {flower.name}\nСтоимость: {flower.cost}\nКоличество: {flower.quantity}\nПоставщик: {flower.supplier}')

@bot.message_handler(commands=['order'])
def order(message):
    markup = types.InlineKeyboardMarkup()
    flowers = session.query(Flower).all()
    for flower in flowers:
        markup.add(types.InlineKeyboardButton(f'{flower.name}: {flower.cost}', callback_data=f'flower_{flower.id}'))
    bot.reply_to(message, 'Выберите цветы:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('flower_'))
def handle_order(call):
    flower_id = int(call.data.split('_')[1])
    flower = session.query(Flower).get(flower_id)
    order = Order(user_id=call.from_user.id, flower_id=flower_id, quantity=1)
    session.add(order)
    session.commit()
    bot.reply_to(call.message, f'Вы заказали {flower.name} по цене {flower.cost}')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['add_flower'])
def add_flower(message):
    admin_ids = session.query(User.id).filter(User.role == 'admin').all()
    if message.from_user.id in admin_ids:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        message.reply_text('Введите название цветка:')
        bot.register_next_step_handler(message, add_flower_name, message.from_user.id)
    else:
        message.reply_text('Only administrators can add flowers.')

def add_flower_name(message, user_id):
    flower_name = message.text.strip()
    if flower_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        message.reply_text('Введите стоимость цветка:')
        bot.register_next_step_handler(message, add_flower_cost, flower_name, user_id)
    else:
        message.reply_text('Название цветка не может быть пустым.')

def add_flower_cost(message, flower_name, user_id):
    flower_cost = message.text.strip()
    if flower_cost:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        message.reply_text('Введите количество цветов:')
        bot.register_next_step_handler(message, add_flower_quantity, flower_name, flower_cost, user_id)
    else:
        message.reply_text('Стоимость цветка не может быть пустой.')

def add_flower_quantity(message, flower_name, flower_cost, user_id):
    flower_quantity = message.text.strip()
    if flower_quantity:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        message.reply_text('Введите имя поставщика:')
        bot.register_next_step_handler(message, add_flower_supplier, flower_name, flower_cost, flower_quantity, user_id)
    else:
        message.reply_text('Количество цветов не может быть пустым.')

def add_flower_supplier(message, flower_name, flower_cost, flower_quantity, user_id):
    flower_supplier = message.text.strip()
    if flower_supplier:
        flower = Flower(name=flower_name, cost=flower_cost, quantity=flower_quantity, supplier=flower_supplier)
        session.add(flower)
        session.commit()
        message.reply_text(f'Flower {flower_name} added to the database.')
    else:
        message.reply_text('Имя поставщика не может быть пустым.')

def main() -> None:
    bot.polling()

if __name__ == '__main__':
    main()