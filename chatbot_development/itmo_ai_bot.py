import telebot
from telebot import types
import json
from difflib import get_close_matches

from chatbot_development.TOKEN import TOKEN

# Загрузка данных
with open('program_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    programs = data['programs']

bot = telebot.TeleBot(TOKEN)

# Хранилище данных пользователя
user_state = {}


# Клавиатура главного меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📋 Список программ",
        "🔍 Поиск курса",
        "💡 Рекомендации",
        "ℹ️ Помощь"
    ]
    markup.add(*buttons)
    return markup


# Обработчик старта
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я помогу тебе с информацией о магистерских программах.\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )


# Обработчик списка программ
@bot.message_handler(func=lambda m: m.text == "📋 Список программ")
def show_programs(message):
    markup = types.InlineKeyboardMarkup()
    for program in programs:
        btn = types.InlineKeyboardButton(
            text=program['program_name'],
            callback_data=f"program_{program['program_name']}"
        )
        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🏛 Доступные программы магистратуры:",
        reply_markup=markup
    )


# Детали программы
@bot.callback_query_handler(func=lambda call: call.data.startswith('program_'))
def program_details(call):
    try:
        program_name = call.data.split('_')[1]
        program = next(p for p in programs if p['program_name'] == program_name)

        response = (
            f"<b>{program['program_name']}</b> ({program['program_name_en']})\n\n"
            f"📝 <b>Описание:</b> {program['description']}\n"
            f"⏳ <b>Длительность:</b> {program['duration_years']} года\n"
            f"🌐 <b>Язык:</b> {program['language'].upper()}\n"
            f"🔗 <b>Сайт:</b> {program['website_url']}\n\n"
            f"📚 <b>Основные дисциплины:</b>\n"
        )

        sample_courses = [
            course['name'] for course in
            list(program['courses_data']['courses'].values())[:5]
        ]
        response += "\n".join(f"• {course}" for course in sample_courses)

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📅 Показать по семестрам", callback_data=f"semesters_{program_name}"),
            types.InlineKeyboardButton("🔍 Поиск в программе", callback_data=f"searchin_{program_name}")
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in program_details: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте позже")


# Показать курсы по семестрам
@bot.callback_query_handler(func=lambda call: call.data.startswith('semesters_'))
def show_semesters(call):
    try:
        program_name = call.data.split('_')[1]
        program = next(p for p in programs if p['program_name'] == program_name)

        markup = types.InlineKeyboardMarkup()
        for semester in sorted(program['courses_data']['semesters'].keys()):
            btn = types.InlineKeyboardButton(
                text=f"Семестр {semester}",
                callback_data=f"semester_{program_name}_{semester}"
            )
            markup.add(btn)

        markup.add(types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"program_{program_name}"
        ))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📅 Выберите семестр программы <b>{program_name}</b>:",
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in show_semesters: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при загрузке семестров")


# Показать курсы конкретного семестра
@bot.callback_query_handler(func=lambda call: call.data.startswith('semester_'))
def show_semester_courses(call):
    try:
        _, program_name, semester = call.data.split('_')
        program = next(p for p in programs if p['program_name'] == program_name)

        courses = program['courses_data']['semesters'].get(semester, [])

        response = f"📚 <b>Курсы {program_name}, семестр {semester}:</b>\n\n"
        for course in courses:
            response += f"• {course['name']} ({course['credits']} кредитов, {course['hours']} часов)\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="⬅️ К списку семестров",
            callback_data=f"semesters_{program_name}"
        ))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in show_semester_courses: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при загрузке курсов")


