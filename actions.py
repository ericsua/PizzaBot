# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, Restarted
from rasa.shared.core.events import Event
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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

    def run(self, dispatcher, tracker, domain):
        pizza_size = tracker.get_slot("pizza_size")
        pizza_type = tracker.get_slot("pizza_type")
        pizza_amount = tracker.get_slot("pizza_amount")
        pizza_sliced = tracker.get_slot("pizza_sliced")
        pizza_crust = tracker.get_slot("pizza_crust")
        order_details = ""
        #for amount, type, size in zip(pizza_amount, pizza_type, pizza_size):
        order_details += f"{pizza_amount} {pizza_size} {pizza_crust} crust {pizza_type}"
        #order_details = ", ".join(order_details)
        order_details += ". All pizzas" + ( " sliced." if pizza_sliced == True else " not sliced.")
        dispatcher.utter_message(text="So you want to order "+order_details+" Is everything correct?")
        #old_order = tracker.get_slot("total_order")
        return [SlotSet("pending_order", order_details)]

class ActionPizzaOrderAdd(Action):
    def name(self):
        return 'action_pizza_order_add'

    def run(self, dispatcher, tracker, domain):
        # pizza_size = tracker.get_slot("pizza_size")
        # pizza_type = tracker.get_slot("pizza_type")
        # pizza_amount = tracker.get_slot("pizza_amount")
        # if pizza_size is None:
        # 	pizza_size = "standard"
        pending_order = tracker.get_slot("pending_order")
        if pending_order is None:
            dispatcher.utter_message(text="Sorry, there is an error. You have no pending order")
            return []
        order_details =  pending_order
        old_order = tracker.get_slot("total_order")
        dispatcher.utter_message(response="utter_order_added")
        return[SlotSet("total_order", [order_details]) if old_order is None else SlotSet("total_order", [old_order[0]+' and '+order_details])]

class ActionResetPizzaForm(Action):
    def name(self):
        return 'action_reset_pizza_form'

    def run(self, dispatcher, tracker, domain):

        return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None), SlotSet("pizza_sliced", None), SlotSet("pizza_crust", None), SlotSet("pending_order", None)]

class ActionOrderNumber(Action):
    def name(self):
        return 'action_order_number'

    def run(self, dispatcher, tracker, domain):
        name_person = tracker.get_slot("client_name")
        number_person = tracker.get_slot("phone_number")
        order_number =  str(name_person + "_"+number_person)
        print(order_number)
        return[SlotSet("order_number", order_number)]


class ActionGetRestaurantLocation(Action):
    def name(self):
        return 'action_get_restaurant_location'

    def run(self, dispatcher, tracker, domain):

        restaurant_address = "Via Sommarive, 9, 38122 Trento TN"

        return[SlotSet("restaurant_location", restaurant_address)]

class ActionGetPizzaTypes(Action):
    def name(self):
        return 'action_get_pizza_types'

    def run(self, dispatcher, tracker, domain):
    
        #pizza_types = ""
        pizza_category = tracker.get_slot("pizza_category")
        if pizza_category is None:
            #pizza_types = "Funghi, Hawaii, Margherita, Pepperoni, Vegetarian"
            dispatcher.utter_message(response="utter_inform_pizza_types")
        elif pizza_category.lower() in ["meat", "meat lover", "meatlovers", "meat-lover", "meat-lovers", "meatlovers", "meat lovers", "no vegetables"]:
            dispatcher.utter_message(response="utter_inform_pizza_types_meat")
        elif pizza_category.lower() in ["vegetarian", "vegan", "vegetable", "vegetables", "veggie", "no meat"]:
            dispatcher.utter_message(response="utter_inform_pizza_types_vegetarian")
        else:
            dispatcher.utter_message(response="utter_inform_pizza_types_no_category")
            dispatcher.utter_message(response="utter_inform_pizza_types")

        return [SlotSet("pizza_category", None)]


