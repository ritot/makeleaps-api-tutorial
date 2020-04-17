from api import MakeLeapsAPI
import time

"""
Main application that sends documents via MakeLeapsAPI
"""

CLIENT_ID = '<your client id>'
CLIENT_SECRET = '<your client secret>'

api = MakeLeapsAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

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
client_url = f'https://api.makeleaps.com/api/partner/{partner_mid}/client/'
status, response = api.post(token=api.token, url=client_url, data=client)

# Create document
document = {
    "document_number": "INV001",
    "document_type": "invoice",
    "document_template": "ja_JP_2",
    "date": "2018-02-05",
    "client": f"{client_res['url']}",
    "client_contact": f"{client_res['contacts'][0]}",
    "lineitems": [
        {"kind": "simple", "description": "Something small", "price": "1000"},
        {"kind": "simple", "description": "Something big", "price": "98999"},
    ],
    "currency": "JPY",
    "total": "99999",
    "subtotal": "99999",
    "tax": "0",
}
document_url = f'https://api.makeleaps.com/api/partner/{partner_mid}/document/'
status, response = api.post(url=document_url, data=document)

# Create sending order
sending_order = {
    "recipient_organization": f"{client_res['url']}",
    "securesend_selected": True,
    "to_emails": ["123@example.com"],
    "subject": "Invoices for March",
    "message": "Invoices are attached. Thank you for your business.",
    "enable_cc_payments": False,
    "sendbypost_selected": False,
    "stamp_type": "invoice",
}
sending_order_url = f'https://meetup.makeleaps.com/api/partner/{partner_mid}/sending/order/'
order_status, order_res = api.post(url=sending_order_url, data=sending_order)
print(order_status, order_res)

# Add item to order
item = {"position": 0, "document": document_res['url']}
item_status, item_res = api.post(url=order_res['items_url'], data=item)
print(item_status, item_res)

# Check for completion of processing
# Max wait time is 1 minute [What should it be?]
for i in range(60):
    ready_status, ready_res = api.get(url=order_res['url'])
    print("GET STATUS")
    print(ready_status, ready_res)
    if ready_res['ready_to_order']:
        # Send sending order
        send_status, send_res = api.post(url=order_res['send_url'], data={})
        print(send_status, send_res)
        break
    else:
        time.sleep(1)
