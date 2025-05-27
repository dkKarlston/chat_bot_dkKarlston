from rasa_sdk import Action, Tracker, logger
from rasa_sdk.executor import CollectingDispatcher
import datetime
from typing import Dict, Any, Text, List

class ActionGetTime(Action):
    # Добавляем обязательный метод name()
    def name(self) -> Text:
        return "action_get_time"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%d.%m.%Y")
            message = f"Сейчас {current_time}, сегодня {current_date}"
            dispatcher.utter_message(text=message)
            return []
        except Exception as e:
            dispatcher.utter_message(text="Не удалось определить время.")
            logger.error(f"Error in action_get_time: {e}")
            return []