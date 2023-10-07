import os
from telebot import types, TeleBot

from catalogue_functions import send_product_info, get_image_for_product, get_product_info
from product_details import get_product_page_names
from writing_questions_to_spreadsheet import write_to_spreadsheet
from database_setup import connect, create_orders_table, close_connection

shop_url = 'https://www.anvibodycare.com/shop'
API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
product_catalog_button = types.KeyboardButton("🛍️ Товари")
about_us_button = types.KeyboardButton("🏢 Про нас")
contact_us_button = types.KeyboardButton("📞 Наші контакти")
# search_button = types.KeyboardButton("🔍 Пошук")
help_button = types.KeyboardButton("👋 Допомога")
shopping_cart_button = types.KeyboardButton("🛒 Кошик")

main_menu_keyboard.row(product_catalog_button)
main_menu_keyboard.row(about_us_button)
main_menu_keyboard.row(contact_us_button)
# main_menu_keyboard.row(search_button)
main_menu_keyboard.row(help_button)
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

help_requested = {}
shopping_cart = {}


@bot.message_handler(func=lambda message: message.text == "👋 Допомога")
def provide_help(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Будь ласка, залиште ваші дані і повідомлення і ми вам зателефонуємо")
    help_requested[user_id] = True


@bot.message_handler(
    func=lambda message: help_requested.get(message.chat.id, False) and message.text != "🛍️ Product Catalog")
def handle_message(message):
    if message.chat.id in help_requested:
        write_to_spreadsheet(message)
        bot.send_message(message.chat.id, "Дякуємо! Ми скоро з Вами зв'яжемось.")
        del help_requested[message.chat.id]


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
    product_buttons = create_product_buttons()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*product_buttons)
    bot.send_message(message.chat.id, "Оберіть товар:", reply_markup=markup)


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


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def provide_product_details(call):
    product_index = int(call.data.split("_")[1])
    product_info_message = send_product_info(product_index)

    buy_button = types.InlineKeyboardButton(
        text="🛒 Купити",
        callback_data=f"buy_{product_index}" if not isinstance(get_product_info(product_index)['product price'], int)
        else f"buy2_{product_index}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(buy_button)

    image_url = get_image_for_product(product_index)
    bot.send_photo(call.message.chat.id, photo=image_url)
    bot.send_message(call.message.chat.id, product_info_message, parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(("buy_", "buy2_")))
def handle_buy_button(call):
    product_index = int(call.data.split("_")[1])
    if call.data.startswith("buy_"):
        markup = types.InlineKeyboardMarkup(row_width=3)
        weight_options = get_product_info(product_index)['weight options']

        for weight_index, weight_option in enumerate(weight_options):
            markup.add(types.InlineKeyboardButton(
                text=f"{weight_option.capitalize()} - "
                     f"{int(get_product_info(product_index)['product price'][weight_index * 2][2])}₴",
                callback_data=f'weight_{product_index}_{weight_index}'
            ))
        bot.send_message(call.message.chat.id, "Оберіть вагу:", parse_mode='HTML', reply_markup=markup)
    else:
        product_name = get_product_info(product_index)['product name']
        product_price = int(get_product_info(product_index)['product price'])

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
    product_index = int(call.data.split("_")[1])
    weight_index = int(call.data.split("_")[2])
    markup = types.InlineKeyboardMarkup(row_width=2)
    packaging_options = get_product_info(product_index)['packaging options']

    weight_price = int(get_product_info(product_index)['product price'][weight_index * 2][2])

    for packaging_index, packaging_option in enumerate(packaging_options):
        packaging_price = int(get_product_info(product_index)['product price'][packaging_index + weight_index * 2][2])
        price_difference = packaging_price - weight_price
        markup.add(types.InlineKeyboardButton(
            text=f"{packaging_option.capitalize()} {'+' + str(price_difference) + '₴' if price_difference > 0 else ''}",
            callback_data=f'packaging_{product_index}_{weight_index}_{packaging_index}'
        ))
    bot.send_message(call.message.chat.id, "Оберіть пакування:", parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("packaging_"))
def handle_packaging_button(call):
    product_index = int(call.data.split("_")[1])
    weight_index = int(call.data.split("_")[2])
    packaging_index = int(call.data.split("_")[3])

    product_name = get_product_info(product_index)['product name']
    weight_option = get_product_info(product_index)['weight options'][weight_index]
    packaging_option = get_product_info(product_index)['packaging options'][packaging_index]
    product_price = int(get_product_info(product_index)['product price'][packaging_index + weight_index * 2][2])

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
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_button = types.KeyboardButton(text="📱 Відправити контакт", request_contact=True)
    cancel_button = types.KeyboardButton(text="❌ Відмінити")
    markup.add(contact_button, cancel_button)

    bot.send_message(call.message.chat.id,
                     text='Для оформлення замовлення, натисніть "📱 Відправити контакт" '
                          'для надання контактних даних або "❌ Відмінити" для скасування.',
                     reply_markup=markup)


@bot.message_handler(content_types=['contact'])
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

    bot.send_message(user_id, "Ваше замовлення було прийнято!")


@bot.message_handler(func=lambda message: message.text == "❌ Відмінити")
def cancel_order(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Замовлення скасовано", reply_markup=main_menu_keyboard)


def create_product_buttons():
    product_buttons = []
    names = get_product_page_names(shop_url)

    for index, product_name in enumerate(names):
        product_buttons.append(
            types.InlineKeyboardButton(
                text=product_name,
                callback_data=f"product_{index}"
            )
        )

    return product_buttons


bot.infinity_polling()
