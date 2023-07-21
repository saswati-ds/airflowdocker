from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.models import TaskInstance
import imaplib
import email
from email.header import decode_header
import time
import spacy
import os
import json
import requests
import ast


# IMAP settings for your email provider
# Replace with the appropriate IMAP server address
imap_server = "outlook.office365.com"
imap_port = 993  # Replace with the appropriate IMAP port
username = "demoofficial@outlook.com"  # Replace with your email ID
password = "Abin@12914"  # Replace with your email password

geturl = "https://api.businesscentral.dynamics.com/v2.0/senzcraft.com/production/api/v2.0/companies(56a77713-529e-ed11-988a-000d3a473558)/items"
posturl = "https://api.businesscentral.dynamics.com/v2.0/senzcraft.com/production/api/v2.0/companies(56a77713-529e-ed11-988a-000d3a473558)/salesOrders"
auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJodHRwczovL2FwaS5idXNpbmVzc2NlbnRyYWwuZHluYW1pY3MuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvYzRmZmMxNDYtOWZkOS00NDZjLWI1N2YtZDU5ODNmMzllNGU0LyIsImlhdCI6MTY4ODM3MjM3NywibmJmIjoxNjg4MzcyMzc3LCJleHAiOjE2ODgzNzY2NjYsImFjciI6IjEiLCJhaW8iOiJBVFFBeS84VEFBQUEvRU1sK3RNVUw5U2E0OTBGL0F1aTA5bG5zMW8rYXpsa1prcWY2YU91dlU4TFIwSTd1dmRwUkQ3N1d2VXBhYy9zIiwiYW1yIjpbInB3ZCJdLCJhcHBpZCI6ImI0MGIwZDRkLTUzNDctNDZkZi04OTA1LTQwZjU2ZTZkM2M4YiIsImFwcGlkYWNyIjoiMSIsImZhbWlseV9uYW1lIjoiVW5uaSIsImdpdmVuX25hbWUiOiJBcmRyYSIsImlwYWRkciI6IjEwMy4xNjUuMjAuMTAwIiwibmFtZSI6IkFyZHJhIFUiLCJvaWQiOiIzMmM0MGJkOC1mM2Y0LTQyOTUtYTU3ZS03MzFlOGVmZjU1NWUiLCJwdWlkIjoiMTAwMzIwMDI1RjU2RjMzRiIsInJoIjoiMC5BWEFBUnNIX3hObWZiRVMxZjlXWVB6bms1RDN2Ylpsc3MxTkJoZ2VtX1R3QnVKOXdBTUUuIiwic2NwIjoiRmluYW5jaWFscy5SZWFkV3JpdGUuQWxsIHVzZXJfaW1wZXJzb25hdGlvbiIsInN1YiI6IjBYV1FWVXJXNUVIWm5PQXdVVTVibUlMclZMTHZxTEtrNnppTEZoR3Q3TEEiLCJ0aWQiOiJjNGZmYzE0Ni05ZmQ5LTQ0NmMtYjU3Zi1kNTk4M2YzOWU0ZTQiLCJ1bmlxdWVfbmFtZSI6ImFyZHJhLnVAc2VuemNyYWZ0LmNvbSIsInVwbiI6ImFyZHJhLnVAc2VuemNyYWZ0LmNvbSIsInV0aSI6ImtXZ0RZN2tlekVhVVlWR2o2RzViQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdfQ.RQaVP0TzsGNjAZfGicbt1TtzqnXojHv_LBF7sJO-wSoOc3hilA5yfs1ovoP2ueyDhYiOwS9D9x0sczz-9qms8VaNW9k7WnO6muV_eBouo5AASBHv1rl9Voln8yaP7H7kr6w5uPmM8ujlEd3CVuE4cnaM5Fn3RVHxIFkBS9medpbmqi5UPwL5eJlfyIQpLIUfyGS2zBt7bhGJy1TPfzx3lwjThWnoGC0JnXnrqZoGmYV8nhzeqSDLmK2Vuohkbx77NrI0iegBVYUiBOwpIreNwMSkwBRloCfqeGtcjYxzlRpH_amSg1ZWES_snj_WD2bOmlJOpPf04uiXK1gwB3LQtw"


