import os
import random

# Категории и шаблоны
CATEGORIES = {
    "Бизнес": {
        "en": [
            "Subject: Partnership Opportunity — {topic}\nFrom: {sender}@{domain}.com\nTo: {to}\n\nDear Team,\n\nWe propose collaboration on {topic}. Let's schedule a call.\n\nBest,\n{sender}",
            "Subject: Business Proposal — {topic}\nFrom: {sender}@{domain}.com\nTo: {to}\n\nHello,\n\nAttached is our proposal for {topic}. Looking forward to your feedback.\n\nRegards,\n{sender}"
        ],
        "ru": [
            "Subject: Деловое предложение — {topic}\nFrom: {sender}@{domain}.ru\nTo: {to}\n\nУважаемые коллеги,\n\nПредлагаем сотрудничество по {topic}. Готовы провести презентацию.\n\nС уважением,\n{sender}",
            "Subject: Сотрудничество — {topic}\nFrom: {sender}@{domain}.ru\nTo: {to}\n\nЗдравствуйте,\n\nВо вложении предложение по {topic}. Ждём вашего ответа.\n\nС уважением,\n{sender}"
        ]
    },
    "Жалоба": {
        "en": [
            "Subject: Complaint — {issue}\nFrom: {sender}@{domain}.net\nTo: {to}\n\nYour {product} is broken! I lost data. Fix it now!\n\nRegards,\n{sender}",
            "Subject: URGENT: Problem with {product}\nFrom: {sender}@{domain}.net\nTo: {to}\n\n{product} crashed. I demand compensation.\n\nSincerely,\n{sender}"
        ],
        "ru": [
            "Subject: Жалоба: {issue}\nFrom: {sender}@{domain}.ru\nTo: {to}\n\n{product} не работает! Я потерял данные. Требую исправить!\n\nС уважением,\n{sender}",
            "Subject: Срочно: проблема с {product}\nFrom: {sender}@{domain}.ru\nTo: {to}\n\n{product} сломался. Требую компенсацию.\n\nС уважением,\n{sender}"
        ]
    },
    "Спам": {
        "en": [
            "Subject: 🎁 WIN NOW! {prize}!\nFrom: prize@{domain}-prize.org\nTo: {to}\n\nCLICK HERE: http://{domain}.xyz/win\nHURRY! Offer expires in 24 hours!!!",
            "Subject: CONGRATULATIONS! You won {prize}!\nFrom: bonus@{domain}-bonus.ru\nTo: {to}\n\nClaim now: http://{domain}.xyz/claim\nDO NOT MISS!"
        ],
        "ru": [
            "Subject: СРОЧНО! Вы выиграли {prize}!\nFrom: prize@{domain}-prize.ru\nTo: {to}\n\nПолучите приз: http://{domain}.xyz/win\n❗ Акция до конца дня! ❗",
            "Subject: ПОЗДРАВЛЯЕМ! Ваш приз — {prize}!\nFrom: bonus@{domain}-bonus.ru\nTo: {to}\n\nЗаберите: http://{domain}.xyz/claim\n❗ Только сегодня! ❗"
        ]
    },
    "Фишинг": {
        "en": [
            "Subject: URGENT: Your account will be suspended\nFrom: security@{spoof_domain}.ru\nTo: {to}\n\nVerify now: http://{fake_domain}/login\nIT Department",
            "Subject: Security Alert — Action Required\nFrom: support@{spoof_domain}-security.ru\nTo: {to}\n\nConfirm your credentials: http://{fake_domain}/verify\nSecurity Team"
        ],
        "ru": [
            "Subject: ВАЖНО: ваша учётная запись будет заблокирована\nFrom: security@{spoof_domain}.ru\nTo: {to}\n\nПодтвердите данные: http://{fake_domain}/login\nСлужба поддержки",
            "Subject: Угроза безопасности — требуется действие\nFrom: support@{spoof_domain}-security.ru\nTo: {to}\n\nПроверьте аккаунт: http://{fake_domain}/verify\nКоманда безопасности"
        ]
    },
    "Техподдержка": {
        "en": [
            "Subject: Support Request — {issue}\nFrom: {sender}@client.com\nTo: {to}\n\nHello,\n\nWe have issue with {product}. Error: {error_code}. Can you help?\n\nThanks,\n{sender}",
            "Subject: API Authentication Problem\nFrom: {sender}@dev.net\nTo: {to}\n\nError 401 when calling {endpoint}. Please advise.\n\nBest,\n{sender}"
        ],
        "ru": [
            "Subject: Запрос в поддержку — {issue}\nFrom: {sender}@client.ru\nTo: {to}\n\nЗдравствуйте,\n\nПроблема с {product}. Ошибка: {error_code}. Помогите, пожалуйста.\n\nСпасибо,\n{sender}",
            "Subject: Ошибка авторизации API\nFrom: {sender}@dev.ru\nTo: {to}\n\nКод 401 при вызове {endpoint}. Прошу помощи.\n\nС уважением,\n{sender}"
        ]
    },
    "HR": {
        "en": [
            "Subject: Job Offer — {role}\nFrom: hr@techcorp.com\nTo: {to}\n\nWe invite you for an interview for {role}. Salary: {salary}.\n\nBest,\nHR Team",
            "Subject: Interview Invitation — {role}\nFrom: recruitment@innovatech.com\nTo: {to}\n\nYou are invited to interview for {role} on {date}.\n\nRegards,\nRecruitment"
        ],
        "ru": [
            "Subject: Вакансия: {role}\nFrom: hr@techcorp.ru\nTo: {to}\n\nПриглашаем на собеседование на позицию {role}. ЗП: {salary}.\n\nС уважением,\nКоманда HR",
            "Subject: Приглашение на собеседование — {role}\nFrom: recruitment@innovatech.ru\nTo: {to}\n\nПриглашаем на собеседование по позиции {role} {date}.\n\nС уважением,\nРекрутинг"
        ]
    },
    "Финансы": {
        "en": [
            "Subject: Invoice #{id}\nFrom: billing@vendor.com\nTo: {to}\n\nAmount: ${amount}. Payment due in {days} days.\n\nRegards,\nFinance Dept",
            "Subject: Payment Reminder — Invoice #{id}\nFrom: accounting@vendor.com\nTo: {to}\n\nOverdue: ${amount}. Please settle ASAP.\n\nBest,\nAccounting"
        ],
        "ru": [
            "Subject: Счёт №{id}\nFrom: billing@vendor.ru\nTo: {to}\n\nСумма: {amount} руб. Оплата в течение {days} дней.\n\nС уважением,\nБухгалтерия",
            "Subject: Напоминание об оплате — Счёт №{id}\nFrom: accounting@vendor.ru\nTo: {to}\n\nПросрочка: {amount} руб. Просьба оплатить.\n\nС уважением,\nБухгалтерия"
        ]
    }
}

