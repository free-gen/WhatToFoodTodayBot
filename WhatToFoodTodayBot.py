import telebot
import json
import os
import random
from telebot import types

# Токен вашего бота (получите у @BotFather)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл для хранения данных пользователей
DATA_FILE = "user_data.json"

# Глобальные переменные для хранения состояния выдачи
user_random_states = {}

# Текстовые константы
TEXT_MAIN_MENU = "Главное меню:"
TEXT_WELCOME = (
    "Привет! Я бот для ответа на вопрос - Что приготовить?.\n\n"
    "Поддерживается два списка блюд:\n"
    "• Простые - обычное повседневное хрючево\n"
    "• Особые - для особых случаев\n\n"
    "Я помогу с выбором блюда из любого списка.\n"
    "Используйте кнопки ниже для управления ботом."
)
TEXT_EMPTY_LIST = "Ваш список пуст."
TEXT_ADD_FIRST_ITEM = "Добавить первый элемент"
TEXT_ADD_ITEM = "Добавить элемент"
TEXT_REMOVE_ITEM = "Удалить элемент"
TEXT_CLEAR_LIST = "Очистить список"
TEXT_BACK = "Назад"
TEXT_RANDOM_CHOICE = "🎲 **{}**"
TEXT_ITEM_ADDED = "Добавлено: **{}**\nТеперь в списке: {} элементов"
TEXT_ITEM_EMPTY = "Элемент не может быть пустым!"
TEXT_LIST_CLEARED = "Список очищен!"
TEXT_LIST_ALREADY_EMPTY = "Список уже пуст!"
TEXT_ITEM_REMOVED = "Удалено: {}"
TEXT_USE_BUTTONS = "Используйте кнопки для управления ботом!"
TEXT_CURRENT_ITEMS_COUNT = "Сейчас в списке {} элементов"
TEXT_LIST_EMPTY_STATUS = "Список пуст"
TEXT_SELECT_ACTION = "Выберите действие:"
TEXT_SELECT_ITEM_TO_REMOVE = "Выберите элемент для удаления:"
TEXT_ENTER_NEW_ITEM = "Введите новый элемент для списка:"
TEXT_YOUR_LIST = "Ваш список:\n\n{}"
TEXT_LIST_EMPTY_ADD = "Ваш список пуст. Нажмите 'Дополнить список', чтобы добавить элементы."
TEXT_RANDOM_EMPTY_LIST = "Ваш список пуст. Сначала добавьте элементы через 'Дополнить список'."

# Кнопки главного меню
BTN_EDIT_LIST = "Дополнить список"
BTN_RANDOM_DAILY = "Что-нибудь попроще"
BTN_RANDOM_SPECIAL = "Что-то особенное"
BTN_SHOW_LIST = "Показать список"

# Базовые списки блюд
DAILY_DISHES = [
    "Пицца", 
    "Плов", 
    "Картошка в духовке", 
    "Картошка тушеная с мясом",
    "Жареная картошка", 
    "Рагу", 
    "Спагетти с зажаркой", 
    "Спагетти с котлетами",
    "Спагетти с сосисками", 
    "Спагетти с отбивными", 
    "Макароны с зажаркой",
    "Макароны с котлетами", 
    "Макароны с сосисками", 
    "Пюре с зажаркой",
    "Пюре с котлетами", 
    "Пюре с сосисками", 
    "Пюре с отбивными", 
    "Пюре с котлетами и жареной капустой", 
    "Борщ", 
    "Суп с курицей"
]

SPECIAL_DISHES = [
    "Паста карбонара",
    "Картошка по деревенски",
    "Салат цезарь",
    "Окрошка",
    "Стейки"
]

# Загружаем данные пользователей
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Сохраняем данные пользователей
def save_user_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Миграция старых данных
def migrate_user_data(data):
    migrated = False
    for user_id, user_data in data.items():
        # Если данные пользователя - это список (старый формат)
        if isinstance(user_data, list):
            # Преобразуем в новый формат
            data[user_id] = {
                "daily_dishes": user_data,
                "special_dishes": SPECIAL_DISHES.copy()
            }
            migrated = True
    if migrated:
        save_user_data(data)
    return data