def read_order_from_mail():
    while True:
        try:
            # Connect to the IMAP server
            imap = imaplib.IMAP4_SSL(imap_server, imap_port)
            imap.login(username, password)

            # Select the mailbox you want to read from
            mailbox = "INBOX"
            imap.select(mailbox)

            # Search for unread emails with a specific subject
            search_query = f'(UNSEEN SUBJECT "Purchase Order")'
            status, messages = imap.search(None, search_query)

            # Loop through the emails and print the subject and sender
            for num in messages[0].split():
                _, msg_data = imap.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]

                # Parse the email
                msg = email.message_from_bytes(email_body)
                subject = decode_header(msg["Subject"])[0][0]
                sender = decode_header(msg["From"])[0][0]

                # Print the content of the email
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            content = part.get_payload(decode=True).decode()
                            print(content)
                            return content
                else:
                    content = msg.get_payload(decode=True).decode()
                    return content

        except Exception as e:
            print("An error occurred:", str(e))

         # Wait for 10 seconds before checking again
        time.sleep(10)


def extract_product_and_quantity(**context):
    confidence = 70
    content = context['task_instance'].xcom_pull(
        task_ids='read_order_from_mail')
    # load model
    nlp_ner = spacy.load("dags/furniture-spacy-best")
    entities_list = []
    doc = nlp_ner(content)
    # print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    # Create a dictionary to store the entities and their labels for each text
    entities = {}
    entities["text"] = content
    entities["label"] = []

    # Iterate over the entities and add them to the dictionary
    for ent in doc.ents:
        entities["label"].append([ent.start_char, ent.end_char, ent.label_])

    # Add the dictionary for each text to the list of dictionaries
    entities_list.append(entities)
    # convert dict to string
    entities_str = json.dumps(entities["label"])
    # extract entities from the Doc object
    product_list = []
    str_quantity_list = []
    quantity_list = []
    due_list = []
    for ent in doc.ents:
        if ent.label_ == "PRODUCT":
            product_list.append((ent.text))
        if ent.label_ == "QUANTITY":
            str_quantity_list.append((ent.text))
        if ent.label_ == "DUEDATE":
            due_list.append((ent.text))

    # converting string to integer
    for string in str_quantity_list:
        # remove all non-digits from string
        num_str = ''.join(filter(str.isdigit, string))
        # convert the resulting string of digits to an integer
        num = int(num_str)
        quantity_list.append(num)

    return confidence, entities_list, product_list, quantity_list

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


def dynamics_upload_main(**context):
    product_list = context['ti'].xcom_pull(
        task_ids='extract_product_and_quantity', key=None)[2]
    quantity_list = context['ti'].xcom_pull(
        task_ids='extract_product_and_quantity', key=None)[3]
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


def check_confidence(confidence):
    confidence = int(confidence)  # Convert confidence to an integer
    if confidence >= 70:
        return 'post_to_dynamics_task'
    else:
        return 'manual_review_task'


default_args = {
    'owner': 'Abin Jilson',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}
with DAG(
    dag_id='order-letter_NER',
    default_args=default_args,
    description='Extracting products and quantity details from order-letter received in mail and upload it to dynamics',
    start_date=datetime(2023, 6, 27),
    schedule_interval='@daily'
) as dag:
    read_order_from_mail_task = PythonOperator(
        task_id='read_order_from_mail',
        python_callable=read_order_from_mail,
        provide_context=True
    )

    extract_product_and_quantity_task = PythonOperator(
        task_id='extract_product_and_quantity',
        python_callable=extract_product_and_quantity,
        provide_context=True
    )

    post_to_dynamics_task = PythonOperator(
        task_id='post_to_dynamics_task',
        python_callable=dynamics_upload_main,
        provide_context=True,  # Pass the task context to the function,
        trigger_rule='all_success'  # Task will run only if previous task succeeds
    )

    check_confidence_task = PythonOperator(
        task_id='check_confidence_task',
        python_callable=check_confidence,
        op_args=[
            '{{ task_instance.xcom_pull(task_ids="extract_product_and_quantity")[0] }}',
        ],
        trigger_rule='all_success'  # Task will run only if previous task succeeds
    )

    read_order_from_mail_task >> extract_product_and_quantity_task >> check_confidence_task >> [
        post_to_dynamics_task]
