from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from urllib.parse import quote
import webbrowser
from typing import Dict, List, Any, Text


class ActionSearchWeb(Action):
    def name(self) -> Text:
        return "action_search_web"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем query из сущности или всего сообщения
        query = next(tracker.get_latest_entity_values("query"), None) or " ".join(
            tracker.latest_message["text"].split()[1:])

        if not query:
            dispatcher.utter_message(text="Пожалуйста, укажите запрос для поиска.")
            return []

        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        dispatcher.utter_message(text=f"Открываю результаты по запросу: {query}")
        return []