# Получаем или создаем список для пользователя
def get_user_list(user_id):
    data = load_user_data()
    
    # Мигрируем данные если нужно
    data = migrate_user_data(data)
    
    if str(user_id) not in data:
        # Инициализируем с базовыми списками
        data[str(user_id)] = {
            "daily_dishes": DAILY_DISHES.copy(),
            "special_dishes": SPECIAL_DISHES.copy()
        }
        save_user_data(data)
    return data[str(user_id)]

# Обновляем список пользователя
def update_user_list(user_id, daily_dishes=None, special_dishes=None):
    data = load_user_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    
    if daily_dishes is not None:
        data[str(user_id)]["daily_dishes"] = daily_dishes
    if special_dishes is not None:
        data[str(user_id)]["special_dishes"] = special_dishes
    
    save_user_data(data)

# Создаем главное меню
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        BTN_RANDOM_DAILY,
        BTN_RANDOM_SPECIAL, 
        BTN_EDIT_LIST,
        BTN_SHOW_LIST
    ]
    keyboard.add(*[types.KeyboardButton(btn) for btn in buttons])
    return keyboard

# Создаем форматированный текст списка
def format_list(items):
    return "\n".join([f"• {item}" for item in items])

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    get_user_list(user_id)  # Инициализируем данные пользователя
    
    bot.send_message(message.chat.id, TEXT_WELCOME, 
                     reply_markup=create_main_keyboard())

# Обработчик кнопки "Показать список"
@bot.message_handler(func=lambda message: message.text == BTN_SHOW_LIST)
def show_list(message):
    user_id = message.from_user.id
    user_data = get_user_list(user_id)
    
    daily_list = user_data.get("daily_dishes", [])
    special_list = user_data.get("special_dishes", [])
    
    if not daily_list and not special_list:
        bot.send_message(message.chat.id, TEXT_LIST_EMPTY_ADD)
    else:
        list_text = "**Простые блюда:**\n"
        list_text += format_list(daily_list) if daily_list else TEXT_EMPTY_LIST
        
        list_text += "\n\n**Особые блюда:**\n"
        list_text += format_list(special_list) if special_list else TEXT_EMPTY_LIST
        
        bot.send_message(message.chat.id, list_text, parse_mode='Markdown')

# Обработчик кнопки "Простое блюдо"
@bot.message_handler(func=lambda message: message.text == BTN_RANDOM_DAILY)
def random_daily_choice(message):
    user_id = message.from_user.id
    user_data = get_user_list(user_id)
    
    # Безопасное получение списка
    if isinstance(user_data, dict):
        daily_dishes = user_data.get("daily_dishes", [])
    else:
        # Если все еще старый формат (на всякий случай)
        daily_dishes = user_data if isinstance(user_data, list) else []
    
    if not daily_dishes:
        bot.send_message(message.chat.id, TEXT_RANDOM_EMPTY_LIST)
        return
    
    # Инициализируем или сбрасываем состояние для пользователя
    if user_id not in user_random_states or user_random_states[user_id].get('list_type') != 'daily':
        shuffled_dishes = daily_dishes.copy()
        random.shuffle(shuffled_dishes)
        user_random_states[user_id] = {
            'list_type': 'daily',
            'shuffled_list': shuffled_dishes,
            'current_index': 0
        }
    
    state = user_random_states[user_id]
    
    # Если дошли до конца списка, перемешиваем заново
    if state['current_index'] >= len(state['shuffled_list']):
        shuffled_dishes = daily_dishes.copy()
        random.shuffle(shuffled_dishes)
        state['shuffled_list'] = shuffled_dishes
        state['current_index'] = 0
    
    # Получаем только одно текущее блюдо
    chosen = state['shuffled_list'][state['current_index']]
    state['current_index'] += 1
    
    # Отправляем только одно сообщение
    bot.send_message(message.chat.id, TEXT_RANDOM_CHOICE.format(chosen), parse_mode='Markdown')

