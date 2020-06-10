const https = require('https');
const MakeLeapsAPI = require('./api.js');

const CLIENT_ID = '<your_client_id>';
const CLIENT_SECRET = '<your_client_secret>';

const api = new MakeLeapsAPI(CLIENT_ID, CLIENT_SECRET);

api.auth_client().then((response) => {
  createClient()
});

const partner_mid = 'XXXXXXXXXXXXXXXXXXX';

// Create client
let client = {
    "client_external_id": "CLIENT-12345",
    "contacts": [
        {
            "contact_type": "organization",
            "name": "Example Co",
            "addresses": [],
            "email": null,
        }, {
            "contact_type": "person",
            "family_name": "Sato",
            "addresses": [],
            "email": {"address": "sato@example.com"},
        }
    ],
}
const client_url = `https://api-meetup.makeleaps.com/api/partner/${partner_mid}/client/`;

function createClient() {
  api.post(client_url, client).then((res) => {
    console.log("Creating client - status: " + res.status)
    createDocument()
  });
}

// Create document (with two different tax rates)
let doc = {
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
const doc_url = `https://api-meetup.makeleaps.com/api/partner/${partner_mid}/document/`;

function createDocument() {
  api.post(doc_url, doc).then((res) => {
    console.log("Creating document - status: " + res.status)
    fetchDocuments()
  });
}

// Get other documents from same client
let document_list = []

function fetchDocuments() {
  api.get(doc_url).then((res) => {
    res.data.forEach((doc) => {
      if (doc['client'] == client_res['url']) {
        document_list.push(doc['url'])
      }
    });
    console.log("Getting other documents - status: " + res.status)
    createOrder()
  });
}

// Create sending order
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
sending_order_url = `https://api-meetup.makeleaps.com/api/partner/${partner_mid}/sending/order/`

function createOrder() {
  api.post(sending_order_url, sending_order).then((res) => {
    console.log("Creating Sending Order - status: " + res.status)
    addDocument()
    addBulk()
    addPDF()
  });
}

// Add created document to sending order
let position = 0;

function addDocument() {
  doc_item = {"position": position, "document": document_res['url']}
  api.post(order_res['items_url'], doc_item).then((res) => {
    console.log("Adding item (document) - status: " + res.status)
  });
}

// Add other documents to sending order
function addBulk() {
  document_list.forEach((doc) => {
    position += 1
    doc_item = {"position": position, "document": f'{doc}'}
    api.post(order_res['items_url'], doc_item).then((res) => {
      console.log("Adding item (document) - status: " + res.status)
    })
  });
}

// Add custom PDF to sending order
function addPDF() {
  filename = "flyer.pdf"
  position += 1
  file_item = {"position": position, "filename": f'{filename}'}
  api.post(order_res['items_url'], file_item).then((res) => {
    console.log("Adding item (pdf) - status: " + res.status)
    uploadPDF()
  });
}

// Upload custom PDF to database
function uploadPDF() {
  api.put(file_item_res['upload_url'], filename).then((res) => {
    console.log("Uploading item (pdf) - status: " + res.status)
    sendOrder()
  });
}

// Check for completion of processing (max wait time: 1 minute)
function sendOrder() {
  for (i = 0; i < 20; i++) {
    api.get(order_res['url']).then((res) => {
      console.log("Processing - status: " + res.status)

      if (res.data['ready_to_order'] == true) {
        // Send sending order
        api.post(order_res['send_url'], {}).then((res) => {
          console.log("Successfully sent - status: " + res.status)
          break
        });

      } else {
        sleep(3)
      }
    })
  }
}
