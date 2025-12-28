"""
Ансамблирование моделей для повышения точности
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import logging

logger = logging.getLogger(__name__)

class EnsembleClassifier:
    """Ансамбль ML моделей для классификации"""
    
    def __init__(self, transformer_model=None):
        self.transformer_model = transformer_model
        self.tfidf = None
        self.classifiers = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Инициализация моделей
        self._init_classifiers()
    
    def _init_classifiers(self):
        """Инициализация классификаторов"""
        self.classifiers = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'naive_bayes': MultinomialNB(alpha=0.1),
            'svm': SVC(
                C=1.0,
                kernel='linear',
                probability=True,
                random_state=42
            )
        }
    
    def train(self, texts: List[str], labels: List[str], features: List[Dict] = None):
        """Обучение ансамбля"""
        logger.info("Обучение ансамбля моделей...")
        
        # 1. TF-IDF фичи
        self.tfidf = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words=None,
            min_df=2
        )
        tfidf_features = self.tfidf.fit_transform(texts)
        
        # 2. Transformer эмбеддинги (если есть модель)
        transformer_features = None
        if self.transformer_model:
            try:
                transformer_features = self.transformer_model.encode(texts)
                logger.info(f"Transformer фичи: {transformer_features.shape}")
            except Exception as e:
                logger.error(f"Ошибка получения transformer фич: {e}")
        
        # 3. Дополнительные фичи (если предоставлены)
        extra_features = None
        if features:
            extra_features = self._extract_numerical_features(features)
        
        # 4. Объединение всех фич
        combined_features = self._combine_features(
            tfidf_features, transformer_features, extra_features
        )
        
        # 5. Обучение каждой модели
        for name, clf in self.classifiers.items():
            logger.info(f"Обучение {name}...")
            try:
                clf.fit(combined_features, labels)
                logger.info(f"{name} обучен успешно")
            except Exception as e:
                logger.error(f"Ошибка обучения {name}: {e}")
        
        self.is_trained = True
        logger.info("Ансамбль моделей обучен")
    
    def predict(self, text: str, features: Dict = None) -> Dict:
        """Предсказание ансамблем"""
        if not self.is_trained:
            return {'error': 'Модель не обучена'}
        
        try:
            # 1. Получение всех фич
            tfidf_feature = self.tfidf.transform([text])
            
            transformer_feature = None
            if self.transformer_model:
                transformer_feature = self.transformer_model.encode([text])
            
            extra_feature = None
            if features:
                extra_feature = self._extract_single_numerical_features(features)
            
            # 2. Объединение фич
            combined = self._combine_features_single(
                tfidf_feature, transformer_feature, extra_feature
            )
            
            # 3. Предсказания от всех моделей
            predictions = {}
            confidences = {}
            
            for name, clf in self.classifiers.items():
                if hasattr(clf, 'predict_proba'):
                    proba = clf.predict_proba(combined)[0]
                    class_idx = np.argmax(proba)
                    confidence = proba[class_idx]
                    
                    if hasattr(clf, 'classes_'):
                        predicted_class = clf.classes_[class_idx]
                        predictions[name] = predicted_class
                        confidences[name] = confidence
            
            # 4. Голосование большинством
            if predictions:
                final_prediction = self._majority_vote(predictions, confidences)
                
                return {
                    'prediction': final_prediction['class'],
                    'confidence': final_prediction['confidence'],
                    'all_predictions': predictions,
                    'all_confidences': confidences,
                    'method': 'ensemble',
                    'model_count': len(predictions)
                }
            else:
                return {'error': 'Нет предсказаний'}
                
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")
            return {'error': str(e)}
    
    def _extract_numerical_features(self, features_list: List[Dict]) -> np.ndarray:
        """Извлечение числовых фич из списка словарей"""
        if not features_list:
            return None
        
        numerical_features = []
        for feat in features_list:
            # Извлекаем только числовые значения
            nums = [v for v in feat.values() if isinstance(v, (int, float))]
            numerical_features.append(nums)
        
        return np.array(numerical_features)
    
    def _extract_single_numerical_features(self, features: Dict) -> np.ndarray:
        """Извлечение числовых фич из одного словаря"""
        nums = [v for v in features.values() if isinstance(v, (int, float))]
        return np.array([nums])
    
    def _combine_features(self, tfidf, transformer, extra):
        """Объединение всех фич в одну матрицу"""
        import scipy.sparse
        
        features_list = [tfidf]
        
        if transformer is not None:
            features_list.append(scipy.sparse.csr_matrix(transformer))
        
        if extra is not None:
            features_list.append(scipy.sparse.csr_matrix(extra))
        
        if len(features_list) > 1:
            combined = scipy.sparse.hstack(features_list)
        else:
            combined = features_list[0]
        
        return combined
    
    def _combine_features_single(self, tfidf, transformer, extra):
        """Объединение фич для одного примера"""
        return self._combine_features(tfidf, transformer, extra)
    
    def _majority_vote(self, predictions: Dict, confidences: Dict) -> Dict:
        """Голосование большинством с учетом уверенности"""
        from collections import Counter
        
        # Подсчет голосов
        vote_counts = Counter(predictions.values())
        
        # Находим максимальное количество голосов
        max_votes = max(vote_counts.values())
        candidates = [cls for cls, count in vote_counts.items() if count == max_votes]
        
        # Если один кандидат - возвращаем его
        if len(candidates) == 1:
            selected_class = candidates[0]
        else:
            # Иначе выбираем с максимальной средней уверенностью
            avg_confidences = {}
            for cls in candidates:
                # Собираем уверенности от всех моделей для этого класса
                cls_confidences = [
                    conf for model, conf in confidences.items() 
                    if predictions[model] == cls
                ]
                avg_confidences[cls] = np.mean(cls_confidences) if cls_confidences else 0
            
            selected_class = max(avg_confidences.items(), key=lambda x: x[1])[0]
        
        # Вычисляем общую уверенность
        selected_confidences = [
            conf for model, conf in confidences.items()
            if predictions[model] == selected_class
        ]
        avg_confidence = np.mean(selected_confidences) if selected_confidences else 0.5
        
        return {
            'class': selected_class,
            'confidence': float(avg_confidence),
            'vote_count': vote_counts[selected_class],
            'total_models': len(predictions)
        }
    
    def save(self, path: str):
        """Сохранение модели"""
        joblib.dump({
            'tfidf': self.tfidf,
            'classifiers': self.classifiers,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }, path)
    
    def load(self, path: str):
        """Загрузка модели"""
        data = joblib.load(path)
        self.tfidf = data['tfidf']
        self.classifiers = data['classifiers']
        self.scaler = data['scaler']
        self.is_trained = data['is_trained']


class HybridMailClassifier:
    """Гибридный классификатор: правила + ML"""
    
    def __init__(self):
        self.rule_based_rules = self._init_rules()
        self.ml_model = None
        
    def _init_rules(self) -> Dict:
        """Инициализация правил для rule-based классификации"""
        return {
            'spam': [
                (r'выиграл|поздравляем|приз|миллион|бесплатно', 0.8),
                (r'отправьте sms|звоните сейчас|срочно', 0.7),
                (r'акция|распродажа|скидка.*%', 0.6)
            ],
            'complaint': [
                (r'жалоб|недовол|претензи|проблем', 0.8),
                (r'ужасно|кошмар|разочарован', 0.7),
                (r'верните деньги|требую|напишу в', 0.6)
            ],
            'business': [
                (r'предложен|сотрудничеств|партнерств|договор', 0.8),
                (r'коммерческ|встреч|переговоры', 0.7),
                (r'инвестици|финансирован', 0.6)
            ],
            'support': [
                (r'помощ|поддержк|сбо|ошибк|не работает', 0.8),
                (r'как.*использовать|инструкция|руководств', 0.7),
                (r'вопрос.*ответ|техническ', 0.6)
            ]
        }
    
    def rule_based_classify(self, text: str) -> Dict:
        """Rule-based классификация"""
        text_lower = text.lower()
        scores = {}
        
        for category, rules in self.rule_based_rules.items():
            category_score = 0
            for pattern, weight in rules:
                if re.search(pattern, text_lower):
                    category_score += weight
            
            if category_score > 0:
                scores[category] = min(category_score / len(rules), 1.0)
        
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])
            return {
                'category': best_category[0],
                'confidence': best_category[1],
                'method': 'rule_based',
                'all_scores': scores
            }
        
        return {'category': 'unknown', 'confidence': 0, 'method': 'rule_based'}
    
    def hybrid_classify(self, text: str, ml_prediction: Dict) -> Dict:
        """Гибридная классификация: правила + ML"""
        rule_result = self.rule_based_classify(text)
        
        # Если правило уверено (conf > 0.7), используем его
        if rule_result['confidence'] > 0.7:
            rule_result['method'] = 'hybrid_rule'
            return rule_result
        
        # Иначе используем ML
        ml_prediction['method'] = 'hybrid_ml'
        return ml_prediction