# Обработчик кнопки "Особое блюдо"
@bot.message_handler(func=lambda message: message.text == BTN_RANDOM_SPECIAL)
def random_special_choice(message):
    user_id = message.from_user.id
    user_data = get_user_list(user_id)
    
    # Безопасное получение списка
    if isinstance(user_data, dict):
        special_dishes = user_data.get("special_dishes", [])
    else:
        special_dishes = []
    
    if not special_dishes:
        bot.send_message(message.chat.id, TEXT_RANDOM_EMPTY_LIST)
        return
    
    # Инициализируем или сбрасываем состояние для пользователя
    if user_id not in user_random_states or user_random_states[user_id].get('list_type') != 'special':
        shuffled_dishes = special_dishes.copy()
        random.shuffle(shuffled_dishes)
        user_random_states[user_id] = {
            'list_type': 'special',
            'shuffled_list': shuffled_dishes,
            'current_index': 0
        }
    
    state = user_random_states[user_id]
    
    # Если дошли до конца списка, перемешиваем заново
    if state['current_index'] >= len(state['shuffled_list']):
        shuffled_dishes = special_dishes.copy()
        random.shuffle(shuffled_dishes)
        state['shuffled_list'] = shuffled_dishes
        state['current_index'] = 0
    
    # Получаем только одно текущее блюдо
    chosen = state['shuffled_list'][state['current_index']]
    state['current_index'] += 1
    
    # Отправляем только одно сообщение
    bot.send_message(message.chat.id, TEXT_RANDOM_CHOICE.format(chosen), parse_mode='Markdown')

# Обработчик кнопки "Дополнить список"
@bot.message_handler(func=lambda message: message.text == BTN_EDIT_LIST)
def edit_list(message):
    user_id = message.from_user.id
    user_data = get_user_list(user_id)
    
    # Безопасное получение списков
    if isinstance(user_data, dict):
        daily_dishes = user_data.get("daily_dishes", [])
        special_dishes = user_data.get("special_dishes", [])
    else:
        daily_dishes = user_data if isinstance(user_data, list) else []
        special_dishes = []
    
    # Создаем клавиатуру для редактирования
    keyboard = types.InlineKeyboardMarkup()
    
    keyboard.add(types.InlineKeyboardButton("Добавить простое блюдо", callback_data="add_daily"))
    keyboard.add(types.InlineKeyboardButton("Добавить особое блюдо", callback_data="add_special"))
    
    if daily_dishes or special_dishes:
        keyboard.add(types.InlineKeyboardButton(TEXT_CLEAR_LIST, callback_data="clear_lists"))
        keyboard.add(types.InlineKeyboardButton(TEXT_REMOVE_ITEM, callback_data="remove_item"))
    
    keyboard.add(types.InlineKeyboardButton(TEXT_BACK, callback_data="back_to_main"))
    
    daily_count = len(daily_dishes)
    special_count = len(special_dishes)
    list_status = f"Простых: {daily_count} | Особых: {special_count}"
    
    bot.send_message(message.chat.id, 
                    f"{list_status}\n\n{TEXT_SELECT_ACTION}",
                    reply_markup=keyboard)

