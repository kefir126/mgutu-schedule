import os
import requests

LOGIN = os.environ.get("MGUTU_LOGIN")
PASSWORD = os.environ.get("MGUTU_PASSWORD")
STUDENT_ID = "49172"  # Ваш ID студента из вашей ссылки

# Создаем сессию, которая сохраняет куки авторизации
session = requests.Session()

# 1. Авторизация
# ВНИМАНИЕ: Если адрес входа отличается от /api/login, замените его здесь:
login_url = "https://dec.mgutm.ru/WebApp/#/login"

# Имена полей (username/password или login/password) в зависимости от того, что вы увидели в F12
login_payload = {
    "username": LOGIN,
    "password": PASSWORD
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Авторизуемся...")
login_response = session.post(login_url, json=login_payload, headers=headers)

# Если API принимает не json, а форму, используется:
# login_response = session.post(login_url, data=login_payload, headers=headers)

# 2. Скачивание календаря с полученными куками
calendar_url = f"https://dec.mgutm.ru/api/Rasp?idStudent={STUDENT_ID}&iCal=true"
print("Запрашиваем расписание...")
calendar_response = session.get(calendar_url, headers=headers)

if "BEGIN:VCALENDAR" in calendar_response.text:
    with open("schedule.ics", "w", encoding="utf-8") as f:
        f.write(calendar_response.text)
    print("Успех: schedule.ics сформирован и сохранен!")
else:
    print("Ошибка: Сервер вернул некорректный ответ.")
    print("Статус код:", calendar_response.status_code)
    print("Ответ сервера (первые 200 символов):", calendar_response.text[:200])
    exit(1)
