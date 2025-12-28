"""
UI.PY - Интеллектуальный классификатор писем
"""

import streamlit as st
import pandas as pd
import json
import time
import os
import warnings
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

# Настройка страницы
st.set_page_config(
    page_title="Intelligent Email Classifier",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': "Intelligent Email Classifier with Zero-shot & Few-shot learning"
    }
)

# ---------- КОНФИГУРАЦИЯ ----------
CONFIG_DIR = Path("config")
CONFIG_DIR.mkdir(exist_ok=True)
CATEGORIES_FILE = CONFIG_DIR / "categories.json"
BENCHMARK_RESULTS_FILE = CONFIG_DIR / "benchmark_results.csv"

DEFAULT_CATEGORIES = [
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

# Загрузка категорий
if CATEGORIES_FILE.exists():
    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            CATEGORIES = json.load(f)
    except:
        CATEGORIES = DEFAULT_CATEGORIES.copy()
else:
    CATEGORIES = DEFAULT_CATEGORIES.copy()
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(CATEGORIES, f, ensure_ascii=False, indent=2)

# Инициализация сессионного состояния
if 'categories' not in st.session_state:
    st.session_state.categories = CATEGORIES.copy()
if 'threshold' not in st.session_state:
    st.session_state.threshold = 35
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = None

# Загрузка ML моделей
ML_AVAILABLE = False
classifier = None
email_processor = None

try:
    from core import email_processor, classifier
    if classifier:
        classifier.set_categories(st.session_state.categories)
        classifier.set_threshold(st.session_state.threshold / 100.0)
        ML_AVAILABLE = True
except Exception as e:
    st.sidebar.warning(f"⚠️ ML модели не загружены: {type(e).__name__}")

# ---------- СТИЛИ ----------
st.markdown("""
<style>
    /* Основные цвета */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray: #6b7280;
        --light-gray: #f3f4f6;
    }
    
    /* Хедер */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #dbeafe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        opacity: 0.9;
        margin: 0.75rem 0 0;
        font-size: 1.2rem;
        max-width: 800px;
    }
    
    /* Карточки */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Бейджи категорий */
    .category-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 4px;
        transition: all 0.2s;
    }
    
    .business { background: #dcfce7; color: #166534; border: 2px solid #86efac; }
    .complaint { background: #fee2e2; color: #b91c1c; border: 2px solid #fca5a5; }
    .support { background: #dbeafe; color: #1e40af; border: 2px solid #93c5fd; }
    .finance { background: #ede9fe; color: #5b21b6; border: 2px solid #c4b5fd; }
    .spam { background: #ffedd5; color: #c2410c; border: 2px solid #fdba74; }
    .hr { background: #fef3c7; color: #92400e; border: 2px solid #fcd34d; }
    .legal { background: #e0e7ff; color: #4338ca; border: 2px solid #a5b4fc; }
    .news { background: #f0f9ff; color: #0c4a6e; border: 2px solid #7dd3fc; }
    .marketing { background: #fce7f3; color: #9d174d; border: 2px solid #f9a8d4; }
    .personal { background: #ecfdf5; color: #047857; border: 2px solid #6ee7b7; }
    .undefined { background: #f1f5f9; color: #475569; border: 2px solid #cbd5e1; }
    
    /* Прогресс-бар уверенности */
    .confidence-container {
        margin: 1.5rem 0;
    }
    
    .confidence-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        color: #4b5563;
    }
    
    .confidence-bar {
        height: 12px;
        background: #e5e7eb;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, var(--success), var(--primary));
        transition: width 1s ease-out;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.85rem 1.75rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        border-bottom: 3px solid var(--primary);
    }
    
    /* Инпут файлов */
    .stFileUploader > div {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 2rem;
        background: #f9fafb;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary);
        background: #f0f9ff;
    }
</style>
""", unsafe_allow_html=True)

# ---------- ХЕДЕР ----------
st.markdown("""
<div class="main-header">
    <h1>📧 Intelligent Email Classifier</h1>
    <p>Zero-shot & Few-shot классификация писем с расширенной аналитикой и бенчмаркингом</p>
</div>
""", unsafe_allow_html=True)

# ---------- БОКОВАЯ ПАНЕЛЬ ----------
with st.sidebar:
    st.markdown("## ⚙️ Конфигурация")
    
    # Порог уверенности
    st.markdown("### 🎯 Порог уверенности")
    threshold = st.slider(
        "Минимальная уверенность для классификации",
        min_value=10,
        max_value=90,
        value=st.session_state.threshold,
        step=5,
        format="%d%%",
        help="При уверенности ниже этого значения письмо помечается как 'Не определена'",
        key="threshold_slider"
    )
    
    if ML_AVAILABLE and threshold != st.session_state.threshold:
        st.session_state.threshold = threshold
        classifier.set_threshold(threshold / 100.0)
        st.success(f"Порог установлен: {threshold}%")
    
    # Категории
    st.markdown("### 🏷️ Категории")
    st.caption("Управление категориями для классификации")
    
    # Список категорий с возможностью удаления
    for i, category in enumerate(st.session_state.categories[:]):
        col1, col2 = st.columns([5, 1])
        with col1:
            # Определяем класс для бейджа
            badge_class = "undefined"
            if "делов" in category.lower(): badge_class = "business"
            elif "жалоб" in category.lower(): badge_class = "complaint"
            elif "поддерж" in category.lower(): badge_class = "support"
            elif "финанс" in category.lower(): badge_class = "finance"
            elif "спам" in category.lower() or "реклам" in category.lower(): badge_class = "spam"
            elif "hr" in category.lower() or "рекрут" in category.lower(): badge_class = "hr"
            elif "юрид" in category.lower(): badge_class = "legal"
            elif "новост" in category.lower(): badge_class = "news"
            elif "маркетинг" in category.lower() or "продаж" in category.lower(): badge_class = "marketing"
            elif "личн" in category.lower(): badge_class = "personal"
            
            st.markdown(f'<div class="category-badge {badge_class}">{category}</div>', unsafe_allow_html=True)
        
        with col2:
            if category != "Не определена":
                if st.button("🗑️", key=f"del_{i}", help="Удалить категорию"):
                    st.session_state.categories.remove(category)
                    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.categories, f, ensure_ascii=False, indent=2)
                    if ML_AVAILABLE:
                        classifier.set_categories(st.session_state.categories)
                    st.rerun()
    
    # Добавление новой категории
    st.markdown("---")
    new_category = st.text_input(
        "Новая категория",
        placeholder="Например: Коммерческое предложение",
        key="new_category_input"
    )
    
    col_add, col_reset = st.columns(2)
    with col_add:
        if st.button("➕ Добавить", type="primary", use_container_width=True):
            if new_category and new_category.strip() not in st.session_state.categories:
                st.session_state.categories.append(new_category.strip())
                with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.categories, f, ensure_ascii=False, indent=2)
                if ML_AVAILABLE:
                    classifier.set_categories(st.session_state.categories)
                st.success(f"Категория '{new_category.strip()}' добавлена")
                st.rerun()
    
    with col_reset:
        if st.button("🔄 Сбросить", use_container_width=True):
            st.session_state.categories = DEFAULT_CATEGORIES.copy()
            with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.categories, f, ensure_ascii=False, indent=2)
            if ML_AVAILABLE:
                classifier.set_categories(st.session_state.categories)
            st.rerun()
    
    # Информация о системе
    st.markdown("---")
    st.markdown("### 📊 Информация о системе")
    
    if ML_AVAILABLE:
        model_info = classifier.get_model_info()
        st.metric("ML модель", model_info.get('model_name', 'Demo'))
        st.metric("Категории", model_info.get('categories_count', 0))
        st.metric("Порог", f"{threshold}%")
    else:
        st.warning("ML модель в демо-режиме")
    
    # Проверка тестовых данных
    test_dir = Path("test_emails")
    if test_dir.exists():
        labels_file = test_dir / "labels.csv"
        if labels_file.exists():
            try:
                df_labels = pd.read_csv(labels_file, encoding='utf-8-sig')
                st.success(f"✅ Тестовых писем: {len(df_labels)}")
            except:
                st.info("📁 Папка test_emails найдена")
        else:
            st.warning("⚠️ labels.csv не найден")

