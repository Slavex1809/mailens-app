import csv
import os

# Категории — как в вашем DEFAULT_CATEGORIES
CATEGORIES = [
    "Деловое предложение",
    "Жалоба клиента",
    "Техническая поддержка",
    "Финансовый запрос",
    "Спам / Реклама",
    "HR / Рекрутинг",
    "Юридическое письмо",
    "Новости / Анонсы",
    "Маркетинг / Продажи",
    "Личное сообщение",
    "Не определена"
]

# Порядок чередования (чтобы было равномерно)
pattern = [
    "Деловое предложение",
    "Жалоба клиента",
    "Техническая поддержка",
    "Финансовый запрос",
    "Спам / Реклама",
    "HR / Рекрутинг",
    "Юридическое письмо",
    "Новости / Анонсы",
    "Маркетинг / Продажи",
    "Личное сообщение"
]

output_dir = "../test_emails"
os.makedirs(output_dir, exist_ok=True)

# Генерация 500 записей
labels = []
for i in range(1, 501):
    filename = f"{i:03d}_{pattern[(i-1) % len(pattern)].replace(' ', '_').replace('/', '-')}.eml"
    true_category = pattern[(i-1) % len(pattern)]
    labels.append({"filename": filename, "true_category": true_category})

# Запись в CSV
csv_path = os.path.join(output_dir, "labels.csv")
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "true_category"])
    writer.writeheader()
    writer.writerows(labels)

print(f"✅ Создано 500 записей в {csv_path}")
print(f"Примеры строк:")
for row in labels[:5]:
    print(f"  {row['filename']} → {row['true_category']}")