# for a generic slot validation please refer to https://rasa.com/docs/action-server/validation-action/
class ValidatePizzaOrderForm(FormValidationAction):

    def name(self) -> Text:
        # https://rasa.com/docs/rasa/forms/#advanced-usage
        return "validate_pizza_order_form"

    @staticmethod
    def pizza_db() -> List[Text]:
        """Database of supported cuisines"""
        return ["funghi", "hawaii", "margherita", "pepperoni", "veggie"]

    def validate_pizza_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        # print("slot val type", slot_value)
        # mod = tracker.get_slot("modify_order")
        # print("modify order", mod)
        

        #print("pizza type value", slot_value, tracker.get_slot("pizza_type"))
        if isinstance(slot_value, str):
            if slot_value.lower() in self.pizza_db():
                # validation succeeded, set the value of the "cuisine" slot to value
                return {"pizza_type": slot_value}
            else:
                return {"pizza_type": "Special " + slot_value.title() }
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_type": concatenated_slot}
            else:
                # validation failed, set this slot to None so that the
                # user will be asked for the slot again
                return {"pizza_type": None}

    def validate_pizza_amount(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        
        # print("slot val type", slot_value)
        # print(tracker.get_slot("pizza_amount"))
        # print(next(tracker.get_latest_entity_values("pizza_amount"), None))
        # mod = tracker.get_slot("modify_order")
        # print("modify order", mod)
        # if mod:
        #     return {"requested_slot": None}

        if isinstance(slot_value, str):
            if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]:
                # validation succeeded, set the value of the "cuisine" slot to value
                return {"pizza_amount": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid number")
                return {"pizza_amount": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_amount": concatenated_slot}
            else:
                # validation failed, set this slot to None so that the
                # user will be asked for the slot again
                dispatcher.utter_message(text="Please tell me a valid number")
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
                # validation succeeded, set the value of the "cuisine" slot to value
                return {"pizza_size": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid size")#. We have baby, small, medium, standard, large, extra large")
                dispatcher.utter_message(response="utter_inform_pizza_size")
                return {"pizza_size": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_size": concatenated_slot}
            else:
                # validation failed, set this slot to None so that the
                # user will be asked for the slot again
                dispatcher.utter_message(text="Please tell me a valid size")#. We have baby, small, medium, standard, large, extra large")
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

        if isinstance(slot_value, str):
            if tracker.get_intent_of_latest_message() == "response_positive": #slot_value.lower() in ["yes", "no"]:
                # validation succeeded, set the value of the "cuisine" slot to value
                return {"pizza_sliced": True}
            elif tracker.get_intent_of_latest_message() == "response_negative":
                return {"pizza_sliced": False}
            else:
                #dispatcher.utter_message(text="Please tell me if you want the pizza sliced or not, with a yes or a no") # not correct since it can be a different intent like "stop" which do not need an answer
                return {"pizza_sliced": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_sliced": concatenated_slot}
            else:
                # validation failed, set this slot to None so that the
                # user will be asked for the slot again
                #dispatcher.utter_message(text="Please tell me yes or no")
                return {"pizza_sliced": None}

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
                # validation succeeded, set the value of the "cuisine" slot to value
                return {"pizza_crust": slot_value}
            else:
                dispatcher.utter_message(text="Please tell me a valid crust")#. We have thin, thick, standard")
                dispatcher.utter_message(response="utter_inform_pizza_crust")
                return {"pizza_crust": None}
        elif isinstance(slot_value, list):
            if len(slot_value) > 0:
                concatenated_slot = ", ".join(slot_value)
                return {"pizza_crust": concatenated_slot}
            else:
                # validation failed, set this slot to None so that the
                # user will be asked for the slot again
                dispatcher.utter_message(text="Please tell me a valid crust")#. We have thin, thick, standard")
                dispatcher.utter_message(response="utter_inform_pizza_crust")
                return {"pizza_crust": None}

class ActionSlicedMapping(Action):
    def name(self):
        return "action_sliced_mapping"
    
    def run(self, dispatcher, tracker: Tracker, domain):
        
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent == "item_change":
            return []
        # get intent of message before last message
        reversed_events = list(reversed(tracker.events))
        #print("reversed_events", reversed_events)
        last_user_message_index = next((i for i, event in enumerate(reversed_events) if event.get('event') == 'user'), None)

        # Find the index of the user message before the last one
        previous_user_message_index = next((i for i, event in enumerate(reversed_events[last_user_message_index+1:]) if event.get('event') == 'user'), None)

        # Calculate the actual index in the original events list
        if previous_user_message_index is not None:
            previous_user_message_index = len(tracker.events) - (last_user_message_index + previous_user_message_index + 2)

            # Get the intent of the user message before the last one
            prev_last_intent = tracker.events[previous_user_message_index]['parse_data']['intent']['name']
            #print("prev_last_intent", prev_last_intent)
        
        entities = tracker.latest_message['entities']
        pizza_sliced_entity = next((e for e in entities if e['entity'] == 'pizza_sliced'), None)
        sliced = pizza_sliced_entity['value'] if pizza_sliced_entity else None
        #sliced = entities['pizza_sliced']
        # print("entities", entities)
        # print("sliced", sliced)
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get('name')
        #print("active_loop", active_loop)
        #print("requested_slot", requested_slot)
        if active_loop == "pizza_order_form":
            if last_intent == "response_positive" and requested_slot == "pizza_sliced" and prev_last_intent != "stop_order":
                return [SlotSet("pizza_sliced", True)]
            elif last_intent == "response_negative" and requested_slot == "pizza_sliced" and prev_last_intent != "stop_order":
                return [SlotSet("pizza_sliced", False)]
            elif last_intent in ["item_start_generic", "item_amount", "item_type", "pizza_size", "pizza_crust", "pizza_sliced"]:
                if sliced is not None and sliced.lower() == "true":
                    return [SlotSet("pizza_sliced", True)]
                elif sliced is not None and sliced.lower() == "false":
                    return [SlotSet("pizza_sliced", False)]
class ActionAskPizzaAmount(Action):
    def name(self):
        return 'action_ask_pizza_amount'
    
    def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        # reversed_events = list(reversed(tracker.events))
        # print(reversed_events[1])
        # modify_order = tracker.get_slot("modify_order")
        # if modify_order is not None:
        #     if modify_order == True:
        #         #dispatcher.utter_message(response="utter_ask_pizza_type_modify")
        #         return []#[FollowupAction("action_change_order")] 

        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_amount" and last_intent not in ["pizza_crust", "stop_order", "explain", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind"]:
            dispatcher.utter_message(response="utter_ask_pizza_amount_again")
            return []

        if last_intent == "item_start_generic":
            dispatcher.utter_message(response="utter_ask_pizza_amount_ack")
        elif last_intent == "item_size" and tracker.get_slot("pizza_size") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_amount_ack_size")
            #dispatcher.utter_message(text="How many pizzas of this size do you want?")
        elif last_intent == "item_type" and tracker.get_slot("pizza_type") is not None:
            #pizza_type = tracker.get_slot("pizza_type")
            #dispatcher.utter_message(text=f"Great choice! How many {pizza_type} pizzas do you want?")
            dispatcher.utter_message(response="utter_ask_pizza_amount_ack_type")
        elif last_intent == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_amount_ack")
        elif last_intent == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_amount_ack_crust")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_amount")
        return []

class ActionAskPizzaType(Action):
    def name(self):
        return 'action_ask_pizza_type'

    def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()

        # modify_order = tracker.get_slot("modify_order")
        # if modify_order is not None:
        #     if modify_order == True:
        #         #dispatcher.utter_message(response="utter_ask_pizza_type_modify")
        #         print("modify order")
        #         return []#[FollowupAction("action_change_order")] 

        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_type" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_types", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind"]:
            dispatcher.utter_message(response="utter_ask_pizza_type_again")
            return []

        if last_intent == "item_start_generic":
            dispatcher.utter_message(response="utter_ask_pizza_type_ack")
        elif last_intent == "item_amount" and tracker.get_slot("pizza_amount") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_type_ack_amount")
        elif last_intent == "item_size" and tracker.get_slot("pizza_size") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_type_ack_size")
        elif last_intent == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_type_ack")
        elif last_intent == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_type_ack_crust")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_type")
        return []

class ActionAskPizzaSize(Action):
    def name(self):
        return 'action_ask_pizza_size'

    def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()
        
        # modify_order = tracker.get_slot("modify_order")
        # if modify_order is not None:
        #     if modify_order == True:
        #         #dispatcher.utter_message(response="utter_ask_pizza_type_modify")
        #         return [FollowupAction("action_change_order")] 

        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_size" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_sizes", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind"]:
            dispatcher.utter_message(response="utter_ask_pizza_size_again")
            return []

        if last_intent == "item_start_generic":
            dispatcher.utter_message(response="utter_ask_pizza_size_ack")
        elif last_intent == "item_amount" and tracker.get_slot("pizza_amount") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_size_ack_amount")
        elif last_intent == "item_type" and tracker.get_slot("pizza_type") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_size_ack_type")
        elif last_intent == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_size_ack")
        elif last_intent == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_size_ack_crust")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_size")
        return[]

