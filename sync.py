import os
import requests

LOGIN = os.environ.get("MGUTU_LOGIN")
PASSWORD = os.environ.get("MGUTU_PASSWORD")
STUDENT_ID = "49172"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}

# 1. Авторизация через tokenauth
login_url = "https://dec.mgutm.ru/api/tokenauth"

# Пробуем передать данные (в MMIS обычно поля называются username или login)
payload = {
    "username": LOGIN,
    "password": PASSWORD
}

print("Пытаемся авторизоваться через tokenauth...")
res = session.post(login_url, json=payload, headers=headers)

# Если вернуло ошибку, пробуем альтернативное имя поля ("login")
if res.status_code != 200 or "token" not in res.text.lower():
    payload = {"login": LOGIN, "password": PASSWORD}
    res = session.post(login_url, json=payload, headers=headers)

print(f"Статус авторизации: {res.status_code}")
print(f"Ответ сервера: {res.text[:300]}")

# Пытаемся извлечь токен, если сервер отдает его в JSON
token = None
try:
    data = res.json()
    if isinstance(data, dict):
        token = data.get("token") or data.get("data") or data.get("accessToken")
except Exception:
    pass

# Если токен найден, подставляем его в заголовок Authorization
if token and isinstance(token, str):
    print("Токен успешно получен!")
    headers["Authorization"] = f"Bearer {token}"

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
    print("Текст ответа:", calendar_response.text[:200])
    exit(1)
