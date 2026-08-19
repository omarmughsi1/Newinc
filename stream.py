import requests
import json
import time
import os

API_KEY = os.environ["CH_API_KEY"]
TARGET_SIC_CODES = {"62012", "62020"}  # <-- replace with your SIC codes

STREAM_URL = "https://stream.companieshouse.gov.uk/companies"

def notify(company):
    print(f"MATCH: {company.get('company_name')} ({company.get('company_number')})")
    # TODO: replace with Slack webhook / email call

def handle_event(event):
    data = event.get("data", {})
    resource_kind = event.get("resource_kind", "")

    is_incorporation = (
        resource_kind == "company-profile"
        and data.get("date_of_creation")
        and data.get("company_status") == "active"
    )

    sic_codes = set(data.get("sic_codes", []))

    if is_incorporation and sic_codes & TARGET_SIC_CODES:
        notify(data)

def connect_and_listen():
    with requests.get(
        STREAM_URL,
        auth=(API_KEY, ""),
        stream=True,
        timeout=60
    ) as response:
        print("Connected, status:", response.status_code)
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode("utf-8"))
                    handle_event(event)
                except json.JSONDecodeError:
                    continue

def run_forever():
    while True:
        try:
            connect_and_listen()
        except Exception as e:
            print("Stream error:", e)
        print("Reconnecting in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    run_forever()
