import spacy
from deep_translator import GoogleTranslator
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, Dict, List, Any  # Добавляем типы

# Загрузка моделей spaCy
nlp_ru = spacy.load("ru_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")


class ActionLogDialog(Action):
    def name(self) -> Text:  
        return "action_log_dialog"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  

        user_input = tracker.latest_message.get("text", "")
        bot_response = tracker.get_last_bot_utterance().get("text", "")

        try:
            with open("chat_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"Пользователь: {user_input}\nБот: {bot_response}\n\n")
            dispatcher.utter_message(text="Диалог записан в журнал 📝")
        except Exception as e:
            dispatcher.utter_message(text="Ошибка записи в журнал")

        return []


class ActionLemmatizeText(Action):
    def name(self) -> Text: 
        return "action_lemmatize_text"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  

        text = tracker.latest_message.get("text", "")

        if not text:
            dispatcher.utter_message(text="Не получил текст для обработки")
            return []

        try:
            
            translator = GoogleTranslator(source='auto', target='en')
            translated = translator.translate(text)

            # Лемматизация
            doc = nlp_en(translated)
            lemmas = " ".join([token.lemma_ for token in doc])

            dispatcher.utter_message(
                text=f"🔍 Результат лемматизации:\n"
                     f"Оригинал: {text}\n"
                     f"Леммы (EN): {lemmas}"
            )

        except Exception as e:
            dispatcher.utter_message(text="Ошибка обработки текста 😞")
            print(f"Lemmatization error: {str(e)}")

        return []

class ActionRespondGreet(Action):
    def name(self) -> Text:
        return "action_respond_greet"

    def run(self, dispatcher, tracker, domain):
       
        dispatcher.utter_message(response="utter_greet")
        return []

class ActionRespondGoodbye(Action):
    def name(self) -> Text:
        return "action_respond_goodbye"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="До свидания! Было приятно помочь.")
        return []
