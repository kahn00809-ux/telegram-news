# Telegram News

Учебный сайт с автоматической лентой новостей из официального блога Telegram и канала Павла Дурова.

## Запуск

```powershell
cd telegram-news
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Откройте `http://127.0.0.1:5000`.

Сайт проверяет источники каждые 30 минут. Интервал меняется через `REFRESH_INTERVAL_MINUTES`.

## Подключение @durov

Для чтения публичного канала нужны `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` из Telegram API. При первом запуске Telethon запросит авторизацию и сохранит локальную сессию. Без этих параметров сайт продолжает работать с блогом Telegram.

В продакшене значения `.env` нужно хранить в секретах хостинга, а процесс Flask запускать через WSGI-сервер.

## Размещение на Render

1. Создайте репозиторий на GitHub и загрузите в него содержимое папки `telegram-news`.
2. На [render.com](https://render.com) выберите **New → Web Service** и подключите этот репозиторий.
3. Укажите настройки:
	- **Runtime:** `Python 3`
	- **Build Command:** `pip install -r requirements.txt`
	- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
4. В разделе **Environment Variables** добавьте `REFRESH_INTERVAL_MINUTES=30`.
5. Для подключения `@durov` добавьте `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` как секретные переменные.
6. Нажмите **Create Web Service**. Через несколько минут Render выдаст публичный адрес сайта.

Важно: бесплатный Render может остановить сервис после периода без запросов. Кроме того, локальный файл `data/news.json` не является постоянным хранилищем на бесплатном тарифе. Для учебного проекта это подходит; для постоянной публикации позже лучше подключить PostgreSQL или диск.
