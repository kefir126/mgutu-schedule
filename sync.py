import os
import requests

LOGIN = os.environ.get("MGUTU_LOGIN")
PASSWORD = os.environ.get("MGUTU_PASSWORD")
STUDENT_ID = "49172"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://dec.mgutm.ru/"
}

# 1. Авторизация
login_url = "https://dec.mgutm.ru/api/tokenauth"
payload = {
    "username": LOGIN,
    "password": PASSWORD
}

print("Авторизуемся...")
res = session.post(login_url, json=payload, headers=headers)
resp_json = res.json()

# Извлекаем токен из глубины ответа
try:
    token_data = resp_json["data"]["data"]
    access_token = token_data["accessToken"]
    user_name = token_data.get("userName", "Студент")
    print(f"Токен успешно получен для пользователя: {user_name}")
except Exception as e:
    print(f"Ошибка извлечения токена: {e}")
    print("Ответ сервера:", resp_json)
    exit(1)

# Передаем токен и в Authorization, и в Cookies (для надежности)
headers["Authorization"] = f"Bearer {access_token}"
session.cookies.set("accessToken", access_token)
session.cookies.set("token", access_token)

# 2. Скачивание календаря
calendar_url = f"https://dec.mgutm.ru/api/Rasp?idStudent={STUDENT_ID}&iCal=true"
print("Запрашиваем расписание...")
calendar_response = session.get(calendar_url, headers=headers)

if "BEGIN:VCALENDAR" in calendar_response.text:
    with open("schedule.ics", "w", encoding="utf-8") as f:
        f.write(calendar_response.text)
    print("УРА! Файл schedule.ics успешно получен и сохранен!")
else:
    print("Ошибка: календарь всё еще не получен.")
    print("Статус:", calendar_response.status_code)
    print("Текст ответа:", calendar_response.text[:300])
    exit(1)
