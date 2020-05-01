from api import MakeLeapsAPI
import time

"""
Main application that sends documents via MakeLeapsAPI
Creates one document, as well as read in pre-existing ones,
then sends them to a client
"""

CLIENT_ID = '<your_client_id>'
CLIENT_SECRET = '<your_client_secret>'

api = MakeLeapsAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

partner_mid = "XXXXXXXXXXXXXXXXXXX"

# Create client
client = {
    "client_external_id": "CLIENT-12345",
    "contacts": [
        {
            "contact_type": "organization",
            "name": "Example Co",
            "addresses": [],
            "email": None,
        }, {
            "contact_type": "person",
            "family_name": "Sato",
            "addresses": [],
            "email": {"address": "sato@example.com"},
        }
    ],
}
client_url = f'https://api-meetup.makeleaps.com/api/partner/{partner_mid}/client/'
client_status, client_res = api.post(url=client_url, data=client)
print("Creating client - status:", client_status)

# Create document (with two different tax rates)
document = {
    "document_number": "INV001",
    "document_type": "invoice",
    "document_template": "ja_JP_2",
    "date": "2020-04-17",
    "client": f"{client_res['url']}",
    "client_contact": f"{client_res['contacts'][0]}",
    "lineitems": [
        {"kind": "simple", "description": "Something small", "price": "1000", "tax_rate": "8"},
        {"kind": "simple", "description": "Something big", "price": "98999", "tax_rate": "10"},
    ],
    "mixed_tax_rate_totals": {
        "8": {
            "subtotal": {"amount": "10000", "currency": "JPY"},
            "tax": {"amount": "800", "currency": "JPY"}
        },
        "10": {
            "subtotal": {"amount": "98999", "currency": "JPY"},
            "tax": {"amount": "9899.9", "currency": "JPY"}
        }
    },
    "currency": "JPY",
    "total": "99999",
    "subtotal": "99999",
    "tax": "10699.9",
}
document_url = f'https://api-meetup.makeleaps.com/api/partner/{partner_mid}/document/'
document_status, document_res = api.post(url=document_url, data=document)
print("Creating document - status:", document_status)

# Get other documents from same client
doc_list_status, doc_list_response = api.get(url=document_url)
document_list = []
for doc in doc_list_response:
    if (doc['client'] == client_res['url']):
        document_list.append(doc['url'])
print("Getting other documents - status:", doc_list_status)

# Create sending order
sending_order = {
    "recipient_organization": f"{client_res['url']}",
    "securesend_selected": True,
    "to_emails": ["sato@example.com"],
    "subject": "Invoices for March",
    "message": "Invoices are attached. Thank you for your business.",
    "enable_cc_payments": False,
    "sendbypost_selected": False,
    "stamp_type": "invoice",
}
sending_order_url = f'https://api-meetup.makeleaps.com/api/partner/{partner_mid}/sending/order/'
order_status, order_res = api.post(url=sending_order_url, data=sending_order)
print("Creating Sending Order - status:", order_status)

# Add created document to sending order
position = 0
doc_item = {"position": position, "document": document_res['url']}
doc_item_status, doc_item_res = api.post(url=order_res['items_url'], data=doc_item)
print("Adding item (document) - status:", doc_item_status)

# Add other documents to sending order
for doc in document_list:
    position += 1
    doc_item = {"position": position, "document": f'{doc}'}
    doc_item_status, doc_item_res = api.post(url=order_res['items_url'], data=doc_item)
    print("Adding item (document) - status:", doc_item_status)

# Add custom PDF to sending order
filename = "flyer.pdf"
position += 1
file_item = {"position": position, "filename": f'{filename}'}
file_item_status, file_item_res = api.post(url=order_res['items_url'], data=file_item)
print("Adding item (pdf) - status:", file_item_status)

# Upload custom PDF to database
upload_status, upload_res = api.put(url=file_item_res['upload_url'], filename=filename)
print("Uploading item (pdf) - status:", upload_status)

# Check for completion of processing (max wait time: 1 minute)
for i in range(20):
    ready_status, ready_res = api.get(url=order_res['url'])
    print("Processing - status:", ready_status)
    if ready_res['ready_to_order']:
        # Send sending order
        send_status, send_res = api.post(url=order_res['send_url'], data={})
        print("Successfully sent - status:", send_status)
        break
    else:
        time.sleep(3)
