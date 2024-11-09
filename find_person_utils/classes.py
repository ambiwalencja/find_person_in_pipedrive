import requests
import json
from prettytable import PrettyTable
import os

class PipedriveApi:
    def __init__(self):
        self.key = os.environ.get('PIPEDRIVE_API_KEY')
        self.urlBase = os.environ.get('PIPEDRIVE_URL_BASE')

    def search_persons(self, field, value):
        url = f'{self.urlBase}persons/search?term={value}&fields={field}&exact_match=0&start=0&limit=10&api_token={self.key}'
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Cookie': '__cf_bm=1BMPIZ5jRcEINNQ2huldQXIEsNJlk18sBaJziGNUrGU-1694632497-0-AWUaUVEkvxDCPLbHsHo+KNoEqSs7WkRp9Z0ikWchtryk2/E/UUcgRRNbUGbmuf1LuWbsjFTNiKGR+qCvIcRy8T8='
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return response

    def create_list_of_dicts(self, list_of_strings):
        list_of_dicts = []
        for string in list_of_strings:
            list_of_dicts.append({"value": string})
        return list_of_dicts

    def update_person(self, person_id, field, old_values, new_value):
        url = f'{self.urlBase}persons/{person_id}?api_token={self.key}'
        values = self.create_list_of_dicts(old_values)
        values.append({'value': new_value})
        payload = json.dumps({field: values})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
        return response

    def create_person(self, name, owner_id, email, phone, source):
        url = f"{self.urlBase}persons?api_token={self.key}"
        payload = json.dumps({
            "name": name,
            "owner_id": owner_id,
            "email": [{"value": email, "primary": "True"}],
            "phone": [{"value": phone, "primary": "True"}],
            "5aa18a52092ff5b167f634a0dc0c3ad9ef1ea85c": source 
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cookie': '__cf_bm=e5PkpufP1Bv4jMnf5PRCGXA7sPgKskmYw3FDDK_S28A-1695064497-0-AUqpBHd+BRcdrduZVOWfji4JZQ+2i+ugc9QnypiR1s03VloAgKrV3WD83wuzmHpSzG7ahbHa99MKmteOSb06ihs='
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response

class Content:
    def __init__(self):
        self.table = PrettyTable()

    def row_exists(self, row):
        for existing_row in self.table.rows:
            if existing_row == row:
                return True
        return False

    def write_person_list_to_table(self, person_list):
        for i, e in enumerate(person_list):
            id = person_list[i]['item']['id']
            row = [person_list[i]['item']['name'], 
                    person_list[i]['item']['emails'], 
                    person_list[i]['item']['phones'], 
                    f'https://futurecollars.pipedrive.com/person/{id}', 
                    person_list[i]['item']['owner']['id']]
            if not self.row_exists(row):
                self.table.add_row(row)
        return True
    
    def create_email_content(self, list1, list2):
        self.table.field_names = ["Name", "Email", "Phone", "Link", "Owner"]
        self.write_person_list_to_table(list1)
        self.write_person_list_to_table(list2)
        return True

def extract_phone_from_text(text):
    phone_number = text
    number_of_chars = len(text)
    space_position = text.find(' ')
    if number_of_chars > 13:
        if space_position > 8:
            phone_number = text[:space_position]
    return phone_number

# change keys names to readable for zapier
def convert_new_client_data(client_data):
    client_data["Kontakt z doradcą"] = client_data["Kontakt_z_doradca"]
    client_data["Deal Owner"] = client_data["Deal_Owner"]
    client_data["Źródło szczegółowe"] = client_data["Zrodlo_szczegolowe"]
    client_data["Źródło (Deal)"] = client_data["Zrodlo_Deal"]
    client_data["Źródło (Person)"] = client_data["Zrodlo_Person"]
    client_data["Wynik testu"] = client_data["Wynik_testu"]
    client_data["Kraj/rynek"] = client_data["Kraj_rynek"]
    client_data["Termin kursu (Amazon)"] = client_data["Termin_kursu_Amazon"]
    keys_to_remove = ["Kontakt_z_doradca", "Deal_Owner", "Zrodlo_szczegolowe", "Zrodlo_Deal",
                      "Zrodlo_Person", "Wynik_testu", "Kraj_rynek", "Termin_kursu_Amazon"]
    for k in keys_to_remove:
        client_data.pop(k, None)
    return client_data