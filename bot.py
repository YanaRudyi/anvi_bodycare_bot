from telebot import types

from bot_cfg import bot
from catalogue_functions import build_product_info
from database_setup import connect, close_connection, create_orders_table
from handler.category_handler import create_category_buttons
from handler.product_handler import product_identifier_map
from product_details import parse_product_page
from writing_questions_to_spreadsheet import write_to_spreadsheet, write_order_to_spreadsheet

shop_url = 'https://www.anvibodycare.com/shop'

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
product_catalog_button = types.KeyboardButton("🛍️ Товари")
about_us_button = types.KeyboardButton("🏢 Про нас")
contact_us_button = types.KeyboardButton("📞 Наші контакти")
search_button = types.KeyboardButton("🔍 Пошук")
help_button = types.KeyboardButton("👋 Допомога")
shopping_cart_button = types.KeyboardButton("🛒 Кошик")

main_menu_keyboard.row(product_catalog_button, about_us_button)
main_menu_keyboard.row(contact_us_button, help_button)
main_menu_keyboard.row(shopping_cart_button)


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Вітаємо в Anvi! Як ми можемо допомогти вам сьогодні?",
                     reply_markup=main_menu_keyboard)


create_orders_table()

insert_order_query = """
INSERT INTO orders (user_id, products, contact_name, contact_phone)
VALUES (%s, %s, %s, %s);
"""

shopping_cart = {}
help_info = {}
order_process_started = {}


@bot.message_handler(func=lambda message: message.text == "👋 Допомога")
def provide_help(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button = types.KeyboardButton(text="📱 Відправити контакт", request_contact=True)
    cancel_button = types.KeyboardButton(text="❌ Відмінити")
    markup.add(contact_button, cancel_button)
    help_info[user_id] = {}
    help_info[user_id]['help_requested'] = True
    bot.send_message(user_id, "Для подачі заяви про допомогу, натисніть \"📱 Відправити контакт\" для надання "
                              "контактних даних або \"❌ Відмінити\" для скасування.",
                     reply_markup=markup)


@bot.message_handler(content_types=['contact'],
                     func=lambda message: help_info.get(message.from_user.id, False))
def handle_support_contact(message):
    user_id = message.from_user.id
    help_info[user_id]['first_name'] = message.contact.first_name
    help_info[user_id]['phone_number'] = message.contact.phone_number
    bot.send_message(user_id, "Залиште, будь ласка, повідомлення")


@bot.message_handler(content_types=['text'],
                     func=lambda message: help_info.get(message.chat.id, False) and message.text != "❌ Відмінити")
def handle_support_message(message):
    user_id = message.from_user.id
    help_info[user_id]['message'] = message.text
    write_to_spreadsheet(help_info[user_id])
    del help_info[user_id]
    bot.send_message(user_id, "Дякуємо за ваш запит. Ми зв'яжемося з Вами найближчим часом!",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda message: message.text == "🔍 Пошук")
def provide_search(message):
    bot.send_message(message.chat.id, "Введіть параметри запиту:")


@bot.message_handler(func=lambda message: message.text == "📞 Наші контакти")
def provide_contact_info(message):
    bot.send_message(message.chat.id, "Ви можете зв'язатись з нами через anvibodycare@gmail.com.")


@bot.message_handler(func=lambda message: message.text == "🏢 Про нас")
def provide_about_us_info(message):
    bot.send_message(message.chat.id, "Ми Anvi. Турбота про ваше тіло – наша головна мета!")


@bot.message_handler(func=lambda message: message.text == "🛍️ Товари")
def show_product_catalog(message):
    category_buttons = create_category_buttons()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*category_buttons)
    bot.send_message(message.chat.id, "Оберіть категорію:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🛒 Кошик")
def show_shopping_cart(message):
    user_id = message.chat.id
    if user_id in shopping_cart and len(shopping_cart[user_id]) > 0:
        cart_text = "🛒 Ваш кошик:\n"
        total_price = 0

        for item in shopping_cart[user_id]:
            product_name = item.get('product name')
            weight_option = item.get('weight option')
            packaging_option = item.get('packaging option')
            product_price = item.get('product price', 0)
            if weight_option and packaging_option:
                cart_text += \
                    f"- <b>{product_name}</b> ({weight_option}, {packaging_option}): <b>{product_price} грн\n</b>"
            else:
                cart_text += f"- <b>{product_name}</b>: {product_price} грн\n"
            total_price += product_price

        cart_text += f"\n🚚 Загальна сума: {total_price} грн"

        markup = types.InlineKeyboardMarkup()
        order_button = types.InlineKeyboardButton("🛍️ Оформити замовлення", callback_data="order")
        clear_cart_button = types.InlineKeyboardButton("🗑️ Очистити кошик", callback_data="clear_cart")
        markup.add(order_button, clear_cart_button)

        bot.send_message(user_id, cart_text, parse_mode='HTML', reply_markup=markup)
    else:
        bot.send_message(user_id, '🛒 Кошик порожній')


