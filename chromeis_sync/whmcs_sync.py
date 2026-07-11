import frappe
import requests

def fetch_whmcs_invoices():
    # WHMCS API Credentials
    url = "https://my.chromeis.com/includes/api.php"
    params = {
        "username": "mwnnh6qYqTSLWfJbSrTZu484zJQzaYPV",
        "password": "XlV4kzFcWPEcyvoTZz5ZI34NLGacudWm",
        "action": "GetInvoices",
        "limitnum": 5,
        "responsetype": "json"
    }

    try:
        response = requests.post(url, data=params)
        data = response.json()
        
        if data.get("result") == "success":
            invoices = data["invoices"]["invoice"]
            for inv in invoices:
                print(f"WHMCS Invoice ID: {inv['id']} | Total: {inv['total']}")
            return invoices
        else:
            print(f"API Error: {data.get('message')}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []
