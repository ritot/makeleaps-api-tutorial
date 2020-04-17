from api import MakeLeapsAPI
import time

"""
Main application that sends documents via MakeLeapsAPI
"""

CLIENT_ID = '<your_client_id>'
CLIENT_SECRET = '<your_client_secret>'

api = MakeLeapsAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
token = api._auth_client()

partner_mid = 'XXXXXXXXXXXXXXXXXXX'

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
client_status, client_res = api.post(token=token, url=client_url, data=client)
print("Creating client - status:", client_status)

# Create document (with two different tax rates)
document = {
    "document_number": "INV000",
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
    # The following four lines seem redundant but I get a error when it's left out
    "currency": "JPY",
    "total": "99999",
    "subtotal": "99999",
    "tax": "10699.9",
}
document_url = f'https://api-meetup.makeleaps.com/api/partner/{partner_mid}/document/'
document_status, document_res = api.post(token=token, url=document_url, data=document)
print("Creating document - status:", document_status)

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
order_status, order_res = api.post(token=token, url=sending_order_url, data=sending_order)
print("Creating Sending Order - status:", order_status, order_res)

# Add document to sending order
item_1 = {"position": 0, "document": document_res['url']}
item_1_status, item_1_res = api.post(token=token, url=order_res['items_url'], data=item_1)
print("Adding item (document) - status:", item_1_status)

# Add custom PDF to sending order
item_2 = {"position": 1, "filename": "flyer.pdf"}
item_2_status, item_2_res = api.post(token=token, url=order_res['items_url'], data=item_2)
print("Adding item (pdf) - status:", item_2_status)

# TODO: Figure out how to interact with API to upload PDF
# Upload PDF
upload_status, upload_res = api.put(token=token, url=order_res['pdf_content_url'])
print("Uploading item (pdf) - status:", upload_status)

# Check for completion of processing
# Max wait time is 1 minute [What should it be?]
for i in range(30):
    ready_status, ready_res = api.get(token, url=order_res['url'])
    print("Processing - status:", ready_status)
    if ready_res['ready_to_order']:
        # Send sending order
        send_status, send_res = api.post(token=token, url=order_res['send_url'], data={})
        print("Successfully sent - status:", send_status)
        break
    else:
        time.sleep(2)
