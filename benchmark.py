"""
BENCHMARK.PY - Улучшенная версия с расширенной аналитикой
"""

import os
import time
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime
import json
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

warnings.filterwarnings('ignore')

class EnhancedModelBenchmark:
    """Улучшенный бенчмарк с детальной аналитикой и визуализацией"""
    
    def __init__(self, test_emails_dir: str = "test_emails"):
        self.test_emails_dir = Path(test_emails_dir)
        self.results_history = []
        
        # Создаём директории для логов
        self.logs_dir = Path("benchmark_logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Конфигурация
        self.config = {
            "min_text_length": 50,
            "max_text_length": 10000,
            "default_threshold": 0.15,  # Пониженный порог
            "max_emails": 500,
            "cache_enabled": True,
            "save_detailed_results": True
        }
        
        # Автоматически создаём демо-данные если папки нет
        if not self.test_emails_dir.exists():
            self._create_enhanced_demo_structure()
    
    def _create_enhanced_demo_structure(self):
        """Создание улучшенной структуры демо-данных"""
        self.test_emails_dir.mkdir(exist_ok=True)
        
        # Расширенные категории с примерами
        category_templates = {
            "Деловое предложение": [
                "Уважаемый партнёр! Предлагаем вам уникальную возможность сотрудничества в сфере IT-разработки. Наша компания готова предоставить эксклюзивные условия по разработке программного обеспечения. Будем рады обсудить детали на личной встрече.\n\nС уважением,\nИван Петров\nДиректор по развитию",
                "Здравствуйте! Компания 'ТехноИнновации' предлагает партнёрство в реализации проекта по автоматизации бизнес-процессов. Готовы рассмотреть индивидуальные условия сотрудничества. Просим направить ваши предложения до конца недели.",
                "Добрый день! Направляем вам коммерческое предложение по поставке облачных сервисов. В приложении вы найдёте детали тарифов и условий сотрудничества. Ждём вашего ответа для уточнения деталей."
            ],
            "Жалоба клиента": [
                "Уважаемая служба поддержки! Я крайне недоволен качеством вашего сервиса. Вчера система была недоступна более 3 часов, что привело к финансовым потерям в размере 50,000 рублей. Требую немедленного решения проблемы и компенсации ущерба.\n\nС нетерпением жду ответа,\nАлексей Сидоров",
                "Добрый день! Это уже третья жалоба за месяц. Ваш продукт постоянно выходит из строя, техническая поддержка не отвечает. Требую срочного вмешательства руководства и решения всех накопившихся проблем.",
                "Здравствуйте! Письмо-претензия по договору №2345. Уведомляю о нарушении сроков поставки на 2 недели. Требую выплаты неустойки согласно пункту 5.3 договора."
            ],
            "Техническая поддержка": [
                "Здравствуйте! Не могу войти в личный кабинет с 10:00 утра. При вводе логина и пароля получаю ошибку '500 Internal Server Error'. Пробовал очистить кэш, сменить браузер — не помогает.\n\nПрошу помочь с решением проблемы.\nАнна К.",
                "Добрый день! Возникла проблема с API интеграцией. При запросе к endpoint /api/v1/data получаю статус 401. Проверил токены — всё в порядке. Нужна срочная техническая помощь.",
                "Здравствуйте! Сообщаю о баге в мобильном приложении версии 2.3.1. На iOS 16 при попытке загрузки файлов приложение крашится. Логи прилагаю."
            ],
            "Финансовый запрос": [
                "Уважаемые коллеги! Прошу предоставить детализированный отчёт по счету №INV-2024-001 за январь 2024 года, а также уточнить сроки оплаты по договору №5678.\n\nС уважением,\nМария Иванова\nФинансовый отдел",
                "Добрый день! Направляем счёт на оплату услуг за декабрь 2023. Сумма: 150,000 рублей. Срок оплата: 10 рабочих дней. Просим подтвердить получение.",
                "Здравствуйте! Запрос на возврат средств по транзакции №TRX-789456 от 15.01.2024. Сумма возврата: 25,000 рублей. Причина: двойное списание."
            ],
            "Спам / Реклама": [
                "🎉 ПОЗДРАВЛЯЕМ! ВЫ ВЫИГРАЛИ 1 000 000 РУБЛЕЙ! 🎉\n\nДля получения приза перейдите по ссылке: http://super-prize.ru/win\n\n❗ АКЦИЯ ДЕЙСТВУЕТ ТОЛЬКО 24 ЧАСА! ❗\n\nНе упустите свой шанс стать миллионером!",
                "СРОЧНО! СКИДКА 70% НА ВСЕ КУРСЫ!\n\nТолько до конца недели! Успейте купить курсы по программированию со скидкой 70%!\n\nПереходите: http://best-courses.ru/discount\n\nНе пропустите эту уникальную возможность!",
                "ВЫ ВЫИГРАЛИ IPHONE 15 PRO MAX!\n\nВаш номер оказался счастливым! Заберите свой приз: http://iphone-giveaway.ru/claim\n\n⚠️ ВНИМАНИЕ: Предложение действительно только для первых 100 участников!"
            ],
            "HR / Рекрутинг": [
                "Здравствуйте, Иван! Мы ознакомились с вашим резюме на HH.ru и хотели бы пригласить вас на собеседование на позицию Senior Python Developer.\n\nДата: 25 января 2024\nВремя: 15:00\nФормат: онлайн (Zoom)\n\nСсылка для подключения: https://zoom.us/j/123456789\n\nЖдём вас!\n\nС уважением,\nАнна, рекрутер",
                "Добрый день! Компания 'ТехноЛаб' ищет Data Scientist. Увидели ваш профиль на LinkedIn. Предлагаем обсудить возможность сотрудничества.\n\nЗарплатная вилка: 250,000 - 350,000 рублей\nФормат работы: гибридный\n\nГотовы обсудить детали в удобное для вас время.",
                "Привет! Видел твоё портфолио на GitHub. У нас в стартапе открыта вакансия ML Engineer. Интересует?"
            ],
            "Юридическое письмо": [
                "УВЕДОМЛЕНИЕ О НАРУШЕНИИ ДОГОВОРА\n\nДоговор №123-456 от 15.01.2023\n\nНастоящим уведомляем, что ваша компания нарушила пункт 4.2 Договора о поставке товаров. Требуем устранить нарушения в течение 10 рабочих дней.\n\nВ случае неисполнения будем вынуждены обратиться в суд.\n\nЮридический отдел\nООО 'ПравоГарант'",
                "ПРЕТЕНЗИЯ\n\nПо договору оказания услуг №789 от 20.12.2023\n\nНаправляем претензию в связи с некачественным оказанием услуг. Требуем:\n1. Устранить недостатки\n2. Выплатить неустойку\n3. Компенсировать убытки\n\nСрок ответа: 5 дней.",
                "ИСКОВОЕ ЗАЯВЛЕНИЕ\n\nПодготовлено исковое заявление о взыскании задолженности по договору №456. Сумма иска: 1,500,000 рублей.\n\nПредлагаем урегулировать вопрос в досудебном порядке."
            ],
            "Новости / Анонсы": [
                "Дорогие пользователи! 🎊\n\nРады сообщить о запуске новой версии платформы 3.0!\n\nОсновные улучшения:\n• Ускорение работы на 40%\n• Совершенно новый интерфейс\n• Дополнительные функции аналитики\n• Улучшенная безопасность\n\nОбновление будет доступно с 1 февраля.\n\nС уважением,\nКоманда разработки",
                "ВАЖНОЕ ОБЪЯВЛЕНИЕ\n\nУведомляем о плановых технических работах 25 января с 02:00 до 06:00 МСК.\n\nВ этот период возможны перебои в работе сервиса.\n\nПриносим извинения за временные неудобства.",
                "АНОНС: Вебинар 'Искусственный интеллект в бизнесе'\n\nДата: 30 января 2024\nВремя: 19:00 МСК\nСпикер: Дмитрий Смирнов, CEO AI Solutions\n\nРегистрация: http://webinar.ai/register"
            ],
            "Маркетинг / Продажи": [
                "СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ ДЛЯ ВАС! ✨\n\nТолько для наших постоянных клиентов — скидка 30% на все курсы по программированию до конца месяца!\n\nИспользуйте промокод: SALE30\n\nНе упустите возможность повысить свои навыки!\n\nЗаписывайтесь сейчас: http://courses.com",
                "УВЕЛИЧЬТЕ ПРОДАЖИ НА 200% С НАШИМ РЕШЕНИЕМ!\n\nПредставляем новую CRM-систему с AI-аналитикой.\n\nПервый месяц бесплатно!\n\nЗакажите демо: http://crm-ai.ru/demo",
                "РАСПРОДАЖА СКЛАДА!\n\nСнижаем цены на всё оборудование на 50%!\n\nТолько этой неделей! Успейте купить:\n• Серверы\n• Сетевое оборудование\n• Компьютеры\n\nПодробности: http://sale.hardware.ru"
            ],
            "Личное сообщение": [
                "Привет! Как дела? Давно не виделись. 😊\n\nПредлагаю встретиться в субботу в 18:00 в нашем любимом кафе 'У Франсуа'.\n\nПозвони мне, чтобы подтвердить.\n\nОбнимаю!\nМаша",
                "Привет, друг! Посмотри это видео, очень смешное: https://youtube.com/watch?v=abcdef\n\nКак твой проект? У меня всё ок, готовлюсь к отпуску.\n\nВечером перезвоню!",
                "Доброе утро! ☕\n\nОтправил тебе документы по проекту. Посмотри, пожалуйста, когда будет время.\n\nХорошего дня!\nКоллега"
            ]
        }
        
        # Создаём улучшенные демо-файлы
        demo_data = []
        for i in range(1, 101):  # 100 демо-писем
            categories = list(category_templates.keys())
            category = categories[(i-1) % len(categories)]
            template = random.choice(category_templates[category])
            
            demo_data.append({
                'filename': f'{i:03d}_{category.replace(" ", "_").replace("/", "-")}.txt',
                'true_category': category
            })
            
            # Сохраняем файл
            filepath = self.test_emails_dir / demo_data[-1]['filename']
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
        
        # Сохраняем labels
        df = pd.DataFrame(demo_data)
        labels_path = self.test_emails_dir / "labels.csv"
        df.to_csv(labels_path, index=False, encoding='utf-8-sig')
        
        # Также сохраняем расширенную информацию
        stats = {
            "total_emails": len(demo_data),
            "categories": {cat: sum(1 for d in demo_data if d['true_category'] == cat) 
                          for cat in category_templates.keys()},
            "created_at": datetime.now().isoformat(),
            "avg_text_length": np.mean([len(t) for templates in category_templates.values() for t in templates])
        }
        
        stats_path = self.test_emails_dir / "dataset_info.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        st.info(f"✅ Создано {len(demo_data)} улучшенных демо-писем в папке {self.test_emails_dir}")
    
    def load_test_emails(self, limit: int = None, shuffle: bool = True) -> List[Dict]:
        """Загрузка тестовых писем с улучшенной обработкой"""
        labels_path = self.test_emails_dir / "labels.csv"
        
        if not labels_path.exists():
            st.error(f"❌ Файл labels.csv не найден: {labels_path.absolute()}")
            return []
        
        try:
            # Загрузка с правильной кодировкой
            df_labels = pd.read_csv(labels_path, encoding='utf-8-sig')
            
            if shuffle:
                df_labels = df_labels.sample(frac=1, random_state=42).reset_index(drop=True)
            
            if limit and limit < len(df_labels):
                df_labels = df_labels.head(limit)
            
            emails = []
            stats = {
                'total': len(df_labels),
                'loaded': 0,
                'failed': 0,
                'categories': {}
            }
            
            for idx, row in df_labels.iterrows():
                filename = str(row["filename"]).strip()
                true_cat = str(row["true_category"]).strip()
                
                # Статистика по категориям
                if true_cat not in stats['categories']:
                    stats['categories'][true_cat] = 0
                stats['categories'][true_cat] += 1
                
                # Ищем файл
                file_found = False
                content = ""
                
                # Пробуем разные пути
                possible_paths = [
                    self.test_emails_dir / filename,
                    self.test_emails_dir / f"{Path(filename).stem}.txt",
                    self.test_emails_dir / f"{Path(filename).stem}.eml",
                ]
                
                for file_path in possible_paths:
                    if file_path.exists():
                        try:
                            # Читаем с разными кодировками
                            with open(file_path, 'rb') as f:
                                raw_content = f.read()
                            
                            # Пробуем декодировать
                            for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251', 'latin-1']:
                                try:
                                    content = raw_content.decode(encoding, errors='ignore')
                                    break
                                except:
                                    continue
                            
                            if content:
                                file_found = True
                                break
                        except Exception as e:
                            continue
                
                if not file_found:
                    # Используем шаблон по категории
                    template_bank = {
                        "Деловое предложение": "Предложение о сотрудничестве в сфере IT разработки. Готовы обсудить условия партнерства и предоставить коммерческое предложение.",
                        "Жалоба клиента": "Официальная жалоба на качество обслуживания. Требуется срочное решение проблемы и компенсация ущерба.",
                        "Техническая поддержка": "Запрос в техническую поддержку. Проблема с доступом к системе, необходима помощь специалиста.",
                        "Финансовый запрос": "Запрос финансовых документов и уточнение условий оплаты по договору.",
                        "Спам / Реклама": "Специальное предложение! Ограниченная акция со скидками!",
                        "HR / Рекрутинг": "Приглашение на собеседование. Обсуждение условий трудоустройства.",
                        "Юридическое письмо": "Юридическое уведомление по договору с требованием исполнения обязательств.",
                        "Новости / Анонсы": "Анонс новых функций платформы и важные объявления для пользователей.",
                        "Маркетинг / Продажи": "Маркетинговое предложение со специальными условиями для клиентов.",
                        "Личное сообщение": "Неформальное сообщение от коллеги или знакомого."
                    }
                    content = template_bank.get(true_cat, f"Текст письма категории: {true_cat}")
                    stats['failed'] += 1
                else:
                    stats['loaded'] += 1
                
                # Проверяем минимальную длину
                if len(content.strip()) < self.config["min_text_length"]:
                    content = content + "\n" + "Дополнительный текст для соответствия минимальной длине."
                
                # Ограничиваем максимальную длину
                if len(content) > self.config["max_text_length"]:
                    content = content[:self.config["max_text_length"]] + "..."
                
                emails.append({
                    "filename": filename,
                    "true_category": true_cat,
                    "text": content,
                    "length": len(content),
                    "words": len(content.split()),
                    "loaded_from_file": file_found
                })
            
            # Отчёт о загрузке
            report = f"""
            📊 Отчёт о загрузке тестовых данных:
            • Всего записей: {stats['total']}
            • Успешно загружено: {stats['loaded']}
            • Использованы шаблоны: {stats['failed']}
            • Категории: {len(stats['categories'])}
            """
            
            st.info(report)
            
            # Сохраняем статистику
            self._save_loading_stats(stats)
            
            return emails
            
        except Exception as e:
            st.error(f"❌ Критическая ошибка загрузки тестовых данных: {str(e)[:200]}")
            return []
    
    def _save_loading_stats(self, stats: Dict):
        """Сохранение статистики загрузки"""
        stats_file = self.logs_dir / "loading_stats.json"
        
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                existing_stats = json.load(f)
        else:
            existing_stats = []
        
        existing_stats.append({
            "timestamp": datetime.now().isoformat(),
            **stats
        })
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(existing_stats, f, ensure_ascii=False, indent=2)
    
    def run_classification_benchmark(self, classifier, num_emails: int = 100, 
                                    detailed_analysis: bool = True) -> pd.DataFrame:
        """Запуск расширенного бенчмарка классификации"""
        # Загружаем письма
        emails = self.load_test_emails(num_emails)
        
        if not emails:
            st.error("❌ Нет писем для тестирования")
            return pd.DataFrame()
        
        results = []
        start_time = time.time()
        
        # Создаём контейнер для прогресса
        progress_container = st.container()
        status_container = st.container()
        metrics_container = st.container()
        
        with progress_container:
            st.markdown("### 🚀 Запуск бенчмарка")
            progress_bar = st.progress(0)
            status_text = st.empty()
            metrics_text = st.empty()
        
        # Временные метрики
        processing_times = []
        confidences = []
        
        for i, email in enumerate(emails):
            # Обновляем статус
            status_text.text(f"📧 Обработка {i+1}/{len(emails)}: {email['filename'][:30]}...")
            
            # Замер времени
            iteration_start = time.perf_counter()
            
            try:
                # Классификация с пониженным порогом
                if hasattr(classifier, 'set_threshold'):
                    classifier.set_threshold(self.config["default_threshold"])
                
                prediction = classifier.classify(email["text"], top_n=3, use_cache=self.config["cache_enabled"])
                
                # Время обработки
                duration = (time.perf_counter() - iteration_start) * 1000
                processing_times.append(duration)
                
                # Определяем правильность
                predicted_cat = prediction.get("predicted_category", "Не определена")
                true_cat = email["true_category"]
                is_undefined = prediction.get("is_undefined", False)
                confidence = prediction.get("confidence", 0.0)
                confidences.append(confidence)
                
                # Улучшенная логика сравнения
                is_correct = self._enhanced_category_match(predicted_cat, true_cat, is_undefined)
                
                # Детальная информация
                result = {
                    "filename": email["filename"],
                    "true_category": true_cat,
                    "predicted_category": predicted_cat,
                    "confidence": confidence,
                    "is_undefined": is_undefined,
                    "time_ms": round(duration, 1),
                    "is_correct": is_correct,
                    "success": True,
                    "text_length": email["length"],
                    "word_count": email["words"],
                    "method": prediction.get("method", "unknown"),
                    "top_categories": json.dumps(prediction.get("top_categories", []), ensure_ascii=False),
                    "all_scores": json.dumps(prediction.get("all_scores", {}), ensure_ascii=False) if prediction.get("all_scores") else "{}"
                }
                
                # Добавляем анализ уверенности
                if confidence > 0.7:
                    result["confidence_level"] = "high"
                elif confidence > 0.4:
                    result["confidence_level"] = "medium"
                else:
                    result["confidence_level"] = "low"
                
                results.append(result)
                
            except Exception as e:
                duration = (time.perf_counter() - iteration_start) * 1000
                results.append({
                    "filename": email["filename"],
                    "true_category": email["true_category"],
                    "predicted_category": "ERROR",
                    "confidence": 0.0,
                    "is_undefined": True,
                    "time_ms": round(duration, 1),
                    "is_correct": False,
                    "success": False,
                    "error": str(e)[:100],
                    "text_length": email["length"],
                    "word_count": email["words"]
                })
            
            # Обновляем прогресс и метрики
            progress = (i + 1) / len(emails)
            progress_bar.progress(progress)
            
            if i % 10 == 0:  # Обновляем каждые 10 итераций
                current_metrics = self._calculate_intermediate_metrics(results, processing_times)
                metrics_text.text(
                    f"✅ Обработано: {i+1}/{len(emails)}\n"
                    f"📊 Точность: {current_metrics.get('accuracy', 0):.1%}\n"
                    f"⚡ Среднее время: {current_metrics.get('avg_time_ms', 0):.1f} мс"
                )
        
        # Завершение
        total_time = time.time() - start_time
        status_text.text(f"✅ Бенчмарк завершён за {total_time:.1f} секунд")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Создаём DataFrame
        df = pd.DataFrame(results)
        
        if detailed_analysis and not df.empty:
            self._perform_detailed_analysis(df, emails)
        
        # Сохраняем результаты
        self._save_benchmark_results(df, total_time)
        
        return df
    
    def _enhanced_category_match(self, predicted: str, true: str, is_undefined: bool) -> bool:
        """Улучшенная логика сравнения категорий"""
        # Нормализация
        pred_norm = predicted.lower().strip()
        true_norm = true.lower().strip()
        
        # Точное совпадение
        if pred_norm == true_norm:
            return True
        
        # Частичное совпадение
        pred_words = set([w for w in pred_norm.split() if len(w) > 2])
        true_words = set([w for w in true_norm.split() if len(w) > 2])
        
        # Если есть пересечение ключевых слов
        if pred_words.intersection(true_words):
            return True
        
        # Синонимы и похожие категории
        synonym_groups = [
            ["деловое предложение", "коммерческое предложение", "бизнес предложение"],
            ["жалоба клиента", "претензия", "рекламация"],
            ["техническая поддержка", "техподдержка", "поддержка"],
            ["финансовый запрос", "финансы", "счёт", "оплата"],
            ["спам / реклама", "спам", "реклама", "рассылка"],
            ["hr / рекрутинг", "кадры", "рекрутинг", "вакансия"],
            ["юридическое письмо", "юридическое", "договор"],
            ["новости / анонсы", "новости", "анонс", "объявление"],
            ["маркетинг / продажи", "маркетинг", "продажи"],
            ["личное сообщение", "личное", "неформальное"]
        ]
        
        for group in synonym_groups:
            if any(word in pred_norm for word in group) and any(word in true_norm for word in group):
                return True
        
        # Для "Не определена" категории
        if ("не определ" in true_norm or "undefined" in true_norm) and is_undefined:
            return True
        
        return False
    
    def _calculate_intermediate_metrics(self, results: List[Dict], processing_times: List[float]) -> Dict:
        """Расчёт промежуточных метрик"""
        if not results:
            return {}
        
        df_temp = pd.DataFrame(results)
        
        correct = df_temp["is_correct"].sum() if "is_correct" in df_temp.columns else 0
        total = len(df_temp)
        
        return {
            "accuracy": correct / total if total > 0 else 0.0,
            "avg_time_ms": np.mean(processing_times) if processing_times else 0.0,
            "processed": total
        }
    
    def _perform_detailed_analysis(self, df: pd.DataFrame, emails: List[Dict]):
        """Выполнение детального анализа результатов"""
        if df.empty:
            return
        
        st.markdown("## 📊 Детальный анализ результатов")
        
        # Основные метрики
        metrics = self.calculate_enhanced_metrics(df)
        
        # Отображаем метрики в колонках
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            accuracy = metrics["accuracy"]
            color = "green" if accuracy > 0.7 else "orange" if accuracy > 0.5 else "red"
            st.metric("🎯 Точность", f"{accuracy:.1%}", delta_color="off")
            st.markdown(f"<p style='color:{color};font-weight:bold'>Правильно: {metrics['correct_predictions']}/{metrics['total_emails']}</p>", unsafe_allow_html=True)
        
        with col2:
            st.metric("⚡ Среднее время", f"{metrics['avg_time_ms']:.1f} мс")
            st.caption(f"Мин: {metrics['min_time_ms']:.1f} мс, Макс: {metrics['max_time_ms']:.1f} мс")
        
        with col3:
            st.metric("❓ Не определено", f"{metrics['undefined_rate']:.1f}%")
            st.caption(f"Всего: {metrics['undefined_count']} писем")
        
        with col4:
            st.metric("📈 Уверенность", f"{metrics['avg_confidence']:.1%}")
            st.caption(f"Высокая: {metrics.get('high_confidence_pct', 0):.1f}%")
        
        # Расширенная аналитика
        st.markdown("### 📋 Расширенная аналитика")
        
        # Вкладки для разных видов анализа
        tab1, tab2, tab3, tab4 = st.tabs(["📊 По категориям", "📈 Временные метрики", "🎭 Матрица ошибок", "📝 Примеры"])
        
        with tab1:
            self._show_category_analysis(df)
        
        with tab2:
            self._show_time_analysis(df)
        
        with tab3:
            self._show_confusion_matrix(df)
        
        with tab4:
            self._show_examples(df, emails)
    
    def _show_category_analysis(self, df: pd.DataFrame):
        """Анализ по категориям"""
        if "true_category" not in df.columns:
            return
        
        # Статистика по категориям
        category_stats = df.groupby("true_category").agg({
            "is_correct": ["count", "sum", "mean"],
            "confidence": ["mean", "std"],
            "time_ms": ["mean", "median"]
        }).round(3)
        
        # Переименовываем колонки
        category_stats.columns = [
            "total", "correct", "accuracy",
            "avg_conf", "std_conf",
            "avg_time", "median_time"
        ]
        
        # Форматирование
        category_stats["accuracy_pct"] = (category_stats["accuracy"] * 100).round(1)
        category_stats["avg_conf_pct"] = (category_stats["avg_conf"] * 100).round(1)
        
        st.dataframe(category_stats, use_container_width=True)
        
        # Визуализация
        if len(category_stats) > 1:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Точность по категориям", "Уверенность по категориям",
                              "Время обработки", "Распределение правильных ответов"),
                vertical_spacing=0.15
            )
            
            # 1. Точность
            fig.add_trace(
                go.Bar(
                    x=category_stats.index,
                    y=category_stats["accuracy_pct"],
                    name="Точность",
                    marker_color='lightblue',
                    text=category_stats["accuracy_pct"].apply(lambda x: f"{x:.1f}%"),
                    textposition='auto'
                ),
                row=1, col=1
            )
            fig.update_xaxes(title_text="Категория", row=1, col=1)
            fig.update_yaxes(title_text="Точность (%)", row=1, col=1)
            
            # 2. Уверенность
            fig.add_trace(
                go.Bar(
                    x=category_stats.index,
                    y=category_stats["avg_conf_pct"],
                    name="Уверенность",
                    marker_color='lightgreen',
                    text=category_stats["avg_conf_pct"].apply(lambda x: f"{x:.1f}%"),
                    textposition='auto'
                ),
                row=1, col=2
            )
            fig.update_xaxes(title_text="Категория", row=1, col=2)
            fig.update_yaxes(title_text="Уверенность (%)", row=1, col=2)
            
            # 3. Время
            fig.add_trace(
                go.Bar(
                    x=category_stats.index,
                    y=category_stats["avg_time"],
                    name="Время (мс)",
                    marker_color='orange',
                    text=category_stats["avg_time"].apply(lambda x: f"{x:.1f}"),
                    textposition='auto'
                ),
                row=2, col=1
            )
            fig.update_xaxes(title_text="Категория", row=2, col=1)
            fig.update_yaxes(title_text="Время (мс)", row=2, col=1)
            
            # 4. Правильные ответы
            fig.add_trace(
                go.Scatter(
                    x=category_stats.index,
                    y=category_stats["correct"],
                    mode='lines+markers',
                    name="Правильные",
                    line=dict(color='red', width=2),
                    marker=dict(size=10)
                ),
                row=2, col=2
            )
            fig.update_xaxes(title_text="Категория", row=2, col=2)
            fig.update_yaxes(title_text="Количество", row=2, col=2)
            
            fig.update_layout(height=600, showlegend=False, title_text="Анализ по категориям")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_time_analysis(self, df: pd.DataFrame):
        """Анализ времени обработки"""
        if "time_ms" not in df.columns:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Гистограмма времени
            fig = px.histogram(
                df, x="time_ms",
                nbins=20,
                title="Распределение времени обработки",
                labels={"time_ms": "Время (мс)"},
                color_discrete_sequence=['skyblue']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot по категориям
            if "true_category" in df.columns:
                fig = px.box(
                    df, x="true_category", y="time_ms",
                    title="Время обработки по категориям",
                    labels={"true_category": "Категория", "time_ms": "Время (мс)"}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Корреляция
        numeric_cols = ["time_ms", "confidence", "text_length"]
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if available_cols:
            st.markdown("#### 📈 Корреляция метрик")
            numeric_df = df[available_cols].apply(pd.to_numeric, errors='coerce')
            
            if not numeric_df.empty and len(available_cols) > 1:
                corr = numeric_df.corr()
                
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale='RdBu',
                    title="Корреляционная матрица"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def _show_confusion_matrix(self, df: pd.DataFrame):
        """Построение матрицы ошибок"""
        if "true_category" not in df.columns or "predicted_category" not in df.columns:
            return
        
        # Создаём матрицу ошибок
        y_true = df["true_category"]
        y_pred = df["predicted_category"]
        
        # Получаем все категории
        categories = sorted(set(y_true.unique()) | set(y_pred.unique()))
        
        # Создаём матрицу
        confusion_data = []
        for true_cat in categories:
            for pred_cat in categories:
                count = len(df[(df["true_category"] == true_cat) & (df["predicted_category"] == pred_cat)])
                if count > 0:
                    confusion_data.append({
                        "Истинная": true_cat,
                        "Предсказанная": pred_cat,
                        "Количество": count
                    })
        
        confusion_df = pd.DataFrame(confusion_data)
        
        if not confusion_df.empty:
            # Heatmap
            fig = px.density_heatmap(
                confusion_df,
                x="Предсказанная",
                y="Истинная",
                z="Количество",
                color_continuous_scale="Viridis",
                title="Матрица ошибок",
                text_auto=True
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Анализ основных ошибок
            st.markdown("#### 🔍 Основные ошибки классификации")
            
            # Находим наиболее частые ошибки
            errors = confusion_df[
                (confusion_df["Истинная"] != confusion_df["Предсказанная"]) &
                (confusion_df["Предсказанная"] != "ERROR")
            ].sort_values("Количество", ascending=False).head(10)
            
            if not errors.empty:
                st.dataframe(errors, use_container_width=True)
    
    def _show_examples(self, df: pd.DataFrame, emails: List[Dict]):
        """Показ примеров классификации"""
        st.markdown("#### ✅ Примеры правильной классификации")
        
        correct_examples = df[df["is_correct"] == True].head(3)
        for _, row in correct_examples.iterrows():
            email = next((e for e in emails if e["filename"] == row["filename"]), None)
            if email:
                with st.expander(f"✅ {row['filename']} (уверенность: {row['confidence']:.1%})"):
                    st.write(f"**Истинная категория:** {row['true_category']}")
                    st.write(f"**Предсказанная:** {row['predicted_category']}")
                    st.write(f"**Длина текста:** {row['text_length']} символов")
                    st.write(f"**Текст (первые 300 символов):**")
                    st.text(email['text'][:300] + "...")
        
        st.markdown("#### ❌ Примеры ошибок классификации")
        
        error_examples = df[(df["is_correct"] == False) & (df["success"] == True)].head(3)
        for _, row in error_examples.iterrows():
            email = next((e for e in emails if e["filename"] == row["filename"]), None)
            if email:
                with st.expander(f"❌ {row['filename']} (уверенность: {row['confidence']:.1%})"):
                    st.write(f"**Истинная категория:** {row['true_category']}")
                    st.write(f"**Предсказанная:** {row['predicted_category']}")
                    st.write(f"**Длина текста:** {row['text_length']} символов")
                    if row["is_undefined"]:
                        st.warning("📭 Письмо помечено как 'Не определено'")
                    st.write(f"**Текст (первые 300 символов):**")
                    st.text(email['text'][:300] + "...")
    
    def _save_benchmark_results(self, df: pd.DataFrame, total_time: float):
        """Сохранение результатов бенчмарка"""
        if df.empty:
            return
        
        # Сохраняем CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.logs_dir / f"benchmark_results_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Сохраняем метрики
        metrics = self.calculate_enhanced_metrics(df)
        metrics["total_time_seconds"] = total_time
        metrics["timestamp"] = timestamp
        
        metrics_path = self.logs_dir / f"benchmark_metrics_{timestamp}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        # Добавляем в историю
        self.results_history.append({
            "timestamp": timestamp,
            "metrics": metrics,
            "file_path": str(csv_path)
        })
        
        # Сохраняем историю
        history_path = self.logs_dir / "benchmark_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.results_history, f, ensure_ascii=False, indent=2)
        
        st.success(f"📁 Результаты сохранены:")
        st.info(f"• CSV: `{csv_path}`\n• Метрики: `{metrics_path}`\n• История: `{history_path}`")
    
    def calculate_enhanced_metrics(self, df: pd.DataFrame) -> Dict:
        """Расчёт расширенных метрик"""
        if df.empty:
            return {}
        
        total = len(df)
        correct = df["is_correct"].sum() if "is_correct" in df.columns else 0
        undefined = df["is_undefined"].sum() if "is_undefined" in df.columns else 0
        
        # Базовые метрики
        metrics = {
            "accuracy": correct / total if total > 0 else 0.0,
            "avg_time_ms": df["time_ms"].mean() if "time_ms" in df.columns else 0.0,
            "min_time_ms": df["time_ms"].min() if "time_ms" in df.columns else 0.0,
            "max_time_ms": df["time_ms"].max() if "time_ms" in df.columns else 0.0,
            "undefined_rate": (undefined / total) * 100 if total > 0 else 0.0,
            "undefined_count": int(undefined),
            "total_emails": total,
            "correct_predictions": int(correct),
            "error_rate": ((total - correct - undefined) / total) * 100 if total > 0 else 0.0,
            "success_rate": (df["success"].sum() / total) * 100 if "success" in df.columns else 0.0
        }
        
        # Метрики уверенности
        if "confidence" in df.columns:
            conf_series = pd.to_numeric(df["confidence"], errors='coerce')
            if not conf_series.empty:
                metrics.update({
                    "avg_confidence": conf_series.mean(),
                    "min_confidence": conf_series.min(),
                    "max_confidence": conf_series.max(),
                    "high_confidence_count": (conf_series > 0.7).sum(),
                    "medium_confidence_count": ((conf_series > 0.4) & (conf_series <= 0.7)).sum(),
                    "low_confidence_count": (conf_series <= 0.4).sum(),
                })
                metrics["high_confidence_pct"] = (metrics["high_confidence_count"] / total) * 100
        
        # Метрики по категориям
        if "true_category" in df.columns and "is_correct" in df.columns:
            category_acc = df.groupby("true_category")["is_correct"].mean()
            if not category_acc.empty:
                metrics["best_category"] = category_acc.idxmax()
                metrics["best_category_acc"] = category_acc.max()
                metrics["worst_category"] = category_acc.idxmin()
                metrics["worst_category_acc"] = category_acc.min()
        
        return metrics
    
    def get_benchmark_history(self) -> pd.DataFrame:
        """Получение истории бенчмарков"""
        history_path = self.logs_dir / "benchmark_history.json"
        
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Преобразуем в DataFrame
                history_data = []
                for entry in history:
                    if "metrics" in entry:
                        row = {"timestamp": entry["timestamp"]}
                        row.update(entry["metrics"])
                        history_data.append(row)
                
                return pd.DataFrame(history_data)
            except:
                return pd.DataFrame()
        
        return pd.DataFrame()
    
    def run_benchmarks(self, classifier, n_emails: int = 100, detailed: bool = True):
        """Основной метод запуска бенчмарков"""
        return self.run_classification_benchmark(classifier, n_emails, detailed)
    
    def get_detailed_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Подробная статистика по категориям"""
        if df.empty or "true_category" not in df.columns:
            return pd.DataFrame()
        
        stats = df.groupby("true_category").agg({
            "is_correct": ["count", "sum", "mean"],
            "confidence": ["mean", "std", "min", "max"],
            "time_ms": ["mean", "median", "std"],
            "is_undefined": ["sum", "mean"]
        }).round(3)
        
        stats.columns = [
            "total", "correct", "accuracy",
            "avg_conf", "std_conf", "min_conf", "max_conf",
            "avg_time", "median_time", "std_time",
            "undefined_count", "undefined_rate"
        ]
        
        stats["accuracy"] = stats["accuracy"].apply(lambda x: f"{x:.1%}")
        stats["avg_conf"] = stats["avg_conf"].apply(lambda x: f"{x:.1%}")
        stats["undefined_rate"] = stats["undefined_rate"].apply(lambda x: f"{x:.1%}")
        
        return stats

# Экспорт класса для обратной совместимости
ModelBenchmark = EnhancedModelBenchmark