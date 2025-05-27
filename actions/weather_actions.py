from typing import  Text
import datetime
import random
import requests
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

import logging

logger = logging.getLogger(__name__)


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher, tracker, domain):
        # Получаем город из последнего сообщения пользователя
        user_message = tracker.latest_message.get('text')
        city = next(tracker.get_latest_entity_values("city"), None)

        # Если город не найден через сущность, попробуем извлечь вручную
        if not city and "погода" in user_message.lower():
            city = user_message.split("погода")[-1].strip()

        if not city:
            dispatcher.utter_message(text="Пожалуйста, уточните город для получения погоды.")
            return []

        # Очистка названия города
        city = city.replace("в ", "").replace("для ", "").strip()


        API_KEY = "c4aec831b9f8a6d4a4acc553848b76ff"
        BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

        try:
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric",
                "lang": "ru"
            }

            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Проверка ответа API
            if data.get("cod") != 200:
                raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")


            main_data = data["main"]
            weather_data = data["weather"][0]
            sys_data = data["sys"]

            temp = main_data["temp"]
            pressure = main_data["pressure"]
            description = weather_data["description"]

            # Конвертируем время
            sunrise = datetime.datetime.fromtimestamp(sys_data["sunrise"]).strftime("%H:%M")
            sunset = datetime.datetime.fromtimestamp(sys_data["sunset"]).strftime("%H:%M")

            # Формируем ответы
            responses = [
                f"В {city} сейчас {description}, {temp}°C. Давление: {pressure} гПа. "
                f"Солнце: восход {sunrise}, закат {sunset}.",

                f"Погода в {city}: {description}, температура {temp}°C. "
                f"Атмосферное давление {pressure} гПа. Восход: {sunrise}, закат: {sunset}.",

                f"Сейчас в {city}: {temp}°C, {description}. "
                f"Давление: {pressure} гПа. Время восхода: {sunrise}, заката: {sunset}."
            ]

            dispatcher.utter_message(text=random.choice(responses))

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                msg = "Не удалось найти город. Проверьте написание и попробуйте снова."
            else:
                msg = "Сервис погоды временно недоступен. Попробуйте позже."
            dispatcher.utter_message(text=msg)
            logger.error(f"HTTP Error: {str(e)}")

        except (KeyError, ValueError) as e:
            dispatcher.utter_message(text="Произошла ошибка при обработке данных о погоде.")
            logger.error(f"Data processing error: {str(e)}")

        except Exception as e:
            dispatcher.utter_message(text="Неожиданная ошибка при получении погоды.")
            logger.error(f"Unexpected error: {str(e)}")

        return [SlotSet("city", None)]