# Обработчик callback-ов от inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    user_data = get_user_list(user_id)
    
    if call.data == "clear_lists":
        update_user_list(user_id, [], [])
        bot.answer_callback_query(call.id, TEXT_LIST_CLEARED)
        edit_list(call.message)
    
    elif call.data == "add_daily":
        msg = bot.send_message(call.message.chat.id, TEXT_ENTER_NEW_ITEM)
        bot.register_next_step_handler(msg, process_add_daily_item)
    
    elif call.data == "add_special":
        msg = bot.send_message(call.message.chat.id, TEXT_ENTER_NEW_ITEM)
        bot.register_next_step_handler(msg, process_add_special_item)
    
    elif call.data == "remove_item":
        user_data = get_user_list(user_id)
        
        # Безопасное получение списков
        if isinstance(user_data, dict):
            daily_dishes = user_data.get("daily_dishes", [])
            special_dishes = user_data.get("special_dishes", [])
        else:
            daily_dishes = user_data if isinstance(user_data, list) else []
            special_dishes = []
        
        if not daily_dishes and not special_dishes:
            bot.answer_callback_query(call.id, TEXT_LIST_ALREADY_EMPTY)
            return
        
        # Создаем клавиатуру для удаления элементов
        keyboard = types.InlineKeyboardMarkup()
        
        # Добавляем простые блюда
        for i, item in enumerate(daily_dishes):
            keyboard.add(types.InlineKeyboardButton(f" {item}", 
                                                  callback_data=f"remove_daily_{i}"))
        
        # Добавляем особые блюда
        for i, item in enumerate(special_dishes):
            keyboard.add(types.InlineKeyboardButton(f" {item}", 
                                                  callback_data=f"remove_special_{i}"))
        
        keyboard.add(types.InlineKeyboardButton(TEXT_BACK, callback_data="back_to_edit"))
        
        bot.edit_message_text(TEXT_SELECT_ITEM_TO_REMOVE,
                             call.message.chat.id,
                             call.message.message_id,
                             reply_markup=keyboard)
    
    elif call.data.startswith("remove_daily_"):
        index = int(call.data.split("_")[2])
        user_data = get_user_list(user_id)
        
        # Безопасное получение списка
        if isinstance(user_data, dict):
            daily_dishes = user_data.get("daily_dishes", [])
        else:
            daily_dishes = user_data if isinstance(user_data, list) else []
        
        if 0 <= index < len(daily_dishes):
            removed_item = daily_dishes.pop(index)
            update_user_list(user_id, daily_dishes=daily_dishes)
            bot.answer_callback_query(call.id, TEXT_ITEM_REMOVED.format(removed_item))
            edit_list(call.message)
    
    elif call.data.startswith("remove_special_"):
        index = int(call.data.split("_")[2])
        user_data = get_user_list(user_id)
        
        # Безопасное получение списка
        if isinstance(user_data, dict):
            special_dishes = user_data.get("special_dishes", [])
        else:
            special_dishes = []
        
        if 0 <= index < len(special_dishes):
            removed_item = special_dishes.pop(index)
            update_user_list(user_id, special_dishes=special_dishes)
            bot.answer_callback_query(call.id, TEXT_ITEM_REMOVED.format(removed_item))
            edit_list(call.message)
    
    elif call.data == "back_to_edit":
        edit_list(call.message)
    
    elif call.data == "back_to_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 
                        TEXT_MAIN_MENU, 
                        reply_markup=create_main_keyboard())

# Обработчик добавления простого блюда
def process_add_daily_item(message):
    user_id = message.from_user.id
    new_item = message.text.strip()
    
    if new_item:
        user_data = get_user_list(user_id)
        
        # Безопасное получение списка
        if isinstance(user_data, dict):
            daily_dishes = user_data.get("daily_dishes", [])
        else:
            daily_dishes = user_data if isinstance(user_data, list) else []
        
        daily_dishes.append(new_item)
        update_user_list(user_id, daily_dishes=daily_dishes)
        
        bot.send_message(message.chat.id, 
                        TEXT_ITEM_ADDED.format(new_item, len(daily_dishes)),
                        parse_mode='Markdown',
                        reply_markup=create_main_keyboard())
    else:
        bot.send_message(message.chat.id, 
                        TEXT_ITEM_EMPTY,
                        reply_markup=create_main_keyboard())

# Обработчик добавления особого блюда
def process_add_special_item(message):
    user_id = message.from_user.id
    new_item = message.text.strip()
    
    if new_item:
        user_data = get_user_list(user_id)
        
        # Безопасное получение списка
        if isinstance(user_data, dict):
            special_dishes = user_data.get("special_dishes", [])
        else:
            special_dishes = []
        
        special_dishes.append(new_item)
        update_user_list(user_id, special_dishes=special_dishes)
        
        bot.send_message(message.chat.id, 
                        TEXT_ITEM_ADDED.format(new_item, len(special_dishes)),
                        parse_mode='Markdown',
                        reply_markup=create_main_keyboard())
    else:
        bot.send_message(message.chat.id, 
                        TEXT_ITEM_EMPTY,
                        reply_markup=create_main_keyboard())

# Обработчик текстовых сообщений (на случай, если пользователь просто напишет текст)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text not in [BTN_EDIT_LIST, BTN_RANDOM_DAILY, BTN_RANDOM_SPECIAL, BTN_SHOW_LIST]:
        bot.send_message(message.chat.id, 
                        TEXT_USE_BUTTONS,
                        reply_markup=create_main_keyboard())

# Запуск бота
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Ошибка: BOT_TOKEN не установлен!")
        print("Установите переменную окружения BOT_TOKEN")
        exit(1)
        
    print("Бот запущен...")
    bot.infinity_polling()