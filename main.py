import telebot
import time
import requests
import json
import os
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = '8412835956:AAEPEddVwd1dKt3VdzwUoVhbdSCipD_f31o'
WEATHER_API_KEY = 'c5b261566d137f05bbc36e67f864ee07'

bot = telebot.TeleBot(BOT_TOKEN)

# Эмодзи
emoji_ok = "✅"


def read_text_file(filename):
    """
    Читает текстовый файл из папки data
    """
    try:
        filepath = os.path.join('data', filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Файл {filename} не найден."
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"


def create_main_keyboard():
    """Создает основную клавиатуру с кнопками"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    button_start = KeyboardButton('🚀 Начать')
    button_weather = KeyboardButton('🌤️ Погода')
    button_abilities = KeyboardButton('❓ Что ты можешь?')
    button_podcasts = KeyboardButton('🎧 Подкасты')
    button_programs = KeyboardButton('💎 Программы')
    button_session = KeyboardButton('📅 Сессия')

    keyboard.add(button_start)
    keyboard.add(button_weather, button_abilities)
    keyboard.add(button_podcasts, button_programs, button_session)

    return keyboard


def get_weather(city="Москва"):
    """
    Получает данные о погоде для указанного города
    """
    try:
        # URL для запроса погоды
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return None

        # Извлекаем нужные данные
        temperature = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = {
            'temperature': temperature,
            'feels_like': feels_like,
            'description': description,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'city': city
        }

        return weather_info

    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return None


def get_weather_recommendation(weather_data):
    """
    Генерирует рекомендации на основе погоды
    """
    temp = weather_data['temperature']
    description = weather_data['description']
    wind_speed = weather_data['wind_speed']

    recommendations = []

    # Рекомендации по температуре
    if temp < -10:
        recommendations.append("🥶 Очень холодно! Оденьтесь очень тепло - пуховик, шапка, шарф, перчатки")
    elif temp < 0:
        recommendations.append("❄️ Холодно! Наденьте зимнюю куртку, шапку и шарф")
    elif temp < 10:
        recommendations.append("🍂 Прохладно! Куртка или теплый свитер будут в самый раз")
    elif temp < 20:
        recommendations.append("🌤️ Тепло! Легкая куртка или кофта")
    else:
        recommendations.append("☀️ Жарко! Можно одеваться легко")

    # Рекомендации по осадкам
    if 'дождь' in description.lower() or 'rain' in description.lower():
        recommendations.append("☔ Возьмите зонтик! Сегодня будет дождь")
    elif 'снег' in description.lower() or 'snow' in description.lower():
        recommendations.append("⛄ Идет снег! Наденьте непромокаемую обувь")

    # Рекомендации по ветру
    if wind_speed > 8:
        recommendations.append("💨 Сильный ветер! Возможно, понадобится ветровка")

    return recommendations


# Обработчик команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = read_text_file('welcome.txt')
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)


# Обработчик кнопки "Начать"
@bot.message_handler(func=lambda message: message.text == '🚀 Начать')
def start_journey(message):
    start_text = read_text_file('start.txt')
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, start_text, reply_markup=keyboard, parse_mode='HTML')


# Обработчик кнопки "Подкасты"
@bot.message_handler(func=lambda message: message.text == '🎧 Подкасты')
def show_podcasts(message):
    podcasts_text = read_text_file('podcasts.txt')
    bot.send_message(message.chat.id, podcasts_text, parse_mode='HTML')


# Обработчик кнопки "Программы"
@bot.message_handler(func=lambda message: message.text == '💎 Программы')
def show_programs(message):
    programs_text = read_text_file('programs.txt')
    bot.send_message(message.chat.id, programs_text, parse_mode='HTML')


# Обработчик кнопки "Сессия"
@bot.message_handler(func=lambda message: message.text == '📅 Сессия')
def show_session(message):
    session_text = read_text_file('session.txt')
    bot.send_message(message.chat.id, session_text, parse_mode='HTML')


# Обработчик для команды /weather или запросов о погоде
@bot.message_handler(commands=['weather'])
@bot.message_handler(func=lambda message: message.text == '🌤️ Погода' or 'погода' in message.text.lower())
def weather_handler(message):
    city = "Москва"
    bot.send_chat_action(message.chat.id, 'typing')

    weather_data = get_weather(city)

    if weather_data:
        # Формируем сообщение о погоде
        weather_text = f"🌤️ Погода в {city}:\n"
        weather_text += f"Температура: {weather_data['temperature']}°C\n"
        weather_text += f"Ощущается как: {weather_data['feels_like']}°C\n"
        weather_text += f"Описание: {weather_data['description'].capitalize()}\n"
        weather_text += f"Влажность: {weather_data['humidity']}%\n"
        weather_text += f"Ветер: {weather_data['wind_speed']} м/с\n"

        # Добавляем рекомендации
        recommendations = get_weather_recommendation(weather_data)
        if recommendations:
            weather_text += "\n💡 Рекомендации:\n"
            for rec in recommendations:
                weather_text += f"• {rec}\n"

        bot.reply_to(message, weather_text)
    else:
        bot.reply_to(message, "Извините, не удалось получить данные о погоде. Попробуйте позже.")


# Обработчик для вопроса "Что ты можешь?"
@bot.message_handler(
    func=lambda message: message.text == '❓ Что ты можешь?' or any(phrase in message.text.lower() for phrase in [
        'что ты можешь', 'что умеешь', 'твои возможности', 'чем можешь помочь'
    ]))
def what_can_you_do(message):
    # Получаем имя пользователя для персонализации
    user_name = message.from_user.first_name
    if user_name:
        greeting = f"Дорогой(ая) {user_name},"
    else:
        greeting = "Дорогая Kristina Guru of Psychology,"

    # Отправляем сообщение по частям с паузами
    first_part = bot.send_message(message.chat.id, greeting)
    time.sleep(1.5)

    second_part = bot.send_message(message.chat.id, "я могу все!")
    time.sleep(1.5)

    third_part = bot.send_message(message.chat.id, "Правда я пока только учусь=)))")
    time.sleep(1.5)

    # Добавляем информацию о погоде
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)

    weather_data = get_weather()
    if weather_data:
        weather_text = f"\n🌤️ Кстати, погода в {weather_data['city']}: {weather_data['temperature']}°C, {weather_data['description']}"

        recommendations = get_weather_recommendation(weather_data)
        if recommendations:
            main_recommendation = recommendations[0]  # Берем первую рекомендацию
            weather_text += f"\n{main_recommendation}"

        final_message = bot.send_message(message.chat.id, weather_text)
    else:
        bot.send_message(message.chat.id, "\n🌤️ Кстати, я могу рассказать о погоде! Просто нажмите кнопку 'Погода'")


# Обработчик обычных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, "Используйте кнопки ниже для навигации 👇", reply_markup=create_main_keyboard())


if __name__ == '__main__':
    # Проверяем существование папки data
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Создана папка 'data'. Добавьте в нее текстовые файлы.")

    print("Бот запущен!")
    bot.infinity_polling()