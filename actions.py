# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ActionConfirmPizzas(Action):
	def name(self):
		return 'action_confirm_pizzas'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_sliced = tracker.get_slot("pizza_sliced")
		order_details = ""
		#for amount, type, size in zip(pizza_amount, pizza_type, pizza_size):
		order_details += f"{pizza_amount} {pizza_size} {pizza_type}"
		#order_details = ", ".join(order_details)
		order_details += ". All pizzas" + ( " sliced" if pizza_sliced == True else " not sliced")
		dispatcher.utter_message(text="So you want to order "+order_details+". Is everything correct?")
		#old_order = tracker.get_slot("total_order")
		return [SlotSet("pending_order", order_details)]

class ActionChangeOrder(Action):
	def name(self):
		return 'action_change_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		SlotSet("pizza_type", pizza_type)
		SlotSet("pizza_size", pizza_size)
		SlotSet("pizza_amount", pizza_amount)
		return[]

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

		restaurant_address = "Via Giuseppe Verdi, 15, 38122 Trento TN"

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
		elif pizza_category.lower() == "meat":
			dispatcher.utter_message(response="utter_inform_pizza_types_meat")
		elif pizza_category.lower() in ["vegetarian", "vegan", "vegetable", "veggie"]:
			dispatcher.utter_message(response="utter_inform_pizza_types_vegetarian")
		else:
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

		if isinstance(slot_value, str):
			if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                     "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
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

class ActionAskPizzaAmount(Action):
	def name(self):
		return 'action_ask_pizza_amount'
	
	def run(self, dispatcher, tracker, domain):
		last_intent = tracker.get_intent_of_latest_message()
  
		requested_slot = tracker.get_slot("requested_slot")
		if requested_slot == "pizza_amount" and last_intent not in ["pizza_crust", "stop_order", "explain"]:
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
		return[]

class ActionAskPizzaType(Action):
	def name(self):
		return 'action_ask_pizza_type'

	def run(self, dispatcher, tracker, domain):
		last_intent = tracker.get_intent_of_latest_message()

		requested_slot = tracker.get_slot("requested_slot")
		if requested_slot == "pizza_type" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_types"]:
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
  
		requested_slot = tracker.get_slot("requested_slot")
		if requested_slot == "pizza_size" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_sizes"]:
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

	def run(self, dispatcher, tracker, domain):
		last_intent = tracker.get_intent_of_latest_message()
  
		requested_slot = tracker.get_slot("requested_slot")
		if requested_slot == "pizza_sliced" and last_intent not in ["pizza_crust", "stop_order", "explain"]:
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
  
		requested_slot = tracker.get_slot("requested_slot")
		if requested_slot == "pizza_crust" and last_intent not in ["pizza_crust", "stop_order", "explain", "request_pizza_crusts"]:
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