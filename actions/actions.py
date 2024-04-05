from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionCalculateWaterNeed(Action):
    def name(self) -> Text:
        return "action_calculate_water_need"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        weight = tracker.get_slot('weight')
        if not weight:
            dispatcher.utter_message(text="Я не знаю ваш вес. Напишите его, пожалуйста.")
            return []
        try:
            weight = float(weight)
            # 30 мл на кг
            daily_need = weight * 30
            dispatcher.utter_message(text=f"Основываясь на вашем весе, вам нужно пить {daily_need} мл воды в день.")
            return [SlotSet("daily_water_goal", daily_need)]
        except ValueError:
            dispatcher.utter_message(text="Я не могу распознать ваш вес. Не могли бы вы указать его в килиграммах?")
            return []


class ActionLogWater(Action):
    def name(self) -> str:
        return "action_log_water"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: str) -> list:
        amount = next(tracker.get_latest_entity_values("amount"), None)
        unit = next(tracker.get_latest_entity_values("unit"), None)
        current_intake = tracker.get_slot("water_intake_today") or 0.0
        if not amount or not unit:
            dispatcher.utter_message(text="Я не понимаю, сколько воды вы выпили.")
            return []

        try:
            amount = float(amount)
            if unit in ["л", "литр"]:
                amount *= 1000
            new_total = current_intake + amount
            dispatcher.utter_message(text=f"Добавлено {amount} мл жидкости.")
            return [SlotSet("water_intake_today", new_total)]
        except ValueError:
            dispatcher.utter_message(text="Похоже, возникла проблема с указанными вами данными")
            return []


class ActionSetWaterGoal(Action):
    def name(self) -> Text:
        return "action_set_water_goal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        goal = tracker.latest_message.get('entities', [{}])[0].get('value')
        if not goal:
            dispatcher.utter_message(text="Мне не удалось найти в вашем сообщении необходимое количество воды.")
            return []

        try:
            goal = float(goal)
            dispatcher.utter_message(text=f"Ваша ежедневная цель по потреблению воды установлена на {goal} мл.")
            return [SlotSet("daily_water_goal", goal)]
        except ValueError:
            dispatcher.utter_message(text="Я не могу распознать желаемое количество воды.")
            return []


class ActionProvideWaterIntake(Action):
    def name(self) -> Text:
        return "action_provide_water_intake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        daily_goal = tracker.get_slot("daily_water_goal")
        if daily_goal:
            dispatcher.utter_message(text=f"Ваша цель по ежедневному потреблению воды - {daily_goal} мл.")
        else:
            dispatcher.utter_message(text="Ваша цель по ежедневному потреблению воды еще не установлена.")
        return []


class ActionProvideRemainingIntake(Action):
    def name(self) -> Text:
        return "action_provide_remaining_intake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        daily_goal = tracker.get_slot("daily_water_goal")
        water_intake_today = tracker.get_slot("water_intake_today") or 0
        remaining_intake = daily_goal - water_intake_today
        if remaining_intake > 0:
            dispatcher.utter_message(text=f"Сегодня вам осталось выпить {remaining_intake} мл воды, чтобы достичь своей цели.")
        else:
            dispatcher.utter_message(text="Вы достигли своей цели по ежедневному потреблению воды. Отличная работа!")
        return []