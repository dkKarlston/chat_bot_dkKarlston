from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re

class ActionCalculate(Action):
    def name(self) -> str:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_input = tracker.latest_message.get("text", "")
        expression = next(tracker.get_latest_entity_values("expression"), None)

        if not expression:
            match = re.search(r"([-+]?\d+\.?\d*[\+\-\*/\^xX]+[-+]?\d+\.?\d*)", user_input)
            if match:
                expression = match.group(1)
            else:
                dispatcher.utter_message(text="Не найдено выражение. Пример: 2+2 или 3x4")
                return []

        try:
            expr = expression.replace('x', '*').replace('X', '*').replace('^', '**')
            result = eval(expr)
            dispatcher.utter_message(text=f"Результат: {result}")
        except:
            dispatcher.utter_message(text="Не могу вычислить это выражение")

        return []