@bot.callback_query_handler(func=lambda call: call.data.startswith(("buy_", "buy2_")))
def handle_buy_button(call):
    product_hash = int(call.data.split("_")[1])
    product = product_identifier_map.get(product_hash)
    product_info = build_product_info(parse_product_page(product.url))
    product_name = product_info['product name']
    if call.data.startswith("buy_"):
        markup = types.InlineKeyboardMarkup(row_width=3)
        weight_options = product_info['weight options']

        for weight_index, weight_option in enumerate(weight_options):
            markup.add(types.InlineKeyboardButton(
                text=f"{weight_option.capitalize()} - "
                     f"{int(product_info['product price'][weight_index * 2][2])}₴",
                callback_data=f'weight_{product_hash}_{weight_index}'
            ))
        bot.send_message(call.message.chat.id, f"Оберіть вагу для товару <b>\"{product_name}\"</b>:",
                         parse_mode='HTML', reply_markup=markup)
    else:
        product_price = int(product_info['product price'])

        user_id = call.from_user.id

        if user_id not in shopping_cart:
            shopping_cart[user_id] = []

        shopping_cart[user_id].append({
            'product name': product_name,
            'product price': product_price
        })

        bot.send_message(call.message.chat.id, f"Товар \"<b>{product_name}</b>\" додано до кошика", parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith("weight_"))
def handle_weight_button(call):
    product_hash = int(call.data.split("_")[1])
    weight_index = int(call.data.split("_")[2])
    product = product_identifier_map.get(product_hash)
    product_info = build_product_info(parse_product_page(product.url))
    markup = types.InlineKeyboardMarkup(row_width=2)
    product_name = product_info['product name']
    packaging_options = product_info['packaging options']

    weight_price = int(product_info['product price'][weight_index * 2][2])

    for packaging_index, packaging_option in enumerate(packaging_options):
        packaging_price = int(product_info['product price'][packaging_index + weight_index * 2][2])
        price_difference = packaging_price - weight_price
        markup.add(types.InlineKeyboardButton(
            text=f"{packaging_option.capitalize()} {'+' + str(price_difference) + '₴' if price_difference > 0 else ''}",
            callback_data=f'packaging_{product_hash}_{weight_index}_{packaging_index}'
        ))
    bot.send_message(call.message.chat.id, f"Оберіть пакування для товару <b>\"{product_name}\"</b>:",
                     parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("packaging_"))
def handle_packaging_button(call):
    product_hash = int(call.data.split("_")[1])
    weight_index = int(call.data.split("_")[2])
    packaging_index = int(call.data.split("_")[3])
    product = product_identifier_map.get(product_hash)
    product_info = build_product_info(parse_product_page(product.url))

    product_name = product_info['product name']
    weight_option = product_info['weight options'][weight_index]
    packaging_option = product_info['packaging options'][packaging_index]
    product_price = int(product_info['product price'][packaging_index + weight_index * 2][2])

    user_id = call.from_user.id

    if user_id not in shopping_cart:
        shopping_cart[user_id] = []

    shopping_cart[user_id].append({
        'product name': product_name,
        'weight option': weight_option,
        'packaging option': packaging_option,
        'product price': product_price
    })

    bot.send_message(call.message.chat.id, f"Товар \"<b>{product_name}</b>\" додано до кошика", parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def handle_clear_cart(call):
    user_id = call.from_user.id
    if user_id in shopping_cart:
        del shopping_cart[user_id]
    bot.send_message(user_id, '🗑️ Кошик очищено')


@bot.callback_query_handler(func=lambda call: call.data == "order")
def start_ordering_process(call):
    user_id = call.from_user.id
    if user_id in shopping_cart and len(shopping_cart[user_id]) > 0:
        order_process_started[user_id] = True

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        contact_button = types.KeyboardButton(text="📱 Відправити контакт", request_contact=True)
        cancel_button = types.KeyboardButton(text="❌ Відмінити")
        markup.add(contact_button, cancel_button)

        bot.send_message(call.message.chat.id,
                         text='Для оформлення замовлення, натисніть "📱 Відправити контакт" '
                              'для надання контактних даних або "❌ Відмінити" для скасування.',
                         reply_markup=markup)
    else:
        bot.send_message(user_id, '❗Помилка: Ваш кошик порожній')


@bot.message_handler(content_types=['contact'], func=lambda message: order_process_started.get(message.from_user.id, False))
def handle_order_contact(message):
    user_id = message.from_user.id
    contact_name = message.contact.first_name
    contact_phone = message.contact.phone_number

    total_price = 0
    for item in shopping_cart[user_id]:
        total_price += item.get('product price', 0)

    write_order_to_spreadsheet({
        'first_name': contact_name,
        'phone_number': contact_phone,
        'message': str(total_price)
    }, shopping_cart[user_id])

    del shopping_cart[user_id], order_process_started[user_id]

    bot.send_message(user_id, "Ваше замовлення було прийнято! Ми зв'яжемося з Вами найближчим часом.", reply_markup=main_menu_keyboard)


@bot.message_handler(content_types=['contact'],
                     func=lambda message: order_process_started.get(message.from_user.id, False))
def handle_contact(call):
    conn = connect()
    cursor = conn.cursor()
    user_id = call.from_user.id
    contact_name = call.contact.first_name
    contact_phone = call.contact.phone_number

    user_shopping_cart = []
    for item in shopping_cart[user_id]:
        user_shopping_cart.extend(item.values())
    user_shopping_cart = ', '.join(map(str, user_shopping_cart))

    cursor.execute(insert_order_query, (user_id, user_shopping_cart, contact_name, contact_phone))
    conn.commit()
    cursor.close()
    close_connection(conn)

    del shopping_cart[user_id], order_process_started[user_id]


@bot.message_handler(func=lambda message: message.text == "❌ Відмінити")
def handle_cancel_button(call):
    user_id = call.chat.id
    if user_id in order_process_started:
        del order_process_started[user_id]
        bot.send_message(user_id, "Замовлення скасовано", reply_markup=main_menu_keyboard)
    if user_id in help_info:
        del help_info[user_id]
        bot.send_message(user_id, "Заява про отримання допомоги скасована", reply_markup=main_menu_keyboard)


bot.infinity_polling()
