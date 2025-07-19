from flask import Flask, request, render_template
import sqlite3
import uuid
from datetime import datetime
import threading
import telebot

app = Flask(__name__)

BOT_TOKEN = '8146568905:AAFYIrAAklQ8HEVH3lXEtu9PKQN1q7LctQI'
CHAT_IDS = ['7873076756', '1270385177', 1496767192, 755780823, 234674848, 515450219]
bot = telebot.TeleBot(BOT_TOKEN)

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nickname TEXT UNIQUE,
            code TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

#отправка сообщения
def notify_admins(nickname, code):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"кто-то прошел арг:\nНик: {nickname}\nКод: {code}\nвремя: {timestamp}"
    for chat_id in CHAT_IDS:
        bot.send_message(chat_id, text)

#регистрация
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname'].strip()

        code = str(uuid.uuid4())[:8]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (nickname, code, timestamp) VALUES (?, ?, ?)",
                      (nickname, code, timestamp))
            conn.commit()
            conn.close()

            # Уведомляем в отдельном потоке
            threading.Thread(target=notify_admins, args=(nickname, code)).start()

            return render_template('register.html', code=code)
        except sqlite3.IntegrityError:
            return "Этот ник уже зарегистрирован."

    return render_template('register.html', code=None)

if __name__ == '__main__':
    app.run(debug=True)


