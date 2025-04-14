# -*- coding: utf-8 -*-

import logging
import json
import requests
from difflib import get_close_matches

import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome to the London Underground Status skill. You can ask about a tube line like the Victoria line."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class TubeStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("TubeStatusIntent")(handler_input)

    def handle(self, handler_input):
        url = "https://api.tfl.gov.uk/line/mode/tube/status"
        default_lines = ['Victoria', 'Circle', 'District']

        try:
            response = requests.get(url)
            data = response.json()

            user_input = ask_utils.get_slot_value(handler_input, "line") or ""
            user_input = user_input.strip()

            if user_input:
                all_lines = [line['name'] for line in data]
                matched_line = get_close_matches(user_input, all_lines, n=1, cutoff=0.5)
                if matched_line:
                    lines_of_interest = matched_line
                else:
                    return handler_input.response_builder.speak(
                        f"Sorry, I couldn't find a line matching {user_input}. Please try again.") \
                        .set_should_end_session(True).response
            else:
                lines_of_interest = default_lines

            status_messages = []
            good_service_count = 0

            for line in data:
                if line['name'] in lines_of_interest:
                    line_name = line['name']
                    status_description = line['lineStatuses'][0]['statusSeverityDescription']
                    reason = line['lineStatuses'][0].get('reason', '')

                    if status_description != "Good Service":
                        message = reason if reason else f"The {line_name} line has {status_description.lower()}."
                        status_messages.append(message)
                    else:
                        good_service_count += 1

            if len(lines_of_interest) == 1 and good_service_count == 1:
                final_status = f"There is currently good service on the {user_input} line"
            elif good_service_count == len(lines_of_interest):
                final_status = "Good service on requested London Underground lines."
            elif good_service_count == 0:
                final_status = ' '.join(status_messages)
            else:
                final_status = ' '.join(status_messages)
                final_status += " Good service on other requested lines."

            return handler_input.response_builder.speak(final_status).set_should_end_session(True).response

        except Exception as e:
            return handler_input.response_builder.speak(
                f"An error occurred while fetching the tube status: {str(e)}") \
                .set_should_end_session(True).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "You can ask about the status of any London Underground line. For example, say 'what's the status of the Victoria line?'"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"
        return handler_input.response_builder.speak(speak_output).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = f"You just triggered {intent_name}."
        return handler_input.response_builder.speak(speak_output).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TubeStatusIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