class ActionAskPizzaSliced(Action):
    def name(self):
        return 'action_ask_pizza_sliced'

    def run(self, dispatcher, tracker: Tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()

        # modify_order = tracker.get_slot("modify_order")
        # if modify_order is not None:
        #     if modify_order == True:
        #         #dispatcher.utter_message(response="utter_ask_pizza_type_modify")
        #         return [FollowupAction("action_change_order")] 

        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_sliced" and last_intent not in ["pizza_crust", "stop_order", "explain", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind"]:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_again")
            return []

        if last_intent == "item_start_generic":
            dispatcher.utter_message(response="utter_ask_pizza_sliced_ack")
        elif last_intent == "item_amount" and tracker.get_slot("pizza_amount") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_amount")
        elif last_intent == "item_type" and tracker.get_slot("pizza_type") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_type")
        elif last_intent == "item_size" and tracker.get_slot("pizza_size") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_size")
        elif last_intent == "pizza_crust" and tracker.get_slot("pizza_crust") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_sliced_ack_crust")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_sliced")
        return[]

class ActionAskPizzaCrust(Action):
    def name(self):
        return 'action_ask_pizza_crust'

    def run(self, dispatcher, tracker, domain):
        last_intent = tracker.get_intent_of_latest_message()

        # modify_order = tracker.get_slot("modify_order")
        # if modify_order is not None:
        #     if modify_order == True:
        #         #dispatcher.utter_message(response="utter_ask_pizza_type_modify")
        #         return [FollowupAction("action_change_order")] 

        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot == "pizza_crust" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_crusts", "response_negative", "bot_challenge", "item_change", "item_change_request_without_entity", "nevermind"]:
            dispatcher.utter_message(response="utter_ask_pizza_crust_again")
            return []

        if last_intent == "item_start_generic":
            dispatcher.utter_message(response="utter_ask_pizza_crust_ack")
        elif last_intent == "item_amount" and tracker.get_slot("pizza_amount") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_crust_ack_amount")
        elif last_intent == "item_type" and tracker.get_slot("pizza_type") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_crust_ack_type")
        elif last_intent == "item_size" and tracker.get_slot("pizza_size") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_crust_ack_size")
        elif last_intent == "pizza_sliced" and tracker.get_slot("pizza_sliced") is not None:
            dispatcher.utter_message(response="utter_ask_pizza_crust_ack")
        else:
            dispatcher.utter_message(response="utter_ask_pizza_crust")
        return[]