# Поиск курсов
@bot.message_handler(func=lambda m: m.text == "🔍 Поиск курса")
def ask_search_query(message):
    msg = bot.send_message(
        message.chat.id,
        "🔍 Введите название курса или ключевые слова:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, process_search)


def process_search(message):
    query = message.text.lower()
    results = []

    for program in programs:
        for course in program['courses_data']['courses'].values():
            if query in course['name'].lower():
                results.append((program['program_name'], course))

    if results:
        response = "🔍 <b>Результаты поиска:</b>\n\n"
        for program_name, course in results[:5]:
            response += (
                f"📚 <b>{course['name']}</b>\n"
                f"🏛 <i>{program_name}</i>\n"
                f"📅 Семестр: {course['semester']} | 🎓 Кредиты: {course['credits']}\n\n"
            )
    else:
        all_courses = [
            course['name'] for program in programs
            for course in program['courses_data']['courses'].values()
        ]
        matches = get_close_matches(query, all_courses, n=3, cutoff=0.6)

        if matches:
            response = "❌ Точных совпадений не найдено. Возможно, вы искали:\n\n"
            response += "\n".join(f"• {match}" for match in matches)
        else:
            response = "❌ Ничего не найдено. Попробуйте изменить запрос."

    bot.send_message(
        message.chat.id,
        response,
        parse_mode='HTML',
        reply_markup=main_menu()
    )


# Рекомендательная система
@bot.message_handler(func=lambda m: m.text == "💡 Рекомендации")
def ask_program_for_recommendations(message):
    markup = types.InlineKeyboardMarkup()
    for program in programs:
        btn = types.InlineKeyboardButton(
            program['program_name'],
            callback_data=f"rec_program_{program['program_name']}"
        )
        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "📊 Для рекомендации курсов выберите программу:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('rec_program_'))
def ask_background(call):
    try:
        program_name = call.data.split('_')[2]
        user_state[call.message.chat.id] = {'program': program_name}

        bot.send_message(
            call.message.chat.id,
            f"📝 Опишите ваш опыт и интересы (например: 'Имею опыт в Python и анализе данных'):",
            reply_markup=types.ReplyKeyboardRemove()
        )

        bot.register_next_step_handler_by_chat_id(
            call.message.chat.id,
            process_recommendations
        )
    except Exception as e:
        print(f"Error in ask_background: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")


def process_recommendations(message):
    try:
        chat_id = message.chat.id
        background = message.text.lower()

        if chat_id not in user_state or 'program' not in user_state[chat_id]:
            bot.send_message(
                chat_id,
                "❌ Не удалось определить программу. Попробуйте снова.",
                reply_markup=main_menu()
            )
            return

        program_name = user_state[chat_id]['program']
        program = next(p for p in programs if p['program_name'] == program_name)

        # Улучшенная система рекомендаций
        recommendations = {
            'python': ['Программирование на Python', 'Разработка веб-приложений (Python Backend)'],
            'анализ данн': ['Математическая статистика', 'Прикладной анализ временных рядов'],
            'машинн': ['Основы машинного обучения', 'Продвинутое МО (Python)'],
            'менеджмент': ['Управление проектами в Data Science', 'Продуктовый менеджмент'],
            'данн': ['Инженерия данных', 'Базы данных'],
            'глубок': ['Основы глубокого обучения', 'Глубокие генеративные модели'],
            'естествен': ['Обработка естественного языка', 'Технологии обработки естественного языка']
        }

        matched_courses = set()
        for keyword, courses in recommendations.items():
            if keyword in background:
                matched_courses.update(courses)

        # Если ничего не найдено, предлагаем базовые курсы
        if not matched_courses:
            matched_courses = {
                course['name'] for course in
                list(program['courses_data']['courses'].values())[:5]
            }

        response = (
            f"🎓 <b>Рекомендации для программы {program_name}</b>\n"
            f"📌 На основе вашего опыта: <i>{background}</i>\n\n"
            "Мы рекомендуем следующие курсы:\n"
        )
        response += "\n".join(f"• {course}" for course in matched_courses)

        bot.send_message(
            chat_id,
            response,
            parse_mode='HTML',
            reply_markup=main_menu()
        )

        # Очищаем состояние
        if chat_id in user_state:
            del user_state[chat_id]

    except Exception as e:
        print(f"Error in process_recommendations: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при формировании рекомендаций",
            reply_markup=main_menu()
        )


@bot.message_handler(func=lambda m: m.text == "ℹ️ Помощь")
def show_help(message):
    help_text = (
        "🤖 <b>Помощь по боту</b>\n\n"
        "Я помогаю получить информацию о магистерских программах ИТМО.\n\n"
        "📋 <b>Список программ</b> - просмотр всех доступных программ\n"
        "🔍 <b>Поиск курса</b> - поиск курсов по названию или ключевым словам\n"
        "💡 <b>Рекомендации</b> - персональные рекомендации курсов\n\n"
        "Для возврата в главное меню используйте команду /start\n"
        "Если возникли проблемы, напишите @ваш_username"
    )

    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='HTML',
        reply_markup=main_menu()
    )


if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()