# ---------- ОСНОВНОЕ СОДЕРЖИМОЕ ----------
tab1, tab2, tab3 = st.tabs(["📤 Анализ письма", "🎯 Few-Shot обучение", "📈 Бенчмаркинг"])

# ---------- ВКЛАДКА 1: Анализ письма ----------
with tab1:
    st.markdown("## 📤 Анализ письма")
    
    col_upload, col_paste = st.columns(2)
    
    with col_upload:
        st.markdown("### 📎 Загрузка файла")
        uploaded_file = st.file_uploader(
            "Загрузите email файл",
            type=["eml", "txt", "msg"],
            help="Поддерживаются форматы: .eml, .txt, .msg",
            label_visibility="collapsed"
        )
    
    with col_paste:
        st.markdown("### 📝 Вставка текста")
        manual_text = st.text_area(
            "Или вставьте текст письма",
            height=150,
            placeholder="Вставьте текст письма здесь...",
            label_visibility="collapsed"
        )
    
    # Определение источника текста
    text_to_classify = ""
    source_type = "none"
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue()
            # Пробуем разные кодировки
            for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251']:
                try:
                    text_to_classify = content.decode(encoding)
                    break
                except:
                    continue
            else:
                text_to_classify = content.decode('utf-8', errors='ignore')
            
            source_type = "file"
            st.success(f"✅ Файл загружен: {uploaded_file.name} ({len(content)} байт)")
        except Exception as e:
            st.error(f"❌ Ошибка чтения файла: {e}")
    
    elif manual_text and len(manual_text.strip()) > 10:
        text_to_classify = manual_text.strip()
        source_type = "text"
        st.success(f"✅ Текст принят ({len(text_to_classify)} символов)")
    
    # Классификация
    if text_to_classify and source_type != "none":
        st.markdown("---")
        st.markdown("### 🧠 Результат классификации")
        
        if st.button("🚀 Запустить классификацию", type="primary", use_container_width=True):
            with st.spinner("Анализирую письмо..."):
                start_time = time.time()
                
                if ML_AVAILABLE:
                    result = classifier.classify(text_to_classify, top_n=3)
                else:
                    # Демо-режим
                    result = {
                        'predicted_category': "Не определена",
                        'confidence': 0.5,
                        'is_undefined': True,
                        'top_categories': [],
                        'method': 'demo-mode'
                    }
                
                processing_time = time.time() - start_time
                
                # Отображение результатов
                col_cat, col_conf, col_time = st.columns(3)
                
                with col_cat:
                    category = result.get('predicted_category', 'Не определена')
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{category}</div><div class="metric-label">Категория</div></div>', unsafe_allow_html=True)
                
                with col_conf:
                    confidence = result.get('confidence', 0.0)
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{confidence:.1%}</div><div class="metric-label">Уверенность</div></div>', unsafe_allow_html=True)
                
                with col_time:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{processing_time:.3f}s</div><div class="metric-label">Время обработки</div></div>', unsafe_allow_html=True)
                
                # Прогресс-бар уверенности
                st.markdown('<div class="confidence-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="confidence-label"><span>Уверенность классификации</span><span>{confidence:.1%}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="confidence-bar"><div class="confidence-fill" style="width: {confidence*100}%"></div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Статус
                is_undefined = result.get('is_undefined', True)
                status = "🟡 Не определена" if is_undefined else "🟢 Классифицировано"
                status_color = "warning" if is_undefined else "success"
                st.markdown(f"**Статус:** <span style='color: var(--{status_color})'>{status}</span>", unsafe_allow_html=True)
                
                # Метод классификации
                method = result.get('method', 'unknown')
                st.caption(f"Метод: {method}")
                
                # Топ категории
                if 'top_categories' in result and result['top_categories']:
                    st.markdown("### 🏆 Топ категории")
                    top_df = pd.DataFrame(result['top_categories'])
                    st.dataframe(top_df, use_container_width=True)
                    
                    # Визуализация
                    fig = px.bar(
                        top_df, 
                        x='category', 
                        y='score',
                        color='score',
                        color_continuous_scale='Viridis',
                        title='Уверенность по категориям'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

# ---------- ВКЛАДКА 2: Few-Shot обучение ----------
with tab2:
    st.markdown("## 🎯 Few-Shot обучение")
    
    if not ML_AVAILABLE:
        st.warning("⚠️ Few-Shot обучение доступно только при загруженной ML модели")
    else:
        st.info("Добавьте примеры писем для улучшения классификации по конкретным категориям")
        
        col_category, col_example = st.columns([1, 2])
        
        with col_category:
            selected_category = st.selectbox(
                "Выберите категорию",
                options=st.session_state.categories,
                key="fewshot_category"
            )
        
        with col_example:
            example_text = st.text_area(
                "Текст примера письма",
                height=150,
                placeholder="Введите текст письма, который относится к выбранной категории...",
                key="fewshot_text"
            )
        
        if st.button("➕ Добавить пример", type="primary", use_container_width=True):
            if example_text and len(example_text.strip()) > 20:
                try:
                    classifier.add_few_shot_example(selected_category, example_text)
                    st.success(f"✅ Пример добавлен для категории '{selected_category}'")
                    
                    # Показываем статистику
                    model_info = classifier.get_model_info()
                    few_shot_stats = model_info.get('few_shot_examples', {})
                    
                    st.markdown("### 📊 Статистика Few-Shot примеров")
                    stats_df = pd.DataFrame([
                        {"Категория": cat, "Примеров": count}
                        for cat, count in few_shot_stats.items()
                    ])
                    
                    if not stats_df.empty:
                        st.dataframe(stats_df, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Ошибка добавления примера: {e}")
        
        # Очистка кэша
        st.markdown("---")
        if st.button("🧹 Очистить кэш классификатора", use_container_width=True):
            try:
                classifier.clear_cache()
                st.success("✅ Кэш очищен")
            except:
                st.info("Кэш не поддерживается в демо-режиме")

# ---------- ВКЛАДКА 3: Бенчмаркинг ----------
with tab3:
    st.markdown("## 📈 Бенчмаркинг системы")
    
    # Проверка тестовых данных
    test_dir = Path("test_emails")
    labels_found = False
    
    if test_dir.exists():
        labels_file = test_dir / "labels.csv"
        if labels_file.exists():
            try:
                df_check = pd.read_csv(labels_file, encoding='utf-8-sig')
                total_emails = len(df_check)
                labels_found = True
                
                st.success(f"✅ Найдено тестовых писем: {total_emails}")
                
                # Показываем распределение категорий
                st.markdown("### 📊 Распределение категорий в тестовых данных")
                category_dist = df_check['true_category'].value_counts()
                
                col_dist1, col_dist2 = st.columns(2)
                
                with col_dist1:
                    fig_dist = px.pie(
                        values=category_dist.values,
                        names=category_dist.index,
                        title='Распределение категорий',
                        hole=0.4
                    )
                    fig_dist.update_layout(height=300)
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                with col_dist2:
                    st.dataframe(category_dist, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Ошибка чтения labels.csv: {e}")
        else:
            st.warning("⚠️ Файл labels.csv не найден в папке test_emails")
    else:
        st.info("📁 Папка test_emails не найдена. Бенчмарк будет использовать демо-данные.")
    
    # Настройки бенчмарка
    st.markdown("### ⚙️ Настройки бенчмарка")
    
    col_samples, col_mode = st.columns(2)
    
    with col_samples:
        if labels_found:
            max_samples = min(total_emails, 500)
            num_samples = st.slider(
                "Количество писем для теста",
                min_value=10,
                max_value=max_samples,
                value=min(100, max_samples),
                step=10,
                help=f"Всего доступно: {total_emails} писем"
            )
        else:
            num_samples = st.slider(
                "Количество писем для теста",
                min_value=10,
                max_value=200,
                value=50,
                step=10
            )
    
    with col_mode:
        benchmark_mode = st.radio(
            "Режим тестирования",
            ["Полный тест", "Быстрый тест"],
            horizontal=True,
            help="Полный тест включает сохранение результатов и детальную статистику"
        )
    
    # Кнопка запуска бенчмарка
    if st.button("🚀 Запустить бенчмарк", type="primary", use_container_width=True):
        if not ML_AVAILABLE:
            st.warning("⚠️ ML модель не загружена. Бенчмарк будет работать в демо-режиме.")
        
        with st.spinner(f"Запуск бенчмарка на {num_samples} письмах..."):
            try:
                from benchmark import ModelBenchmark
                
                # Запуск бенчмарка
                benchmark = ModelBenchmark("test_emails")
                results_df = benchmark.run_classification_benchmark(classifier, num_samples)
                
                if results_df.empty:
                    st.error("❌ Бенчмарк вернул пустые результаты")
                else:
                    # Сохранение в session state
                    st.session_state.benchmark_results = results_df
                    
                    # Расчёт метрик
                    metrics = benchmark.calculate_metrics(results_df)
                    
                    # Отображение метрик
                    st.markdown("### 📊 Результаты бенчмарка")
                    
                    col_acc, col_time, col_undef, col_conf = st.columns(4)
                    
                    with col_acc:
                        accuracy = metrics['accuracy']
                        accuracy_color = "success" if accuracy > 0.7 else "warning" if accuracy > 0.5 else "danger"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value" style="color: var(--{accuracy_color})">{accuracy:.1%}</div>
                            <div class="metric-label">Точность</div>
                            <div style="font-size: 0.8rem; color: var(--gray); margin-top: 0.5rem;">
                                {metrics['correct_predictions']}/{metrics['total_emails']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_time:
                        avg_time = metrics['avg_time_ms']
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{avg_time:.1f} мс</div>
                            <div class="metric-label">Среднее время</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_undef:
                        undef_rate = metrics['undefined_rate']
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{undef_rate:.1f}%</div>
                            <div class="metric-label">Не определено</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_conf:
                        avg_conf = metrics.get('avg_confidence', 0.0)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{avg_conf:.1%}</div>
                            <div class="metric-label">Средняя уверенность</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Детальная статистика
                    st.markdown("### 📋 Детальная статистика")
                    
                    # Матрица ошибок
                    st.markdown("#### Матрица ошибок")
                    if 'true_category' in results_df.columns and 'predicted_category' in results_df.columns:
                        confusion_data = results_df.groupby(['true_category', 'predicted_category']).size().reset_index(name='count')
                        fig_confusion = px.density_heatmap(
                            confusion_data,
                            x='predicted_category',
                            y='true_category',
                            z='count',
                            color_continuous_scale='Viridis',
                            title='Матрица классификации'
                        )
                        fig_confusion.update_layout(height=400)
                        st.plotly_chart(fig_confusion, use_container_width=True)
                    
                    # Топ-10 результатов
                    st.markdown("#### Топ-10 результатов")
                    display_df = results_df[['filename', 'true_category', 'predicted_category', 'confidence', 'time_ms', 'is_correct']].head(10)
                    st.dataframe(
                        display_df.style.applymap(
                            lambda x: 'background-color: #dcfce7' if x == True else ('background-color: #fee2e2' if x == False else ''),
                            subset=['is_correct']
                        ),
                        use_container_width=True
                    )
                    
                    # Распределение времени обработки
                    st.markdown("#### Распределение времени обработки")
                    fig_time = px.histogram(
                        results_df,
                        x='time_ms',
                        nbins=20,
                        title='Время обработки писем',
                        labels={'time_ms': 'Время (мс)'}
                    )
                    fig_time.update_layout(height=300)
                    st.plotly_chart(fig_time, use_container_width=True)
                    
                    # Скачивание результатов
                    st.markdown("---")
                    csv_data = results_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Скачать полные результаты",
                        data=csv_data,
                        file_name=f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            except Exception as e:
                st.error(f"❌ Ошибка выполнения бенчмарка: {str(e)}")
                st.exception(e)
    
    # Загрузка предыдущих результатов
    st.markdown("---")
    st.markdown("### 📂 Загрузка сохранённых результатов")
    
    if BENCHMARK_RESULTS_FILE.exists():
        try:
            saved_results = pd.read_csv(BENCHMARK_RESULTS_FILE, encoding='utf-8-sig')
            st.success(f"✅ Найден сохранённый файл с {len(saved_results)} результатами")
            
            if st.button("📊 Загрузить сохранённые результаты", use_container_width=True):
                st.session_state.benchmark_results = saved_results
                st.rerun()
        except:
            st.info("Нет доступных сохранённых результатов")

# ---------- ФУТЕР ----------
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("🤖 Intelligent Email Classifier")
    st.caption("Zero-shot & Few-shot классификация")

with col_footer2:
    st.caption("📧 Поддержка форматов: .eml, .txt, .msg")
    st.caption("🌍 Мультиязычная обработка")

with col_footer3:
    st.caption("⚡ Быстрая обработка")
    st.caption("📊 Детальная аналитика")

# Отображение загруженных результатов бенчмарка
if st.session_state.benchmark_results is not None:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Последние результаты")
    
    results_df = st.session_state.benchmark_results
    accuracy = results_df['is_correct'].mean() if 'is_correct' in results_df.columns else 0
    
    st.sidebar.metric("Последняя точность", f"{accuracy:.1%}")
    st.sidebar.caption(f"На основе {len(results_df)} писем")
    
    if st.sidebar.button("Очистить результаты", use_container_width=True):
        st.session_state.benchmark_results = None
        st.rerun()