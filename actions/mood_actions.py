
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from transformers import pipeline
import random
import re  # Добавьте эту строку
import logging
from typing import Text, Dict, List, Any

# Инициализация логгера
logger = logging.getLogger(__name__)

# Загрузка модели для анализа тональности
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="blanchefort/rubert-base-cased-sentiment"
)

class ActionAnalyzeMood(Action):
    def name(self) -> Text:
        return "action_analyze_mood"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        text = tracker.latest_message.get('text', '')
        cleaned_text = self.preprocess_text(text)

        try:
            result = sentiment_analyzer(cleaned_text, truncation=True)[0]
            label = result['label']
            score = result['score']

            # Детализированные ответы
            responses = {
                'POSITIVE': {
                    'high_confidence': [
                        "Ваша радость заразительна! 🌈 Чем порадовать вас ещё?",
                        "Так держать! Отличное настроение - залог успеха!"
                    ],
                    'low_confidence': [
                        "Кажется, вы в хорошем расположении духа?",
                        "Уловил позитивные нотки. Расскажите подробнее?"
                    ]
                },
                'NEGATIVE': {
                    'high_confidence': [
                        "Вижу, что вам тяжело... Хотите об этом поговорить? 💔",
                        "Мне жаль, что вы так себя чувствуете. Чем помочь?"
                    ],
                    'low_confidence': [
                        "Кажется, что-то беспокоит? Можете поделиться?",
                        "Заметил негативные ноты. Нужна поддержка?"
                    ]
                },
                'NEUTRAL': [
                    "Понял вас. Хотите обсудить что-то конкретное?",
                    "Расскажите больше, чтобы я лучше понял ваше состояние."
                ]
            }

            # Динамический выбор ответа
            if label in ['POSITIVE', 'NEGATIVE']:
                confidence_key = 'high_confidence' if score >= 0.8 else 'low_confidence'
                response = random.choice(responses[label][confidence_key])
            else:
                response = random.choice(responses['NEUTRAL'])

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"Ошибка анализа настроения: {str(e)}")
            dispatcher.utter_message(text="Не удалось определить настроение. Попробуйте описать его другими словами.")

        return []

    def preprocess_text(self, text: str) -> str:
        text = re.sub(r"[^a-zA-Zа-яА-ЯёЁ\d\s!?.,;:]+", "", text)
        return text.lower().strip()