class ActionChangeOrder(Action):
    def name(self):
        return 'action_change_order'

    def run(self, dispatcher, tracker: Tracker, domain):
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
        if typeChanged:
            pizza_type = typeChanged
            #dispatcher.utter_message(response="utter_confirm_change_type")
            dispatcher.utter_message(text=f"Alright, I changed the pizza type to {pizza_type}")
        if sizeChanged:
            pizza_size = sizeChanged
            #dispatcher.utter_message(response="utter_confirm_change_size")
            dispatcher.utter_message(text=f"No problem, I changed the size to {pizza_size}")
        if amountChanged:
            pizza_amount = amountChanged
            #dispatcher.utter_message(response="utter_confirm_change_amount")
            dispatcher.utter_message(text=f"Sure, I changed the number of pizzas to {pizza_amount}")
        if crustChanged:
            pizza_crust = crustChanged
            #dispatcher.utter_message(response="utter_confirm_change_crust")
            dispatcher.utter_message(text=f"Alright, I changed the crust to {pizza_crust}")
        if slicedChanged:
            pizza_sliced = slicedChanged
            if pizza_sliced == "true":
                #dispatcher.utter_message(response="utter_confirm_change_sliced")
                dispatcher.utter_message(text=f"Alright, the pizzas will be sliced")
                pizza_sliced = True
            else:
                #dispatcher.utter_message(response="utter_confirm_change_not_sliced")
                dispatcher.utter_message(text=f"Alright, the pizzas won't be sliced")
                pizza_sliced = False
        return [
            SlotSet("pizza_type", pizza_type),
            SlotSet("pizza_size", pizza_size),
            SlotSet("pizza_amount", pizza_amount),
            SlotSet("pizza_crust", pizza_crust),
            SlotSet("pizza_sliced", pizza_sliced),
            SlotSet("modify_order", None),
        ]