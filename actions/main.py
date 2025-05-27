from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import logging
import sqlite3

logger = logging.getLogger(__name__)


class ActionSaveUserData(Action):
    def name(self) -> Text:
        return "action_save_user_data"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        user_id = str(tracker.sender_id)

        # Логируем все сущности
        entities = tracker.latest_message.get("entities", [])
        logger.debug(f"Entities found: {entities}")

        # Извлекаем значения
        name = next((e["value"] for e in entities if e["entity"] == "user_name"), None)
        city = next((e["value"] for e in entities if e["entity"] == "user_city"), None)

        # Проверка на пустые значения
        if not name and not city:
            dispatcher.utter_message("❌ Не удалось получить данные для сохранения")
            return []

        # Получаем из слотов, если сущности не найдены
        name = name or tracker.get_slot("user_name")  
        city = city or tracker.get_slot("user_city")

        logger.info(f"User ID: {user_id}")
        logger.info(f"Extracted city: {city}")

        try:
            with sqlite3.connect('C:/Users/dimak/Desktop/plitech/6 sem/II/chat_bot_4/user_data.db') as conn:
                cursor = conn.cursor()

                # Проверка существующей записи
                cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()

                if exists:
                    # Обновление
                    query = '''
                                UPDATE users 
                                SET name = COALESCE(?, name), 
                                    city = COALESCE(?, city)
                                WHERE user_id = ?
                            '''
                    cursor.execute(query, (name, city, user_id))
                else:
                    # Новая запись
                    cursor.execute('''
                                INSERT INTO users (user_id, name, city)
                                VALUES (?, ?, ?)
                            ''', (user_id, name, city))

                conn.commit()
                dispatcher.utter_message("✅ Данные успешно обновлены!")

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            dispatcher.utter_message("😞 Ошибка при работе с базой данных")

        return [
            SlotSet("user_name", name),  
            SlotSet("user_city", city)  
        ]



class ActionGetProfile(Action):
    def name(self) -> Text:
        return "action_get_profile"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        user_id = str(tracker.sender_id)
        logger.info(f"Current user_id: {user_id}")

        try:
            with sqlite3.connect('C:/Users/dimak/Desktop/plitech/6 sem/II/chat_bot_4/user_data.db') as conn:
                # Автоматическое создание таблицы при необходимости
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        name TEXT,
                        city TEXT
                    )
                ''')
                conn.commit()

                # Поиск данных пользователя
                cursor.execute('''
                    SELECT name, city 
                    FROM users 
                    WHERE user_id = ?
                ''', (user_id,))

                result = cursor.fetchone()

                events = []
                if result:
                    name, city = result
                    intent_name = tracker.latest_message['intent']['name']

                    # Устанавливаем слоты для дальнейшего использования
                    events.append(SlotSet("user_name", name))
                    events.append(SlotSet("user_city", city))

                    # Ответ в зависимости от интента
                    if intent_name == 'ask_name':
                        dispatcher.utter_message(f"👤 Вас зовут: {name}")
                    elif intent_name == 'ask_city':
                        dispatcher.utter_message(f"🏙️ Ваш город: {city}")
                    else:
                        dispatcher.utter_message(f"📝 Профиль: {name}, {city}")
                else:
                    dispatcher.utter_message("❌ Ваши данные не найдены. Пожалуйста, укажите имя и город.")

        except Exception as e:
            logger.error(f"Ошибка запроса: {str(e)}")
            dispatcher.utter_message("⚠️ Ошибка при загрузке данных")
            return []

        return events