# Параметры
TOPICS = ["AI Integration", "Cloud Security", "Data Analysis", "ML Pipeline"]
ISSUES = ["crash", "login failure", "slow performance", "data loss"]
PRODUCTS = ["MailLens", "SecureMail", "AV Shield", "DataGuard"]
ERROR_CODES = ["401", "500", "403", "Timeout"]
ENDPOINTS = ["/api/v1/auth", "/api/v2/data", "/api/secure"]
SPOOF_DOMAINS = ["avsoft-security", "avsoft-support", "av-secure"]
FAKE_DOMAINS = ["avsoft-login.ru", "av-verify.ru", "secure-av.ru"]
ROLES = ["Senior Data Engineer", "ML Developer", "Security Analyst"]
SALARIES = ["300 000 RUB", "250 000 RUB", "350 000 RUB"]
DATES = ["26 Dec", "27 Dec", "28 Dec"]
AMOUNTS = ["15,000", "25,000", "10,500"]
IDS = [f"INV-{random.randint(1000,9999)}" for _ in range(50)]
PRIZES = ["$1,000,000", "iPhone 16", "Trip to Bali", "1,000,000 RUB"]
DAYS = ["10", "5", "15", "30"]  # для {days}

# Генерация
os.makedirs("test_emails", exist_ok=True)
labels = []

for i in range(1, 501):
    category = random.choice(list(CATEGORIES.keys()))
    lang = random.choice(["en", "ru"])
    template = random.choice(CATEGORIES[category][lang])
    
    # Все параметры из шаблонов переданы явно
    content = template.format(
        topic=random.choice(TOPICS),
        issue=random.choice(ISSUES),
        product=random.choice(PRODUCTS),
        error_code=random.choice(ERROR_CODES),
        endpoint=random.choice(ENDPOINTS),
        spoof_domain=random.choice(SPOOF_DOMAINS),
        fake_domain=random.choice(FAKE_DOMAINS),
        role=random.choice(ROLES),
        salary=random.choice(SALARIES),
        date=random.choice(DATES),
        amount=random.choice(AMOUNTS),
        id=random.choice(IDS),
        prize=random.choice(PRIZES),
        days=random.choice(DAYS),  # ← есть!
        sender=f"{random.choice(['alex', 'maria', 'john', 'anna'])}.{random.choice(['smith', 'ivanov', 'petrov'])}",
        domain=random.choice(["techcorp", "innovatech", "securemail", "dataguard"]),
        to="test@avsoft.ru"
    )
    
    # Сохранение с явной кодировкой
    filename = f"{i:03d}_{category.lower().replace(' ', '_')}_{lang}.eml"
    with open(f"test_emails/{filename}", "w", encoding="utf-8") as f:
        f.write(content)
    
    labels.append(f"{filename},{category},{lang}")

# Сохранение меток
with open("test_emails/labels.csv", "w", encoding="utf-8") as f:
    f.write("filename,true_category,language\n")
    f.write("\n".join(labels))

print("✅ 500 писем успешно сгенерировано!")
print("📁 Папка: test_emails/")
print("📊 Метки: test_emails/labels.csv")