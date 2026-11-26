import os
import re
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

try:
    token_data = resp_json["data"]["data"]
    access_token = token_data["accessToken"]
    user_name = token_data.get("userName", "Студент")
    print(f"Токен успешно получен для пользователя: {user_name}")
except Exception as e:
    print(f"Ошибка извлечения токена: {e}")
    print("Ответ сервера:", resp_json)
    exit(1)

headers["Authorization"] = f"Bearer {access_token}"
session.cookies.set("accessToken", access_token)
session.cookies.set("token", access_token)

# 2. Скачивание календаря
calendar_url = f"https://dec.mgutm.ru/api/Rasp?idStudent={STUDENT_ID}&iCal=true"
print("Запрашиваем расписание...")
calendar_response = session.get(calendar_url, headers=headers)

raw_ics = calendar_response.text

if "BEGIN:VCALENDAR" not in raw_ics:
    print("Ошибка: календарь не получен.")
    print("Статус:", calendar_response.status_code)
    print("Текст ответа:", raw_ics[:300])
    exit(1)

# Сохраняем общий исходный файл (на всякий случай)
with open("schedule.ics", "w", encoding="utf-8") as f:
    f.write(raw_ics)

# 3. Разбиваем расписание по типам пар
if "BEGIN:VEVENT" in raw_ics:
    header = raw_ics.split("BEGIN:VEVENT", 1)[0]
    events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", raw_ics, re.DOTALL)
else:
    header = raw_ics.replace("END:VCALENDAR", "")
    events = []

if not header.endswith("\n"):
    header += "\n"

categories = {
    "lectures.ics": [],   # Лекции
    "labs.ics": [],       # Лабораторные
    "practices.ics": [],  # Практики
    "credits.ics": [],    # Зачеты
    "exams.ics": [],      # Экзамены
    "other.ics": []       # Прочее (консультации и т.д.)
}

for event in events:
    match = re.search(r"^SUMMARY:(.*)$", event, re.MULTILINE | re.IGNORECASE)
    summary = match.group(1).strip().lower() if match else ""

    if re.match(r"^(лек|лекция)\b", summary):
        categories["lectures.ics"].append(event)
    elif re.match(r"^(лаб|лабораторная)\b", summary):
        categories["labs.ics"].append(event)
    elif re.match(r"^(пр|практ|практика)\b", summary):
        categories["practices.ics"].append(event)
    elif re.match(r"^(зач|зачет|зачёт|диф\.?\s*зач)\b", summary):
        categories["credits.ics"].append(event)
    elif re.match(r"^(экз|экзамен)\b", summary):
        categories["exams.ics"].append(event)
    else:
        categories["other.ics"].append(event)

for filename, ev_list in categories.items():
    body = "\n".join(ev_list) + ("\n" if ev_list else "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + body + "END:VCALENDAR\n")
    print(f"Файл {filename}: сохранено событий — {len(ev_list)}")

print("Готово! Все файлы успешно обновлены.")
