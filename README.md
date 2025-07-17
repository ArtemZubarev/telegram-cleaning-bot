# 🧹 Telegram Cleaning Bot

Бот для техслужащих отеля (уборка номеров) на Python + aiogram 3.

---

## 🚀 Запуск локально

1. Клонируй репозиторий
2. Установи зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Создай переменные окружения (например, через .env или в системе):

   ```bash
   export BOT_TOKEN=твой_токен
   ```

4. Запусти:

   ```bash
   python main.py
   ```

---

## ☁️ Деплой на Render

1. Подключи GitHub репозиторий к Render
2. В **Build Command** оставь пустым или укажи:

   ```bash
   pip install -r requirements.txt
   ```

3. В **Start Command**:

   ```bash
   python main.py
   ```

4. Добавь Environment Variable:

   | KEY       | VALUE           |
   | --------- | --------------- |
   | BOT_TOKEN | твой*токен*бота |

5. Нажми **Deploy** – готово ✅

---
