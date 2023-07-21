import imaplib
import email
from email.header import decode_header
import time
import spacy
import os
import json
import requests
from doccano_client import DoccanoClient


geturl = "https://api.businesscentral.dynamics.com/v2.0/senzcraft.com/production/api/v2.0/companies(56a77713-529e-ed11-988a-000d3a473558)/items"
posturl = "https://api.businesscentral.dynamics.com/v2.0/senzcraft.com/production/api/v2.0/companies(56a77713-529e-ed11-988a-000d3a473558)/salesOrders"
auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJodHRwczovL2FwaS5idXNpbmVzc2NlbnRyYWwuZHluYW1pY3MuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvYzRmZmMxNDYtOWZkOS00NDZjLWI1N2YtZDU5ODNmMzllNGU0LyIsImlhdCI6MTY4ODAzNDAzOSwibmJmIjoxNjg4MDM0MDM5LCJleHAiOjE2ODgwMzg0NjIsImFjciI6IjEiLCJhaW8iOiJBVFFBeS84VEFBQUE4NDhpYjgwVnNzZTB4RjU1bnBFd2o2WmhHR21yOTFucVBLOUxla3hxNlNhUkthMDc1YVRTcFFlZ2ZOM0g1MVNLIiwiYW1yIjpbInB3ZCJdLCJhcHBpZCI6ImI0MGIwZDRkLTUzNDctNDZkZi04OTA1LTQwZjU2ZTZkM2M4YiIsImFwcGlkYWNyIjoiMSIsImZhbWlseV9uYW1lIjoiVW5uaSIsImdpdmVuX25hbWUiOiJBcmRyYSIsImlwYWRkciI6IjEwMy4xNjUuMjAuMTAwIiwibmFtZSI6IkFyZHJhIFUiLCJvaWQiOiIzMmM0MGJkOC1mM2Y0LTQyOTUtYTU3ZS03MzFlOGVmZjU1NWUiLCJwdWlkIjoiMTAwMzIwMDI1RjU2RjMzRiIsInJoIjoiMC5BWEFBUnNIX3hObWZiRVMxZjlXWVB6bms1RDN2Ylpsc3MxTkJoZ2VtX1R3QnVKOXdBTUUuIiwic2NwIjoiRmluYW5jaWFscy5SZWFkV3JpdGUuQWxsIHVzZXJfaW1wZXJzb25hdGlvbiIsInN1YiI6IjBYV1FWVXJXNUVIWm5PQXdVVTVibUlMclZMTHZxTEtrNnppTEZoR3Q3TEEiLCJ0aWQiOiJjNGZmYzE0Ni05ZmQ5LTQ0NmMtYjU3Zi1kNTk4M2YzOWU0ZTQiLCJ1bmlxdWVfbmFtZSI6ImFyZHJhLnVAc2VuemNyYWZ0LmNvbSIsInVwbiI6ImFyZHJhLnVAc2VuemNyYWZ0LmNvbSIsInV0aSI6IkUxVlBNVFNnR1VPTWc2V3VhelFZQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdfQ.AIDkJaDy0fGOUeTdkzL0osXXPuTVeemabPGFsMSvjl8MQPrHqW-ce0eqcD3PuQ_ByFbcvDxomsuNmMcLeVTdlEEAqsXabWBUHZs3Esc808h57jadDCeb7xyrvOvEBzbNNFDTeuGsY5y_Wx7WrGKSRIL3ptSWGafPyZ_eZNeSiRJNBxTRgchRLymdpcD0yudhtN0rIUVtNYn0YwqqetENs5vtNhFiZF5RWVaZOfMHBdGFu2G4bGV7jIgWu3uL1Vws5Ggv1P5vPMGUO6JTujpDYOInOKUdPdexbwI8cYag5Sdyiit5A7rcNQYN4FVVESgNba0ahwGh4X5snf-jOrSfow"

# Getting the productdetails


def get_data(url, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error:", response.status_code, response.text)
        return None


def get_itemid_and_unit_price(product_list, jres):
    id_list = []
    unit_price_list = []

    item_list = jres["value"]
    for product in product_list:
        for item in item_list:
            if product in item['displayName']:
                id_list.append(item['id'])
                unit_price_list.append(item['unitPrice'])
    return id_list, unit_price_list


def post_to_dynamics(url, salesorder):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    response = requests.post(url=url, headers=headers, json=salesorder)

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        return data
    else:
        print("Error:", response.status_code, response.text)
        return None


def dynamics_upload_main(product_list, quantity_list):
    jres = get_data(geturl, auth_token)
    if jres != None:
        id_list, unit_price_list = get_itemid_and_unit_price(
            product_list, jres)
        # Create a list of dictionaries for each line item
        sales_order_lines = []
        for i in range(len(id_list)):
            line_item = {
                "itemId": id_list[i],
                "quantity": quantity_list[i],
                "unitPrice": unit_price_list[i]
            }
        sales_order_lines.append(line_item)

        # Create the main dictionary with the "salesOrderLines" key
        sales_order = {
            "customerNumber": "10000",
            "salesOrderLines": sales_order_lines
        }

        # Print the resulting JSON
        print(json.dumps(sales_order, indent=4))
        post_to_dynamics(posturl, sales_order)


def manual_review(entities_list):
    # Write the list of dictionaries to a JSONL file
    with open("dags/python_files/order_letter_ner/entities.jsonl", "w") as f:
        for entities in entities_list:
            f.write(json.dumps(entities) + "\n")

    # instantiate a client and log in to a Doccano instance
    client = DoccanoClient('http://localhost:8000/')
    client.login(username='admin', password='password')

    # get basic information about the authorized user
    r_me = client.get_profile()

    # print the details from the above query
    print(r_me)
    # upload a json file to project 1. If file is in current directory, file_path is omittable
    r_json_upload = client.upload(project_id=4, file_paths=[os.path.join(
        os.getcwd(), 'dags/python_files/order_letter_ner/entities.jsonl')], format='JSONL', task='SequenceLabeling')
    print("Upload Completed")
