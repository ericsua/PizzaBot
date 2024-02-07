# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Coroutine, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, Restarted
from rasa.shared.core.events import Event
from typing import Text, List, Any, Dict
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from itertools import islice
class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"
    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ):
        return [Restarted(), FollowupAction("action_listen")]
class ActionConfirmPizzas(Action):
    def name(self):
        return 'action_confirm_pizzas'
    async def run(self, dispatcher, tracker, domain):
        pizza_size = tracker.get_slot("pizza_size")
        pizza_type = tracker.get_slot("pizza_type")
        pizza_amount = tracker.get_slot("pizza_amount")
        pizza_sliced = tracker.get_slot("pizza_sliced")
        pizza_crust = tracker.get_slot("pizza_crust")
        order_details = ""
        toppings = tracker.get_slot("pizza_toppings")
        if toppings is not None:
            toppings = ", ".join(toppings) if toppings is not None else ""
            toppings = toppings.rsplit(', ', 1)
            toppings = " and ".join(toppings)
            toppings = "with " + toppings
            order_details += f"{pizza_amount} {pizza_size} {pizza_crust} crust {pizza_type} {toppings}"
        else:
            order_details += f"{pizza_amount} {pizza_size} {pizza_crust} crust {pizza_type}"
        order_details += ", all pizza" + ( " sliced" if pizza_sliced == True else " not sliced")
        if tracker.get_slot("future_pizza_amount") is not None or tracker.get_slot("future_pizza_type") is not None or tracker.get_slot("future_pizza_size") is not None or tracker.get_slot("future_pizza_crust") is not None:
            dispatcher.utter_message(text="So, for now, you want to order "+order_details+". Is everything correct?")
        else:
            dispatcher.utter_message(text="So, you want to order "+order_details+". Is everything correct?")
        old_order = tracker.get_slot("pending_order")
        pending_order = (old_order + [order_details]) if old_order is not None else [order_details]
        return [SlotSet("pending_order", pending_order)]
class ActionTotalOrder(Action):
    def name(self):
        return 'action_total_order'
    async def run(self, dispatcher, tracker, domain):
        total_order = tracker.get_slot("total_order")
        if total_order is None:
            dispatcher.utter_message(text="Sorry, there is an error. You have no pending order.")
            return []
        else:
            total_order = ", and ".join(total_order)
            dispatcher.utter_message(text=f"Okay, great! So your total order is {total_order}. Do you prefer take away or home delivery?")
            return [SlotSet("total_order", total_order)]
class ActionCancelPendingOrder(Action):
    def name(self):
        return 'action_cancel_pending_order'
    async def run(self, dispatcher, tracker, domain):
        pending_order = tracker.get_slot("pending_order")
        if pending_order is None:
            dispatcher.utter_message(text="Sorry, there is an error. You have no pending order.")
            return []
        else:
            if len(pending_order) > 0:
                pending_order.pop(-1)
                return [SlotSet("pending_order", pending_order if len(pending_order) > 0 else None)]
            return [SlotSet("pending_order", None)]
class ActionNextOrder(Action):
    def name(self) -> Text:
        return "action_next_order"
    async def run(self, dispatcher, tracker: Tracker, domain):
        future_pizza_type = tracker.get_slot("future_pizza_type")
        future_pizza_size = tracker.get_slot("future_pizza_size")
        future_pizza_amount = tracker.get_slot("future_pizza_amount")
        future_pizza_crust = tracker.get_slot("future_pizza_crust")
        pizza_type = tracker.get_slot("pizza_type")
        pizza_size = tracker.get_slot("pizza_size")
        pizza_amount = tracker.get_slot("pizza_amount")
        pizza_crust = tracker.get_slot("pizza_crust")
        next_pizza_type = None
        next_pizza_size = None
        next_pizza_amount = None
        next_pizza_crust = None
        events = []
        doForm = False
        if future_pizza_type is not None:
            next_pizza_type = future_pizza_type.pop(0)
            events += [SlotSet("pizza_type", next_pizza_type), SlotSet("future_pizza_type", future_pizza_type if len(future_pizza_type) > 0 else None)]
            doForm = True
        else:
            events += [SlotSet("pizza_type", None)]
        if future_pizza_size is not None:
            next_pizza_size = future_pizza_size.pop(0)
            events += [SlotSet("pizza_size", next_pizza_size), SlotSet("future_pizza_size", future_pizza_size if len(future_pizza_size) > 0 else None)]
            doForm = True
        else:
            events += [SlotSet("pizza_size", None)]
        if future_pizza_amount is not None:
            next_pizza_amount = future_pizza_amount.pop(0)
            events += [SlotSet("pizza_amount", next_pizza_amount), SlotSet("future_pizza_amount", future_pizza_amount if len(future_pizza_amount) > 0 else None)]
            doForm = True
        else:
            events += [SlotSet("pizza_amount", None)]
        if future_pizza_crust is not None:
            next_pizza_crust = future_pizza_crust.pop(0)
            events +=  [SlotSet("pizza_crust", next_pizza_crust), SlotSet("future_pizza_crust", future_pizza_crust if len(future_pizza_crust) > 0 else None)]
            doForm = True
        else:
            events += [SlotSet("pizza_crust", None)]
        if next_pizza_type is not None or next_pizza_size is not None or next_pizza_amount is not None or next_pizza_crust is not None:
            next_order= ""
            next_order += f"{next_pizza_amount} " if next_pizza_amount is not None else ""
            next_order += f"{next_pizza_size} " if next_pizza_size is not None else ""
            next_order += f"{next_pizza_crust} crust " if next_pizza_crust is not None else ""
            next_order += f"{next_pizza_type}" if next_pizza_type is not None else ""
            dispatcher.utter_message(text=f"Alright, let's go through the next {next_order} pizza.")
        if doForm:
            events += [SlotSet("pizza_sliced", None), FollowupAction("pizza_order_form")]
            return events
        else:
            return []
