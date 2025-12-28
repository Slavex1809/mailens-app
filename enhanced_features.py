"""
Улучшенная обработка текста и извлечение фич для ML модели
"""

import re
import numpy as np
from typing import Dict, List, Tuple
import emoji
from langdetect import detect, LangDetectException
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import logging

logger = logging.getLogger(__name__)

class EnhancedTextProcessor:
    """Продвинутая очистка и обработка текста"""
    
    @staticmethod
    def clean_email_text(text: str) -> str:
        """Улучшенная очистка email текста"""
        if not text:
            return ""
        
        # Удаляем стандартные email заголовки и подписи
        lines = text.split('\n')
        clean_lines = []
        
        signature_keywords = [
            'с уважением', 'best regards', 'kind regards', 'sincerely',
            'искренне ваш', 'с наилучшими пожеланиями', 'спасибо',
            'sent from', 'отправлено с', 'дата:', 'date:',
            'тел.', 'phone:', 'email:', 'e-mail:'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Пропускаем подписи и контактную информацию
            if any(keyword in line_lower for keyword in signature_keywords):
                continue
            
            # Пропускаем пустые строки и разделители
            if not line.strip() or line.strip().startswith('---'):
                continue
            
            # Удаляем автоматические сообщения
            if any(auto in line_lower for auto in [
                'автоматически сгенерирован', 'auto-generated',
                'не отвечайте на это письмо', 'do not reply'
            ]):
                continue
            
            clean_lines.append(line)
        
        # Объединяем обратно
        clean_text = '\n'.join(clean_lines)
        
        # Удаляем HTML теги
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        
        # Удаляем специальные символы, но сохраняем пунктуацию
        clean_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', clean_text)
        
        # Удаляем URL
        clean_text = re.sub(r'https?://\S+|www\.\S+', '', clean_text)
        
        # Удаляем email адреса
        clean_text = re.sub(r'\S+@\S+\.\S+', '', clean_text)
        
        # Нормализуем пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Определение языка текста"""
        try:
            if len(text) < 10:
                return 'unknown'
            return detect(text)
        except LangDetectException:
            return 'unknown'
    
    @staticmethod
    def extract_advanced_features(text: str) -> Dict:
        """Извлечение продвинутых фич из текста"""
        features = {}
        
        # Базовые статистики
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(sent_tokenize(text) if text else [])
        
        # Стилистические фичи
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['digit_count'] = sum(c.isdigit() for c in text)
        features['has_emoji'] = bool(emoji.get_emoji_regexp().search(text))
        
        # Структурные фичи (специфичные для email)
        text_lower = text.lower()
        features['has_greeting'] = any(g in text_lower for g in [
            'уважаемый', 'уважаемая', 'здравствуйте', 'добрый день',
            'привет', 'дорогой', 'дорогая', 'hello', 'hi', 'dear'
        ])
        
        features['has_thanks'] = any(t in text_lower for t in [
            'спасибо', 'благодарю', 'thank you', 'thanks', 'благодарность'
        ])
        
        features['has_urgent'] = any(u in text_lower for u in [
            'срочно', 'urgent', 'asap', 'немедленно', 'важно', 'important'
        ])
        
        features['has_meeting'] = any(m in text_lower for m in [
            'встреча', 'звонок', 'совещание', 'конференция',
            'meeting', 'call', 'conference'
        ])
        
        features['has_date'] = bool(re.search(r'\d{1,2}[-./]\d{1,2}[-./]\d{2,4}', text))
        features['has_time'] = bool(re.search(r'\d{1,2}[:]\d{2}', text))
        features['has_money'] = bool(re.search(r'\$\d+|€\d+|£\d+|\d+\s*(руб|р\.|долл|евро)', text_lower))
        
        # Эмоциональные фичи
        positive_words = ['отличн', 'хорош', 'прекрасн', 'супер', 'great', 'good', 'excellent']
        negative_words = ['плох', 'ужасн', 'кошмар', 'разочарован', 'bad', 'terrible', 'disappointed']
        
        features['positive_score'] = sum(text_lower.count(word) for word in positive_words)
        features['negative_score'] = sum(text_lower.count(word) for word in negative_words)
        features['sentiment_ratio'] = (features['positive_score'] - features['negative_score']) / max(features['word_count'], 1)
        
        # Формальность
        formal_words = ['прошу', 'предлагаю', 'сообщаю', 'уведомляю', 'информирую']
        informal_words = ['привет', 'пока', 'ок', 'ладно', 'чё', 'ага']
        
        features['formal_score'] = sum(text_lower.count(word) for word in formal_words)
        features['informal_score'] = sum(text_lower.count(word) for word in informal_words)
        features['formality_ratio'] = features['formal_score'] / max(features['formal_score'] + features['informal_score'], 1)
        
        return features
    
    @staticmethod
    def calculate_text_complexity(text: str) -> float:
        """Расчет сложности текста"""
        if not text or len(text.split()) < 10:
            return 0.0
        
        try:
            # Средняя длина слова
            words = text.split()
            avg_word_len = np.mean([len(w) for w in words])
            
            # Средняя длина предложения
            sentences = sent_tokenize(text)
            avg_sent_len = np.mean([len(s.split()) for s in sentences])
            
            # Разнообразие слов (тип/токен ratio)
            unique_words = len(set(words))
            ttr = unique_words / len(words) if words else 0
            
            # Комплексность = комбинация факторов
            complexity = (avg_word_len * 0.3 + avg_sent_len * 0.4 + ttr * 0.3) / 10
            
            return min(complexity, 1.0)
            
        except:
            return 0.5


class FeatureEngineer:
    """Инженерия фич для ML модели"""
    
    def __init__(self):
        self.processor = EnhancedTextProcessor()
        
    def create_feature_vector(self, text: str) -> Dict:
        """Создание полного вектора фич"""
        # Очистка текста
        clean_text = self.processor.clean_email_text(text)
        
        # Основные фичи
        features = self.processor.extract_advanced_features(clean_text)
        
        # Дополнительные расчеты
        features['text_complexity'] = self.processor.calculate_text_complexity(clean_text)
        features['language'] = self.processor.detect_language(clean_text)
        features['is_short'] = features['word_count'] < 20
        features['is_long'] = features['word_count'] > 500
        features['has_questions'] = features['question_count'] > 0
        features['is_emotional'] = features['exclamation_count'] > 2
        
        # Категориальные фичи
        features['text_type'] = self._classify_text_type(features)
        
        return features
    
    def _classify_text_type(self, features: Dict) -> str:
        """Классификация типа текста по фичам"""
        if features['has_urgent'] and features['exclamation_count'] > 1:
            return 'urgent'
        elif features['has_meeting'] and features['has_date']:
            return 'scheduling'
        elif features['has_money'] and features['formal_score'] > 0:
            return 'financial'
        elif features['negative_score'] > features['positive_score']:
            return 'complaint'
        elif features['has_thanks'] and features['positive_score'] > 0:
            return 'appreciation'
        elif features['is_short'] and features['has_emoji']:
            return 'informal'
        else:
            return 'general'
    
    def get_feature_names(self) -> List[str]:
        """Возвращает список всех фич"""
        return [
            'char_count', 'word_count', 'sentence_count',
            'exclamation_count', 'question_count', 'uppercase_ratio',
            'digit_count', 'has_emoji', 'has_greeting', 'has_thanks',
            'has_urgent', 'has_meeting', 'has_date', 'has_time',
            'has_money', 'positive_score', 'negative_score',
            'sentiment_ratio', 'formal_score', 'informal_score',
            'formality_ratio', 'text_complexity', 'is_short',
            'is_long', 'has_questions', 'is_emotional'
        ]