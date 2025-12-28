import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Добавляем папку benchmark в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'benchmark'))

from benchmark import StreamlitBenchmark
# Импортируйте вашу реальную функцию обработки
from utils.email_processor import process_email

def main():
    st.set_page_config(
        page_title="Mailens App - Бенчмарк",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📊 Mailens App - Бенчмарк обработки писем")
    
    # Сайдбар с настройками
    with st.sidebar:
        st.header("Настройки бенчмарка")
        
        num_emails = st.slider(
            "Количество тестовых писем",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            help="Выберите количество писем для тестирования"
        )
        
        test_mode = st.selectbox(
            "Режим тестирования",
            ["Быстрый (10 писем)", "Стандартный (50 писем)", "Полный (100+ писем)"],
            index=1
        )
        
        if test_mode == "Быстрый (10 писем)":
            num_emails = 10
        elif test_mode == "Стандартный (50 писем)":
            num_emails = 50
        else:
            num_emails = 100
        
        st.divider()
        
        if st.button("🚀 Запустить бенчмарк", type="primary", use_container_width=True):
            st.session_state.run_benchmark = True
        else:
            st.session_state.run_benchmark = False
    
    # Основное содержимое
    if st.session_state.get('run_benchmark', False):
        # Инициализация бенчмарка
        benchmark = StreamlitBenchmark(test_emails_dir="test_emails")
        
        # Запуск бенчмарка
        with st.spinner("Запуск бенчмарка..."):
            results_df = benchmark.run_benchmark_streamlit(
                processing_func=process_email,  # Ваша функция
                num_emails=num_emails
            )
        
        # Расчет метрик
        metrics = benchmark.calculate_metrics(results_df)
        
        # Отображение дашборда
        benchmark.display_metrics_dashboard(metrics)
        
        # Визуализации
        benchmark.create_streamlit_visualizations(results_df)
        
        # Экспорт
        benchmark.generate_export_data(results_df, metrics)
        
        # Очистка состояния
        if st.button("🔄 Сбросить и начать заново"):
            st.session_state.run_benchmark = False
            st.rerun()
    else:
        # Стартовый экран
        st.markdown("""
        ## Добро пожаловать в бенчмарк Mailens App!
        
        Этот инструмент позволяет протестировать производительность обработки писем.
        
        ### Что будет измеряться:
        - ⏱️ **Время обработки** каждого письма
        - ✅ **Успешность** обработки
        - 📈 **Пропускная способность** (писем в секунду)
        - 📊 **Зависимость** времени от длины письма
        - 🎯 **Статистика** по приоритетам и вложениям
        
        ### Как использовать:
        1. Выберите количество писем в боковой панели
        2. Нажмите кнопку "Запустить бенчмарк"
        3. Наблюдайте за прогрессом в реальном времени
        4. Анализируйте результаты и графики
        5. Экспортируйте данные для дальнейшего анализа
        
        ### Готовы начать?
        """)
        
        if st.button("🚀 Начать бенчмарк", type="primary"):
            st.session_state.run_benchmark = True
            st.rerun()

if __name__ == "__main__":
    main()