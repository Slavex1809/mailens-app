import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class ResultVisualizer:
    """Визуализация результатов классификации"""
    
    @staticmethod
    def create_confidence_chart(predictions: dict, threshold: float = 0.3):
        """Создание графика уверенности"""
        if not predictions.get('all_scores'):
            return None
        
        categories = list(predictions['all_scores'].keys())
        scores = list(predictions['all_scores'].values())
        
        # Цвета: зеленый для лучшей, синий для остальных, красный для ниже порога
        colors = []
        for score in scores:
            if score == max(scores):
                colors.append('#10b981')  # зеленый для лучшей
            elif score < threshold:
                colors.append('#ef4444')  # красный для ниже порога
            else:
                colors.append('#3b82f6')  # синий для остальных
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=scores,
                marker_color=colors,
                text=[f'{s:.1%}' for s in scores],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Уверенность: %{y:.2%}<extra></extra>'
            )
        ])
        
        # Добавляем линию порога
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Порог: {threshold:.0%}",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title="📊 Распределение уверенности по категориям",
            xaxis_title="Категории",
            yaxis_title="Уверенность",
            yaxis_tickformat=".0%",
            height=500,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_similarity_heatmap(predictions: dict):
        """Тепловая карта сходства (если есть несколько текстов)"""
        if 'all_similarities' not in predictions:
            return None
        
        similarities = predictions['all_similarities']
        categories = list(similarities.keys())
        values = list(similarities.values())
        
        # Нормализуем значения для тепловой карты
        norm_values = (values - np.min(values)) / (np.max(values) - np.min(values) + 1e-8)
        
        fig = go.Figure(data=go.Heatmap(
            z=[norm_values],
            x=categories,
            y=['Сходство'],
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='<b>%{x}</b><br>Сходство: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="🔥 Тепловая карта сходства",
            height=200,
            xaxis_title="Категории",
            yaxis_title=""
        )
        
        return fig
    
    @staticmethod
    def create_model_info_card(model_info: dict):
        """Карточка с информацией о модели"""
        html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">
            <h4 style="margin:0;">🤖 Информация о модели</h4>
            <p style="margin:5px 0;"><b>Модель:</b> {model_info.get('name', 'Неизвестно')}</p>
            <p style="margin:5px 0;"><b>Устройство:</b> {model_info.get('device', 'CPU')}</p>
            <p style="margin:5px 0;"><b>Категорий:</b> {model_info.get('categories_count', 0)}</p>
            <p style="margin:5px 0;"><b>Порог:</b> {model_info.get('threshold', 0.3):.0%}</p>
        </div>
        """
        return html