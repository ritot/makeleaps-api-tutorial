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
const client = {
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
    createDocument(res.data.response)
  });
}

// Create document (with two different tax rates)
function createDocument(client_res) {
  const doc = {
      "document_number": "INV223",
      "document_type": "invoice",
      "document_template": "ja_JP_2",
      "date": "2020-04-17",
      "client": `${client_res['url']}`,
      "client_contact": `${client_res['contacts'][0]}`,
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

  api.post(doc_url, doc).then((res) => {
    console.log("Creating document - status: " + res.status)
    const doc_res = res.data.response
    fetchDocuments(client_res, doc_url, doc_res)
  });
}

// Get other documents from same client
const document_list = []

function fetchDocuments(client_res, doc_url, doc_res) {
  api.get(doc_url).then((res) => {
    res.data.response.forEach((doc) => {
      if (doc['client'] == client_res['url']) {
        document_list.push(doc['url'])
      }
    });
    console.log("Getting other documents - status: " + res.status)
    createOrder(client_res, doc_res)
  });
}

// Create sending order
function createOrder(client_res, doc_res) {
  const sending_order = {
      "recipient_organization": `${client_res['url']}`,
      "securesend_selected": true,
      "to_emails": ["sato@example.com"],
      "subject": "Invoices for March",
      "message": "Invoices are attached. Thank you for your business.",
      "enable_cc_payments": false,
      "sendbypost_selected": false,
      "stamp_type": "invoice",
  }
  const sending_order_url = `https://api-meetup.makeleaps.com/api/partner/${partner_mid}/sending/order/`

  api.post(sending_order_url, sending_order).then((res) => {
    console.log("Creating Sending Order - status: " + res.status)
    addDocument(res.data.response, doc_res)
    addBulk(res.data.response)
    addPDF(res.data.response)
  });
}

// Add created document to sending order
let position = 0;

function addDocument(order_res, document_res) {
  const doc_item = {"position": position, "document": document_res['url']}
  api.post(order_res['items_url'], doc_item).then((res) => {
    console.log("Adding item (document) - status: " + res.status)
  });
}

// Add other documents to sending order
function addBulk(order_res) {
  document_list.forEach((doc) => {
    position += 1
    const doc_item = {"position": position, "document": `${doc}`}
    api.post(order_res['items_url'], doc_item).then((res) => {
      console.log("Adding item (document) - status: " + res.status)
    })
  });
}

// Add custom PDF to sending order
function addPDF(order_res) {
  const filename = "flyer.pdf"
  position += 1
  const file_item = {"position": position, "filename": `${filename}`}
  api.post(order_res['items_url'], file_item).then((res) => {
    console.log("Adding item (pdf) - status: " + res.status)
    uploadPDF(res.data.response, filename)
  });
}

// Upload custom PDF to database
function uploadPDF(file_item_res, filename) {
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
