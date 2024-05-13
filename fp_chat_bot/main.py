import telebot
import requests

TOKEN = ''
bot = telebot.TeleBot(TOKEN)
user_names = {}
flg_weath = False

def log_event(event):
    with open("log.txt", "a") as log_file:
        log_file.write(event + "\n")

def get_weather(city):
    api_key = ''
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric', 
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']

            return f"Погода в городе {city}: {description}, температура: {temperature}°C"
        else:
            return "Не удалось получить информацию о погоде. Попробуйте еще раз."

    except Exception as e:
        return f"Произошла ошибка: {e}"


def get_currency_exchange_rates():
    app_id = ''
    base_url = 'https://open.er-api.com/v6/latest/RUB'

    try:
        response = requests.get(base_url, params={'app_id': app_id})
        data = response.json()

        if response.status_code == 200:
            rates = data.get('rates', {})

            usd_rate = 1/rates.get('USD', 'N/A')
            eur_rate = 1/rates.get('EUR', 'N/A')
            gbp_rate = 1/rates.get('CNY', 'N/A')

            return f"Курс валют к рублю:\nUSD: {usd_rate}\nEUR: {eur_rate}\nCNY: {gbp_rate}"
        else:
            return "Не удалось получить информацию о валютах. Попробуйте еще раз."

    except Exception as e:
        return f"Произошла ошибка: {e}"


def get_chuck_norris_joke():
    response = requests.get("https://api.chucknorris.io/jokes/random")
    joke = response.json()["value"]
    return joke


# Получение имени пользователя
def get_user_name(user_id):
    return user_names.get(user_id, "Гость")

# Сохранение имени пользователя
def save_user_name(user_id, name):
    user_names[user_id] = name


# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id

    # Если имя пользователя не сохранено, предложим ввести его
    if chat_id not in user_names:
        bot.send_message(chat_id, "Привет! Я ваш чат-бот. Как к тебе обращаться? (Введите ваше имя)")
    else:
        user_name = get_user_name(chat_id)
        bot.send_message(chat_id, f"Привет, {user_name}!")
    log_event(f"User {chat_id} starts to chat with bot")

# Обработка введенного имени пользователя
@bot.message_handler(func=lambda message: message.text and message.text.lower() != "/start" and message.chat.id not in user_names)
def handle_user_name(message):
    chat_id = message.chat.id
    user_name = message.text.strip()

    save_user_name(chat_id, user_name)
    bot.send_message(chat_id, f"Отлично, {user_name}! Теперь вы можете задавать мне вопросы.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    help_message = (
        "Привет! Я ваш чат-бот. Вот что я умею:\n"
        "/start - начать взаимодействие\n"
        "/help - получить справку о функционале\n"
        "Упомяни в сообщении слово 'погода' чтобы получть информацию о погоде.\n"
        "Упомяни в сообщении фразу 'курс валют' чтобы получить курсы валют к рублю\n"
        "Упомяни в сообщении слово 'шутка' чтобы увидеть шутку про Чака Норриса"
    )
    bot.send_message(chat_id, help_message)

# Обработка текстовых сообщений от пользователя
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    user_name = get_user_name(chat_id)
    text = message.text.lower()

    global flg_weath

    if "погода" in text:
        bot.send_message(chat_id, f"В каком же городе вы хотите узнать погоду, {get_user_name(chat_id)}? Введите: Город 'название города'")
        flg_weath = True
        log_event(f"User {chat_id} asked for weather")
    elif "город" in text and flg_weath:
        flg_weath = False
        wrds = text.split()
        city = wrds[wrds.index("город")+1]
        bot.send_message(chat_id, get_weather(city))
    elif "курс валют" in text:
        bot.send_message(chat_id, f"Конечно, {get_user_name(chat_id)}, давайте я покажу вам курсы валют. \n"
                         f"{get_currency_exchange_rates()}")
        log_event(f"User {chat_id} asked for excange couses")
    elif "шутка" in text:
        bot.send_message(chat_id, f"Хотите шутку {get_user_name(chat_id)}? Держите!")
        joke = get_chuck_norris_joke()
        bot.send_message(chat_id, joke)
        log_event(f"User {chat_id} asked for a joke")
    else:
        bot.send_message(chat_id, f"Не понимаю ваш запрос, {user_name}. Попробуйте еще раз.")
        log_event(f"User {chat_id} sent unknown message")

# Запуск бота
if __name__ == "__main__":
    log_event(f"Bot online")
    bot.polling(none_stop=True)
