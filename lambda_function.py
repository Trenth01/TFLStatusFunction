import json
import requests
from difflib import get_close_matches

def lambda_handler(event, context):
    # TfL API endpoint for line statuses
    url = "https://api.tfl.gov.uk/line/mode/tube/status"
    
    # Default lines of interest for alarm invocation
    default_lines = ['Victoria', 'Circle', 'District']
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Extract user-requested lines from the event
        user_input = event.get('request', {}).get('intent', {}).get('slots', {}).get('line', {}).get('value', '').strip()
        
        # Determine lines to check
        if user_input:
            all_lines = [line['name'] for line in data]
            matched_line = get_close_matches(user_input, all_lines, n=1, cutoff=0.5)
            if matched_line:
                lines_of_interest = matched_line
            else:
                return {
                    "version": "1.0",
                    "statusCode": 200,
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": f"Sorry, I couldn't find a line matching '{user_input}'. Please try again."
                        },
                        "shouldEndSession": True
                    }
                }
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
                    if reason:
                        message = reason
                    else:
                        message = f"The {line_name} line has {status_description.lower()}."
                    status_messages.append(message)
                else:
                    good_service_count += 1
        
        # Prepare the final status message
        if good_service_count == len(lines_of_interest):
            final_status = "Good service on all requested lines."
        elif good_service_count == 0:
            final_status = ' '.join(status_messages)
        else:
            final_status = ' '.join(status_messages)
            final_status += " Good service on other requested lines."
        
        # Return the response in Alexa-friendly format
        return {
            "version": "1.0",
            'statusCode': 200,
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': final_status
                },
                'shouldEndSession': True
            }
        }

    except Exception as e:
        return {
            'version': "1.0",
            'statusCode': 500,
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': f"An error occurred while fetching the tube status: {str(e)}"
                },
                'shouldEndSession': True
            }
        }