class ActionPizzaOrderAdd(Action):
    def name(self):
        return 'action_pizza_order_add'
    async def run(self, dispatcher, tracker, domain):
        pending_order = tracker.get_slot("pending_order")
        if pending_order is None:
            dispatcher.utter_message(text="Sorry, there is an error. You have no pending order.")
            return []
        total_order = tracker.get_slot("total_order")
        if total_order is None:
            total_order = []
        total_order.extend(tracker.get_slot("pending_order"))
        return [SlotSet("total_order", total_order), SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None), SlotSet("pizza_sliced", None), SlotSet("pizza_crust", None),  SlotSet("pizza_toppings", None), SlotSet("pending_order", None)]
class ActionResetPizzaForm(Action):
    def name(self):
        return 'action_reset_pizza_form'
    async def run(self, dispatcher, tracker, domain):
        return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None), SlotSet("pizza_sliced", None), SlotSet("pizza_crust", None), SlotSet("pending_order", None)]
class ActionOrderNumber(Action):
    def name(self):
        return 'action_order_number'
    async def run(self, dispatcher, tracker, domain):
        name_person = tracker.get_slot("client_name")
        number_person = tracker.get_slot("phone_number")
        order_number =  str(name_person + "_"+number_person)
        print(order_number)
        return[SlotSet("order_number", order_number)]
class ActionGetRestaurantLocation(Action):
    def name(self):
        return 'action_get_restaurant_location'
    async def run(self, dispatcher, tracker, domain):
        restaurant_address = "Via Sommarive, 9, 38122 Trento TN"
        return[SlotSet("restaurant_location", restaurant_address)]
class ActionGetPizzaTypes(Action):
    def name(self):
        return 'action_get_pizza_types'
    async def run(self, dispatcher, tracker, domain):
        pizza_category = tracker.get_slot("pizza_category")
        if tracker.get_intent_of_latest_message() == "order_anti_pizza":
            dispatcher.utter_message(text="We only sell pizza here.")
        if pizza_category is None:
            dispatcher.utter_message(response="utter_inform_pizza_types")
        elif pizza_category.lower() in ["meat", "meat lover", "meatlovers", "meat-lover", "meat-lovers", "meatlovers", "meat lovers", "no vegetables"]:
            dispatcher.utter_message(response="utter_inform_pizza_types_meat")
        elif pizza_category.lower() in ["vegetarian", "vegan", "vegetable", "vegetables", "veggie", "no meat"]:
            dispatcher.utter_message(response="utter_inform_pizza_types_vegetarian")
        else:
            dispatcher.utter_message(response="utter_inform_pizza_types_no_category")
            dispatcher.utter_message(response="utter_inform_pizza_types")
        return [SlotSet("pizza_category", None)]
