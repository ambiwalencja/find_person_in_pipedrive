import phonenumbers
from .classes import PipedriveApi, Content, extract_phone_from_text, convert_new_client_data
from db.db_connect import get_db
from db.db_find_person import new_execution, update_execution_success, update_execution_output
import logger
import json
import os
import traceback
import resend
import requests

def find_person_in_pipedrive(new_client, dry_run):
    if dry_run:
        logger.logger.info(f'THIS IS DRY RUN')
    logger.logger.info(f'Decoded a new client data: name - {new_client["Name"]}, email - {new_client["Email"]}, phone - {new_client["Phone"]}, other data (tba)')
    
    new_execution_data = new_execution(next(get_db()), new_client)

    resend.api_key = os.environ["RESEND_API_KEY"]

    new_request = PipedriveApi()
    person_id = 0
    person_owner_id = 0
    persons_by_phone = []
    persons_by_email = []
    phone = 0
    logger.logger.info(f'Defined an object for requests, as well as variables for person_id and lists of phones and emails.')

    # prepare for phone number parsing
    phone = extract_phone_from_text(new_client["Phone"])
    # search by phone
    try:
        phone = phonenumbers.parse(phone, "PL") # Polish is default country code
    except Exception as e:
        logger.logger.error(f'Parsing phone: {phone} failed, error: {traceback.format_exc()}')
        new_client["Phone"] = ""
    else:
        if phonenumbers.is_valid_number(phone):
            new_client["Phone"] = str(phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)) # correct number is overwritten in client data
            logger.logger.info(f'The number {new_client["Phone"]} is valid')
            try:
                search_response = new_request.search_persons("phone", phone.national_number)
                if search_response.status_code >= 204:
                    error_message = f'Status code of the response from searching persons by phone: {search_response.status_code}, {search_response.text}'
                    logger.logger.error(error_message)
                    update_execution_success(next(get_db()), new_execution_data, False, error_message)
                    return error_message
                logger.logger.info(f'Sent a request for searching persons by phone, status code of the response: {search_response.status_code}')
            except Exception as e:
                error_message = f'Sending request for searching persons by phone failed, error: {traceback.format_exc()}'
                logger.logger.error(error_message)
                update_execution_success(next(get_db()), new_execution_data, False, error_message)
                return error_message
            else:
                persons_by_phone = search_response.json()['data']['items']
                logger.logger.info(f'Received a list of persons by phone: {persons_by_phone}')
        else: # number is irrelevant
            new_client["Phone"] = ""
    
    # search by email
    try:
        search_response = new_request.search_persons("email", new_client["Email"])
        if search_response.status_code >= 204:
            error_message = f'Status code of the response from searching persons by email: {search_response.status_code}, {search_response.text}'
            logger.logger.error(error_message)
            update_execution_success(next(get_db()), new_execution_data, False, error_message)
            return error_message
        logger.logger.info(f'Sent a request for searching persons by email, status code of the response: {search_response.status_code}')
    except Exception as e:
        error_message = f'Sending request for searching persons by email failed, error: {traceback.format_exc()}'
        logger.logger.error(error_message)
        update_execution_success(next(get_db()), new_execution_data, False, error_message)
        return error_message
    else:
        persons_by_email = search_response.json()['data']['items']
        logger.logger.info(f'Received a list of persons by email: {persons_by_email}')
    
    # search result options:
    if len(persons_by_phone) == 0 and len(persons_by_email) == 0:
        logger.logger.info(f'No persons were found')
        person_owner_id = 11645848
        try:
            if not dry_run:
                create_person_response = new_request.create_person(new_client["Name"], person_owner_id, new_client["Email"], new_client["Phone"], new_client["Zrodlo_Person"])
                if create_person_response.status_code >= 204:
                    error_message = f'Status code of the response from creating person: {create_person_response.status_code}, {search_response.text}'
                    logger.logger.error(error_message)
                    update_execution_success(next(get_db()), new_execution_data, False, error_message)
                    return error_message
                logger.logger.info(f'Sent a request for creating person, status code of the response: {create_person_response.status_code}')
            else:
                logger.logger.info(f'DRY_RUN: Not creating person with data: {new_client["Name"]}, {person_owner_id}, {new_client["Email"]}, {new_client["Phone"]}')
        except Exception as e:
            error_message = f'Sending request for creating a person failed, error: {traceback.format_exc()}'
            logger.logger.error(error_message)
            update_execution_success(next(get_db()), new_execution_data, False, error_message)
            return error_message
        else:
            if not dry_run:
                person_id = create_person_response.json()['data']['id']
                logger.logger.info(f'Created a person in Pipedrive with data: {new_client["Name"]}, {new_client["Email"]}, {new_client["Phone"]},\
                                    person ID: {person_id}, ')
            else:
                logger.logger.info(f'DRY_RUN: person ID: {person_id}, ')
    elif len(persons_by_phone) == 1 and len(persons_by_email) == 0:
        logger.logger.info(f'One person was found by phone')
        person_id = persons_by_phone[0]['item']['id']
        person_owner_id = persons_by_phone[0]['item']['owner']['id']
        logger.logger.info(f'Got a person ID from persons_by_phone list: {person_id}')
        try:
            if not dry_run:
                update_person_response = new_request.update_person(person_id, 'email', persons_by_phone[0]['item']['emails'], new_client["Email"])
                logger.logger.info(f'Status code of the response from updating person: {update_person_response.status_code}')
                if update_person_response.status_code >= 204:
                    error_message = f'Request unsuccessful: {search_response.text}'
                    logger.logger.error(error_message)
                    update_execution_success(next(get_db()), new_execution_data, False, error_message)
                    return error_message
                else:
                    logger.logger.info(f'Updated a found person with id: {person_id} by adding an email: {new_client["Email"]}')
            else:
                logger.logger.info(f'DRY_RUN: Not updating person with email: {new_client["Email"]}')
        except Exception as e:
            error_message = f'Sending request for updating a person found by phone failed, error: {traceback.format_exc()}'
            logger.logger.error(error_message)
            update_execution_success(next(get_db()), new_execution_data, False, error_message)
            return error_message
    elif len(persons_by_phone) == 0 and len(persons_by_email) == 1:
        logger.logger.info(f'One person was found by email')
        person_id = persons_by_email[0]['item']['id']
        person_owner_id = persons_by_email[0]['item']['owner']['id']
        logger.logger.info(f'Got a person ID from persons_by_email list: {person_id}')
        if phone:
            if phonenumbers.is_valid_number(phone):
                try:
                    if not dry_run:
                        update_person_response = new_request.update_person(person_id, 'phone', persons_by_email[0]['item']['phones'], new_client["Phone"])
                        logger.logger.info(f'Status code of the response from updating person: {update_person_response.status_code}')
                        if update_person_response.status_code >= 204:
                            error_message = f'Request unsuccessful: {search_response.text}'
                            logger.logger.error(error_message)
                            update_execution_success(next(get_db()), new_execution_data, False, error_message)
                            return error_message
                        else:
                            logger.logger.info(f'Updated a found person with id: {person_id} by adding phone: {new_client["Phone"]}')
                    else:
                        logger.logger.info(f'DRY_RUN: Not updating person with phone: {new_client["Phone"]}')
                except Exception as e:
                    error_message = f'Sending request for updating a person found by email failed, error: {traceback.format_exc()}'
                    logger.logger.error(error_message)
                    update_execution_success(next(get_db()), new_execution_data, False, error_message)
                    return error_message
    elif len(persons_by_phone) == 1 and len(persons_by_email) == 1 and persons_by_phone[0]['item']['id'] == persons_by_email[0]['item']['id']:
        person_id = persons_by_phone[0]['item']['id']
        person_owner_id = persons_by_phone[0]['item']['owner']['id']
        logger.logger.info(f'One person was found by both email and phone, with id {person_id}')
    else:
        logger.logger.info(f'Multiple persons were found: {len(persons_by_phone)} by phone and {len(persons_by_email)} by email.')
        new_content = Content()
        try:
            new_content.create_email_content(persons_by_phone, persons_by_email)
            table_of_persons = new_content.table
        except Exception as e:
            error_message = f'Creating email content failed, error: {traceback.format_exc()}'
            logger.logger.error(error_message)
            update_execution_success(next(get_db()), new_execution_data, False, error_message)
            return error_message
        else:
            logger.logger.info(f'Created table with found persons: {table_of_persons}')
            try:
                params: resend.Emails.SendParams = {
                    "sender": "Find Person In Pipedrive <findperson@automation.futurecollars.com>",
                    "to": ["dev@futurecollars.com", "it@futurecollars.com"],
                    "subject": "Duplikaty osób kontaktowych w Pipedrive",
                    "html": table_of_persons.get_html_string(),
                    "reply_to": "it@futurecollars.com"
                }
            except Exception as e:
                error_message = f'Creating email failed, error: {traceback.format_exc()}'
                logger.logger.error(error_message)
                update_execution_success(next(get_db()), new_execution_data, False, error_message)
                return error_message
            else:
                logger.logger.info(f'Created an email message with the table')
                try:
                    if not dry_run:
                        email = resend.Emails.send(params) # attention, can stop working when resend is updated
                        logger.logger.info(f'Sent an email from {email.sender} to {email.to}')
                    else:
                        params['subject'] = "DRY RUN: Duplikaty osób kontaktowych w Pipedrive"
                        email = resend.Emails.send(params) # attention, can stop working when resend is updated
                        logger.logger.info(f'DRY RUN: Sent an email from {email.sender} to {email.to}')
                except Exception as e:
                    error_message = f'Sending an email from {params["sender"]} to {params["to"]} failed, error: {traceback.format_exc()}'
                    logger.logger.error(error_message)
                    update_execution_success(next(get_db()), new_execution_data, False, error_message)
                    return error_message
                else:
                    if len(persons_by_phone) > 0:
                        person_id = persons_by_phone[0]['item']['id']
                        person_owner_id = persons_by_phone[0]['item']['owner']['id']
                        logger.logger.info(f'Set person_id as an id of a person found by phone: {person_id}')
                    else:
                        person_id = persons_by_email[0]['item']['id']
                        person_owner_id = persons_by_email[0]['item']['owner']['id']
                        logger.logger.info(f'Set person_id as an id of a person found by email: {person_id}')
    new_client["Person ID"] = person_id
    new_client["Person Owner ID"] = person_owner_id

    # change keys names to readable for zapier
    new_client = convert_new_client_data(new_client)

    new_client_json_output = json.dumps(new_client)
    # send output to zapier webhook
    try:
        r = requests.post(new_client["Webhook"], data=new_client_json_output, headers={'Content-Type': 'application/json'})
        logger.logger.info(f'Sent output data to Zapier webhook: {new_client["Webhook"]}')
    except Exception as e:
        error_message = f'Sending output data to Zapier webhook failed, error: {traceback.format_exc()}'
        logger.logger.error(error_message)
        update_execution_success(next(get_db()), new_execution_data, False, error_message)
        return error_message
    # update database
    update_execution_success(next(get_db()), new_execution_data, True, '')
    update_execution_output(next(get_db()), new_execution_data, person_id, person_owner_id, new_client)
    return new_client_json_output