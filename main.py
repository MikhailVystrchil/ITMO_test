from chatbot_development.itmo_ai_bot import bot

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
