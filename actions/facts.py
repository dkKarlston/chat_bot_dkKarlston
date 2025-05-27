from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random

class ActionTellFact(Action):
    def name(self) -> str:
        return "action_tell_fact"

    FACTS = {
        "спорт": [
            "Бадминтон - самый быстрый ракеточный вид спорта: скорость волана достигает 270 км/ч.",
            "В мячике для гольфа 336 выемок.",
        ],
        "история": [
            "Великая Китайская стена не видна с Луны.",
            "Первая фотография сделана в 1826 году.",
        ],
        "космос": [
            "На Венере температура достигает 465°C.",
            "Гора Олимп на Марсе высотой 21 км.",
        ]
    }

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        category = next(tracker.get_latest_entity_values("category"), None)

        if category and category.lower() in self.FACTS:
            fact = random.choice(self.FACTS[category.lower()])
            dispatcher.utter_message(text=fact)
        else:
            dispatcher.utter_message(
                text="Пожалуйста, укажите категорию: спорт, история или космос"
            )
        return []