class ValidatePizzaOrderForm(FormValidationAction):
    def __init__(self) -> None:
        super().__init__()
        self.warn_user = False
    def name(self) -> Text:
        return "validate_pizza_order_form"
    @staticmethod
    def pizza_db() -> List[Text]:
        """Database of supported cuisines"""
        return ["funghi", "hawaii", "margherita", "pepperoni", "veggie"]
    def reset_warn(self):
        self.warn_user = False
    def warn_user_one_at_time(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> None:
        if not self.warn_user:
            future_pizza_type = tracker.get_slot("future_pizza_type")
            future_pizza_size = tracker.get_slot("future_pizza_size")
            future_pizza_amount = tracker.get_slot("future_pizza_amount")
            future_pizza_crust = tracker.get_slot("future_pizza_crust")
            pizza_type = tracker.get_slot("pizza_type")
            pizza_size = tracker.get_slot("pizza_size")
            pizza_amount = tracker.get_slot("pizza_amount")
            pizza_crust = tracker.get_slot("pizza_crust")
            if future_pizza_type is not None or future_pizza_size is not None or future_pizza_amount is not None or future_pizza_crust is not None:
                if future_pizza_type is not None and pizza_type is not None:
                    dispatcher.utter_message(text=f"Sure, but for now let's first only go through the {pizza_type} pizza.")
                elif future_pizza_size is not None and pizza_size is not None:
                    dispatcher.utter_message(text=f"Sure, but let's focus only on the first {pizza_size} pizza.")
                elif future_pizza_amount is not None and pizza_amount is not None:
                    dispatcher.utter_message(text=f"Alright, but let's focus only on the first {pizza_amount} pizza.")
                elif future_pizza_crust is not None and pizza_crust is not None:
                    dispatcher.utter_message(text=f"Okay, but let's focus only on the first {pizza_crust} pizza.")
                self.warn_user = True
            return True
        else:
            return False
    def validate_pizza_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        if isinstance(slot_value, str):
            if slot_value.lower() in self.pizza_db():
                self.warn_user_one_at_time(dispatcher, tracker, domain)
                return {"pizza_type": slot_value}
            else:
                return {"pizza_type": "Special " + slot_value.title() }
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_type": concatenated_slot}
            else:
                return {"pizza_type": None}
    def validate_pizza_amount(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        if isinstance(slot_value, str):
            if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]:
                self.warn_user_one_at_time(dispatcher, tracker, domain)
                return {"pizza_amount": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid number.")
                return {"pizza_amount": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_amount": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me a valid number.")
                return {"pizza_amount": None}
    def validate_pizza_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        if isinstance(slot_value, str):
            if slot_value.lower() in ["baby", "small", "medium", "standard", "large", "extra large"]:
                self.warn_user_one_at_time(dispatcher, tracker, domain)
                return {"pizza_size": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid size.")
                dispatcher.utter_message(response="utter_inform_pizza_size")
                return {"pizza_size": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_size": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me a valid size.")
                dispatcher.utter_message(response="utter_inform_pizza_size")
                return {"pizza_size": None}
    def validate_pizza_sliced(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        return {}
    def validate_pizza_crust(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        if isinstance(slot_value, str):
            if slot_value.lower() in ["thin", "flatbread", "stuffed", "cracker"]:
                self.warn_user_one_at_time(dispatcher, tracker, domain)
                return {"pizza_crust": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid crust.")
                dispatcher.utter_message(response="utter_inform_pizza_crust")
                return {"pizza_crust": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_crust": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me a valid crust.")
                dispatcher.utter_message(response="utter_inform_pizza_crust")
                return {"pizza_crust": None}
class ActionTypeMapping(Action):
    def name(self) -> Text:
        return "action_type_mapping"
    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_start_generic": 
            pizza_type = tracker.get_slot("pizza_type")
            ent_pizza_type = next(tracker.get_latest_entity_values("pizza_type"), None)
            if ent_pizza_type is None:
                return []
            else:
                if pizza_type is None:
                    return [SlotSet("pizza_type", ent_pizza_type)]
                else:
                    return [SlotSet("pizza_type", pizza_type)]
        return []
class ActionSizeMapping(Action):
    def name(self) -> Text:
        return "action_size_mapping"
    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_start_generic": 
            pizza_size = tracker.get_slot("pizza_size")
            ent_pizza_size = next(tracker.get_latest_entity_values("pizza_size"), None)
            if ent_pizza_size is None:
                return []
            else:
                if pizza_size is None:
                    return [SlotSet("pizza_size", ent_pizza_size)]
                else:
                    return [SlotSet("pizza_size", pizza_size)]
        return []
class ActionAmountMapping(Action):
    def name(self) -> Text:
        return "action_amount_mapping"
    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_start_generic": 
            pizza_amount = tracker.get_slot("pizza_amount")
            ent_pizza_amount = next(tracker.get_latest_entity_values("pizza_amount"), None)
            if ent_pizza_amount is None:
                return []
            else:
                if pizza_amount is None:
                    return [SlotSet("pizza_amount", ent_pizza_amount)]
                else:
                    return [SlotSet("pizza_amount", pizza_amount)]
        return []
class ActionCrustMapping(Action):
    def name(self) -> Text:
        return "action_crust_mapping"
    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_start_generic": 
            pizza_crust = tracker.get_slot("pizza_crust")
            ent_pizza_crust = next(tracker.get_latest_entity_values("pizza_crust"), None)
            if ent_pizza_crust is None:
                return []
            else:
                if pizza_crust is None:
                    return [SlotSet("pizza_crust", ent_pizza_crust)]
                else:
                    return [SlotSet("pizza_crust", pizza_crust)]
        return []
class ActionSlicedMapping(Action):
    def name(self):
        return "action_sliced_mapping"
    async def run(self, dispatcher, tracker: Tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_change":
            return []
        reversed_events = list(reversed(tracker.events))
        last_user_message_index = next((i for i, event in enumerate(reversed_events) if event.get('event') == 'user'), None)
        previous_user_message_index = next((i for i, event in enumerate(reversed_events[last_user_message_index+1:]) if event.get('event') == 'user'), None)
        if previous_user_message_index is not None:
            previous_user_message_index = len(tracker.events) - (last_user_message_index + previous_user_message_index + 2)
            prev_last_intent = tracker.events[previous_user_message_index]['parse_data']['intent']['name']
        entities = tracker.latest_message['entities']
        pizza_sliced_entity = next((e for e in entities if e['entity'] == 'pizza_sliced'), None)
        sliced = pizza_sliced_entity['value'] if pizza_sliced_entity else None
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get('name')
        if active_loop == "pizza_order_form":
            if last_intent == "response_positive" and requested_slot == "pizza_sliced" and prev_last_intent != "stop_order":
                return [SlotSet("pizza_sliced", True)]
            elif last_intent == "response_negative" and requested_slot == "pizza_sliced" and prev_last_intent != "stop_order":
                return [SlotSet("pizza_sliced", False)]
            elif last_intent == "item_start_generic": 
                if sliced is not None and sliced.lower() == "true":
                    return [SlotSet("pizza_sliced", True)]
                elif sliced is not None and sliced.lower() == "false":
                    return [SlotSet("pizza_sliced", False)]
class ActionAskPizzaAmount(Action):
    def name(self):
        return 'action_ask_pizza_amount'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_amount" and last_intent not in ["request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods", "stop_order", "explain", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_pizza_amount_again")
            return []
        if last_intent == "item_start_generic":
            if requested_slot == "pizza_type" and tracker.get_slot("pizza_type") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_amount_ack_type")
            elif requested_slot == "pizza_size" and tracker.get_slot("pizza_size") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_amount_ack_size")
            elif requested_slot == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_amount_ack_crust")
            elif requested_slot == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_amount_ack")
            else:
                dispatcher.utter_message(response="utter_ask_pizza_amount_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_amount")
        return []
class ActionAskPizzaType(Action):
    def name(self):
        return 'action_ask_pizza_type'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_type" and last_intent not in ["request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods", "stop_order", "explain", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_pizza_type_again")
            return []
        if last_intent == "item_start_generic":
            if requested_slot == "pizza_size" and tracker.get_slot("pizza_size") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_type_ack_size")
            elif requested_slot == "pizza_amount" and tracker.get_slot("pizza_amount") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_type_ack_amount")
            elif requested_slot == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_type_ack_crust")
            elif requested_slot == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_type_ack")
            else:
                dispatcher.utter_message(response="utter_ask_pizza_type_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_type")
        return []
class ActionAskPizzaSize(Action):
    def name(self):
        return 'action_ask_pizza_size'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_size" and last_intent not in ["request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods", "stop_order", "explain", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_pizza_size_again")
            return []
        if last_intent == "item_start_generic":
            if requested_slot == "pizza_type" and tracker.get_slot("pizza_type") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack_type")
            elif requested_slot == "pizza_amount" and tracker.get_slot("pizza_amount") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack_amount")
            elif requested_slot == "pizza_size" and tracker.get_slot("pizza_size") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack_size")
            elif requested_slot == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack_crust")
            elif requested_slot == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack")
            else:
                dispatcher.utter_message(response="utter_ask_pizza_size_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_size")
        return[]
class ActionAskPizzaSliced(Action):
    def name(self):
        return 'action_ask_pizza_sliced'
    async def run(self, dispatcher, tracker: Tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_sliced" and last_intent not in ["request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods", "stop_order", "explain", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_again")
            return []
        if last_intent == "item_start_generic":
            if requested_slot == "pizza_type" and tracker.get_slot("pizza_type") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_type")
            elif requested_slot == "pizza_size" and tracker.get_slot("pizza_size") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_size")
            elif requested_slot == "pizza_amount" and tracker.get_slot("pizza_amount") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_amount")
            elif requested_slot == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_crust")
            else:
                dispatcher.utter_message(response="utter_ask_pizza_sliced_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_sliced")
        return[]
class ActionAskPizzaCrust(Action):
    def name(self):
        return 'action_ask_pizza_crust'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_crust" and last_intent not in ["request_pizza_crusts", "request_pizza_sizes", "request_pizza_types","request_delivery_areas", "request_payment_methods", "stop_order", "explain", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_pizza_crust_again")
            return []
        if last_intent == "item_start_generic":
            if requested_slot == "pizza_type" and tracker.get_slot("pizza_type") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_crust_ack_type")
            elif requested_slot == "pizza_size" and tracker.get_slot("pizza_size") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_crust_ack_size")
            elif requested_slot == "pizza_amount" and tracker.get_slot("pizza_amount") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_crust_ack_amount")
            elif requested_slot == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
                dispatcher.utter_message(response="utter_ask_pizza_crust_ack")
            else:
                dispatcher.utter_message(response="utter_ask_pizza_crust_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_crust")
        return[]
class ActionChangeOrder(Action):
    def name(self):
        return 'action_change_order'
    async def run(self, dispatcher, tracker: Tracker, domain):
        pizza_size = tracker.get_slot("pizza_size")
        pizza_type = tracker.get_slot("pizza_type")
        pizza_amount = tracker.get_slot("pizza_amount")
        pizza_crust = tracker.get_slot("pizza_crust")
        pizza_sliced = tracker.get_slot("pizza_sliced")
        typeChanged = next(tracker.get_latest_entity_values("pizza_type"), None)
        sizeChanged = next(tracker.get_latest_entity_values("pizza_size"), None)
        amountChanged = next(tracker.get_latest_entity_values("pizza_amount"), None)
        crustChanged = next(tracker.get_latest_entity_values("pizza_crust"), None)
        slicedChanged = next(tracker.get_latest_entity_values("pizza_sliced"), None)
        if pizza_size is None and pizza_type is None and pizza_amount is None and pizza_crust is None and pizza_sliced is None:
            dispatcher.utter_message(response="utter_warning_nothing_to_change")
            return [SlotSet("modify_order", None)]
        changes = []
        if typeChanged:
            pizza_type = typeChanged
            changes.append(f"the pizza type to {pizza_type}")
        if sizeChanged:
            pizza_size = sizeChanged
            changes.append(f"the size to {pizza_size}")
        if amountChanged:
            pizza_amount = amountChanged
            changes.append(f"the number of pizzas to {pizza_amount}")
        if crustChanged:
            pizza_crust = crustChanged
            changes.append(f"the crust to {pizza_crust}")
        if slicedChanged:
            pizza_sliced = slicedChanged
            if pizza_sliced == "true":
                changes.append("the pizzas to be sliced")
                pizza_sliced = True
            else:
                changes.append("the pizzas won't be sliced")
                pizza_sliced = False
        if len(changes) > 0:
            if len(changes) > 1:
                changes[-1] = "and " + changes[-1]
            total_changes = "Alright, I changed " + ", ".join(changes) + "."
            dispatcher.utter_message(text=total_changes)
        return [
            SlotSet("pizza_type", pizza_type),
            SlotSet("pizza_size", pizza_size),
            SlotSet("pizza_amount", pizza_amount),
            SlotSet("pizza_crust", pizza_crust),
            SlotSet("pizza_sliced", pizza_sliced),
            SlotSet("modify_order", None),
            SlotSet("pending_order", None)
        ]
class ValidataDeliveryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_delivery_form"
    async def validate_client_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if isinstance(slot_value, str):
            return {"client_name": slot_value}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"client_name": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me your name.")
                return {"client_name": None}
    async def validate_client_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.active_loop.get('name') != "delivery_form":
            dispatcher.utter_message(text="We'll get to the delivery in a moment.")
            return {"client_address": None}
        if isinstance(slot_value, str):
            return {"client_address": slot_value}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"client_address": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me your address.")
                return {"client_address": None}
    async def validate_client_payment(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.active_loop.get('name') != "delivery_form":
            dispatcher.utter_message(text="We'll get to the payment later.")
            return {"client_payment": None}
        if isinstance(slot_value, str):
            if slot_value.lower() in ["cash", "card"]:
                return {"client_payment": slot_value}
            else:
                dispatcher.utter_message(text="Sorry, we only accept cash or card as payment methods.")
                return {"client_payment": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"client_payment": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me your payment method.")
                return {"client_payment": None}
class ValidateTakeawayForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_takeaway_form"
    async def validate_client_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if isinstance(slot_value, str):
            return {"client_name": slot_value}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"client_name": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me your name.")
                return {"client_name": None}
class ActionClientNameMapping(Action):
    def name(self):
        return "action_client_name_mapping"
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "client_name" or last_intent == "welcome_greet":
            client_name = tracker.get_slot("client_name")
            ent_client_name = next(tracker.get_latest_entity_values("PERSON"), None)
            if ent_client_name is None:
                return []
            else:
                if client_name is None:
                    return [SlotSet("client_name", ent_client_name)]
                else:
                    return [SlotSet("client_name", client_name)]
        return []
class ActionAddressMapping(Action):
    def name(self):
        return "action_address_mapping"
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if tracker.active_loop.get('name') != "delivery_form":
            dispatcher.utter_message(text="We'll get to the delivery later.")
        if last_intent == "client_address":
            client_address = tracker.get_slot("client_address")
            ent_client_address = next(tracker.get_latest_entity_values("client_address"), None)
            if ent_client_address is None:
                return []
            else:
                if client_address is None:
                    return [SlotSet("client_address", ent_client_address)]
                else:
                    return [SlotSet("client_address", client_address)]
        return []
class ActionPaymentMapping(Action):
    def name(self):
        return "action_payment_mapping"
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if tracker.active_loop.get('name') != "delivery_form":
            dispatcher.utter_message(text="We'll get to the payment later.")
        if last_intent == "client_payment":
            client_payment = tracker.get_slot("client_payment")
            ent_client_payment = next(tracker.get_latest_entity_values("client_payment"), None)
            if ent_client_payment is None:
                return []
            else:
                if client_payment is None:
                    return [SlotSet("client_payment", ent_client_payment)]
                else:
                    return [SlotSet("client_payment", client_payment)]
        return []
class ActionAskClientName(Action):
    def name(self):
        return 'action_ask_client_name'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        active_loop = tracker.active_loop.get('name')
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "client_name" and last_intent not in ["delivery_change", "delivery_change_request_without_entity", "item_change_request_without_entity", "stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_client_name_again")
            return []
        if active_loop == "delivery_form":
            if requested_slot == "client_address" and tracker.get_slot("client_address") is not None:
                dispatcher.utter_message(response="utter_ask_client_name_ack_address")
            elif requested_slot == "client_payment" and tracker.get_slot("client_payment") is not None:
                dispatcher.utter_message(response="utter_ask_client_name_ack_payment")
            else:
                dispatcher.utter_message(response="utter_ask_client_name_ack_delivery")
        elif active_loop == "takeaway_form":
            dispatcher.utter_message(response="utter_ask_client_name_ack_takeaway")
        else:
            dispatcher.utter_message(response="utter_ask_client_name")
        return []
class ActionAskClientAddress(Action):
    def name(self):
        return 'action_ask_client_address'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get('name')
        if requested_slot == "client_address" and last_intent not in ["delivery_change", "delivery_change_request_without_entity", "item_change_request_without_entity", "request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods", "stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_client_address_again")
            return []
        if last_intent in ["client_name", "client_address", "client_payment"]:
            if requested_slot == "client_payment" and tracker.get_slot("client_payment") is not None:
                dispatcher.utter_message(response="utter_ask_client_address_ack_payment")
            elif requested_slot == "client_name" and tracker.get_slot("client_name") is not None:
                dispatcher.utter_message(response="utter_ask_client_address_ack_name")
            else:
                dispatcher.utter_message(response="utter_ask_client_address_ack")
        else:
            dispatcher.utter_message(response="utter_ask_client_address")
        return []
class ActionAskClientPayment(Action):
    def name(self):
        return 'action_ask_client_payment'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get('name')
        if requested_slot == "client_payment" and last_intent not in ["delivery_change", "delivery_change_request_without_entity",  "item_change_request_without_entity", "request_pizza_crusts", "request_pizza_sizes", "request_pizza_types", "request_delivery_areas", "request_payment_methods","stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_client_payment_again")
            return []
        if last_intent in ["client_name", "client_address", "client_payment"]:
            if requested_slot == "client_name" and tracker.get_slot("client_name") is not None:
                dispatcher.utter_message(response="utter_ask_client_payment_ack_name")
            elif requested_slot == "client_address" and tracker.get_slot("client_address") is not None:
                dispatcher.utter_message(response="utter_ask_client_payment_ack_address")
            else:
                dispatcher.utter_message(response="utter_ask_client_payment_ack")
        else:
            dispatcher.utter_message(response="utter_ask_client_payment")
        return []
class ActionConfirmDelivery(Action):
    def name(self):
        return 'action_confirm_delivery'
    async def run(self, dispatcher, tracker, domain):
        client_name = tracker.get_slot("client_name")
        client_address = tracker.get_slot("client_address")
        client_payment = tracker.get_slot("client_payment")
        message = f"Great! Can you confirm that the order will be delivered to {client_name} at {client_address} and that it will be paid with {client_payment}?"
        dispatcher.utter_message(text=message)
        return []
class ActionConfirmTakeaway(Action):
    def name(self):
        return 'action_confirm_takeaway'
    async def run(self, dispatcher, tracker, domain):
        client_name = tracker.get_slot("client_name")
        message = f"Great! Can you confirm that the order will be for {client_name} to take away?"
        dispatcher.utter_message(text=message)
        return []
class ActionChangeDelivery(Action):
    def name(self):
        return 'action_change_delivery'
    async def run(self, dispatcher, tracker, domain):
        client_name = tracker.get_slot("client_name")
        client_address = tracker.get_slot("client_address")
        client_payment = tracker.get_slot("client_payment")
        nameChanged = next(tracker.get_latest_entity_values("PERSON"), None)
        addressChanged = next(tracker.get_latest_entity_values("client_address"), None)
        paymentChanged = next(tracker.get_latest_entity_values("client_payment"), None)
        if client_name is None and client_address is None and client_payment is None:
            dispatcher.utter_message(response="utter_warning_nothing_to_change_delivery")
            return []
        changes = []
        if nameChanged:
            client_name = nameChanged
            changes.append(f"the name to {client_name}")
        if addressChanged:
            client_address = addressChanged
            changes.append(f"the address to {client_address}")
        if paymentChanged:
            client_payment = paymentChanged
            changes.append(f"the payment method to {client_payment}")
        if len(changes) > 0:
            if len(changes) > 1:
                changes[-1] = "and " + changes[-1]
            total_changes = "Alright, I changed " + ", ".join(changes) + "."
            dispatcher.utter_message(text=total_changes)
        return [
            SlotSet("client_name", client_name),
            SlotSet("client_address", client_address),
            SlotSet("client_payment", client_payment),
        ]
class ActionValidateTimeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_time_form"
    async def validate_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if isinstance(slot_value, str):
            return {"time": slot_value}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"time": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me the time.")
                return {"time": None}
    async def validate_premium_subscription_boolean(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if isinstance(slot_value, bool):
            if slot_value in [True, False]:
                return {"premium_subscription_boolean": slot_value}
            else:
                dispatcher.utter_message(text="Sorry, there was an error.")
                return {"premium_subscription_boolean": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"premium_subscription_boolean": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me if you have a premium subscription.")
                return {"premium_subscription_boolean": None}
    async def validate_premium_subscription_username(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value not in ["john doe", "jane doe", "pizza lover", "pizza eater", "NO_USERNAME"]:
            dispatcher.utter_message(text="Sorry, our system doesn't recognize that username as a premium subscription.")
            return {"premium_subscription_username": None}
        if isinstance(slot_value, str):
            return {"premium_subscription_username": slot_value}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"premium_subscription_username": concatenated_slot}
            else:
                dispatcher.utter_message(text="Please tell me your username.")
                return {"premium_subscription_username": None}
class ActionPremiumSubscriptionBoolMapping(Action):
    def name(self):
        return "action_premium_subscription_bool_mapping"
    async def run(self, dispatcher, tracker, domain):
        if tracker.active_loop.get('name') != "time_form":
            return []
        last_intent = tracker.get_intent_of_latest_message()
        last_bot_action = tracker.get_last_event_for("action", exclude=["action_listen", "time_form"])
        last_bot_action_name = last_bot_action.get("name")
        if last_bot_action_name in ["utter_confirm_takeaway_final", "utter_confirm_delivery_final", "utter_ask_premium_subscription_boolean_again", "utter_explain_premium_subscription_boolean", "explain"]:
            last_user_message = tracker.get_last_event_for("user")
            if last_user_message.get("timestamp") < last_bot_action.get("timestamp") or tracker.get_slot("requested_slot") != "premium_subscription_boolean":
                return []
            premium_subscription_boolean = tracker.get_slot("premium_subscription_boolean")
            if premium_subscription_boolean is None:
                if last_intent == "response_positive":
                    return [SlotSet("premium_subscription_boolean", True)]
                elif last_intent == "response_negative":
                    return [SlotSet("premium_subscription_boolean", False), SlotSet("premium_subscription_username", "NO_USERNAME")]
                else:
                    return []
            else:
                return [SlotSet("premium_subscription_boolean", premium_subscription_boolean)]
        return []
class ActionPremiumSubscriptionUsernameMapping(Action):
    def name(self):
        return "action_premium_subscription_username_mapping"
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "username":
            premium_subscription_username = tracker.get_slot("premium_subscription_username")
            ent_premium_subscription_username = next(tracker.get_latest_entity_values("premium_subscription_username"), None)
            if ent_premium_subscription_username is None:
                return []
            else:
                if premium_subscription_username is None:
                    return [SlotSet("premium_subscription_username", ent_premium_subscription_username)]
                else:
                    return [SlotSet("premium_subscription_username", premium_subscription_username)]
        return []
class ActionTimeMapping(Action):
    def name(self):
        return "action_time_mapping"
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "time":
            time = tracker.get_slot("time")
            ent_time = next(tracker.get_latest_entity_values("time"), None)
            if ent_time is None:
                return []
            else:
                if time is None:
                    return [SlotSet("time", ent_time)]
                else:
                    return [SlotSet("time", time)]
        return []
class ActionAskTime(Action):
    def name(self):
        return 'action_ask_time'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "time" and last_intent not in ["time_change", "time_change_request_without_entity", "stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_time_again")
            return []
        isTakeaway = tracker.get_slot("takeaway_boolean")
        if isTakeaway:
            if last_intent == "username" and tracker.get_slot("premium_subscription_username") not in [None, "NO_USERNAME"]:
                dispatcher.utter_message(response="utter_ask_time_takeaway_ack_username")
            elif last_intent in ["response_negative", "response_positive"]:
                dispatcher.utter_message(response="utter_ask_time_takeaway_ack")
            else:
                dispatcher.utter_message(response="utter_ask_time_takeaway")
        else:
            if last_intent == "username" and tracker.get_slot("premium_subscription_username") not in [None, "NO_USERNAME"]:
                dispatcher.utter_message(response="utter_ask_time_delivery_ack_username")
            elif last_intent in ["response_negative", "response_positive"]:
                dispatcher.utter_message(response="utter_ask_time_delivery_ack")
            else:
                dispatcher.utter_message(response="utter_ask_time_delivery")
        return []
class ActionAskPremiumSubscriptionBoolean(Action):
    def name(self):
        return 'action_ask_premium_subscription_boolean'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "action_ask_premium_subscription_boolean" and last_intent not in ["time_change", "time_change_request_without_entity", "stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_premium_subscription_again")
            return []
        if tracker.active_loop.get("name") == "time_form":
            dispatcher.utter_message(response="utter_ask_premium_subscription_username_boolean_ack")
        else:
            dispatcher.utter_message(response="utter_ask_premium_subscription_username_boolean")
        return []
class ActionAskPremiumSubscriptionUsername(Action):
    def name(self):
        return 'action_ask_premium_subscription_username'
    async def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "premium_subscription_username" and last_intent not in ["time_change", "time_change_request_without_entity", "stop_order", "explain", "response_negative", "bot_challenge", "nevermind", "book_table"]:
            dispatcher.utter_message(response="utter_ask_premium_subscription_username_again")
            return []
        if tracker.active_loop.get("name") == "time_form":
            if requested_slot == "premium_subscription_boolean" and tracker.get_slot("premium_subscription_boolean") is True:
                dispatcher.utter_message(response="utter_ask_premium_subscription_username_ack")
        else:
            dispatcher.utter_message(response="utter_ask_premium_subscription_username")
        return []
class ActionChangeTime(Action):
    def name(self):
        return 'action_change_time'
    async def run(self, dispatcher, tracker, domain):
        time = tracker.get_slot("time")
        premium_subscription_boolean = tracker.get_slot("premium_subscription_boolean")
        premium_subscription_username = tracker.get_slot("premium_subscription_username")
        timeChanged = next(tracker.get_latest_entity_values("time"), None)
        premiumSubscriptionBoolChanged = next(tracker.get_latest_entity_values("premium_subscription_boolean"), None)
        premiumSubscriptionUsernameChanged = next(tracker.get_latest_entity_values("premium_subscription_username"), None)
        if time is None and premium_subscription_boolean is None and premium_subscription_username is None:
            dispatcher.utter_message(response="utter_warning_nothing_to_change_time")
            return []
        changes = []
        if timeChanged:
            time = timeChanged
            changes.append(f"the time to {time}")
        if premiumSubscriptionBoolChanged:
            premium_subscription_boolean = premiumSubscriptionBoolChanged
            changes.append(f"the premium subscription status to {premium_subscription_boolean}")
        if premiumSubscriptionUsernameChanged:
            premium_subscription_username = premiumSubscriptionUsernameChanged
            changes.append(f"the premium subscription username to {premium_subscription_username}")
        if len(changes) > 0:
            if len(changes) > 1:
                changes[-1] = "and " + changes[-1]
            total_changes = "Alright, I changed " + ", ".join(changes) + "."
            dispatcher.utter_message(text=total_changes)
        return [
            SlotSet("time", time),
            SlotSet("premium_subscription_boolean", premium_subscription_boolean),
            SlotSet("premium_subscription_username", premium_subscription_username),
        ]
class ActionConfirmTime(Action):
    def name(self):
        return 'action_confirm_time'
    async def run(self, dispatcher, tracker, domain):
        time = tracker.get_slot("time")
        premium_subscription_boolean = tracker.get_slot("premium_subscription_boolean")
        premium_subscription_username = tracker.get_slot("premium_subscription_username")
        isTakeaway = tracker.get_slot("takeaway_boolean")
        if premium_subscription_boolean:
            if isTakeaway:
                message = f"Great! Can you confirm that the order will be picked up at {time} and that your premium subscription username is {premium_subscription_username}?"
            else:
                message = f"Great! Can you confirm that the order will be delivered at {time} and that your premium subscription username is {premium_subscription_username}?"
            dispatcher.utter_message(text=message)
        else:
            if isTakeaway:
                message = f"Great! Can you confirm that the order will be picked up at {time}?"
            else:
                message = f"Great! Can you confirm that the order will be delivered at {time}?"
            dispatcher.utter_message(text=message)
        return []