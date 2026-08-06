import time
import pandas as pd
import requests

# 1. Configuration
API_KEY = "a824a81e-369b-44f4-a6b3-0c0c48af9920"
COLLECTOR_ID = "c_msgdmhnw9ih549m7j"  # Your active collector ID from the terminal output

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Target URLs to pass into your collector
payload = [
    {"url": "https://www.amazon.in/s?k=asus+rog+laptops"},
    {"url": "https://www.flipkart.com/search?q=asus+tuf+laptop"},
]


def run_pipeline():
  print("Triggering Scraper Studio collector...")

  # Step 1: Trigger the collection job
  trigger_url = f"https://api.brightdata.com/dca/trigger?collector={COLLECTOR_ID}&queue_next=1"
  response = requests.post(trigger_url, headers=headers, json=payload)

  if response.status_code != 200:
    print(f"Trigger failed ({response.status_code}): {response.text}")
    return

  res_json = response.json()
  snapshot_id = res_json.get("collection_id")

  if not snapshot_id:
    print(f"No collection_id returned: {res_json}")
    return

  print(f"Job triggered successfully. Snapshot ID: {snapshot_id}")
  print("Waiting for extraction to complete...")

  # Step 2: Poll for results
  dataset_url = f"https://api.brightdata.com/dca/dataset?id={snapshot_id}"

  for attempt in range(1, 15):
    time.sleep(10)
    print(f"Polling attempt {attempt}/14...")

    data_response = requests.get(dataset_url, headers=headers)

    if data_response.status_code == 200:
      try:
        raw_data = data_response.json()
        if isinstance(raw_data, list) and len(raw_data) > 0:
          print("Data fetched successfully! Processing with Pandas...")
          process_data(raw_data)
          return
      except Exception:
        # Still building/returning status text instead of final json array
        continue

  print("Timed out waiting for the collector to finish.")


def process_data(raw_data):
  cleaned_rows = []
  for item in raw_data:
    title = item.get("title", "ASUS Laptop Model")
    price_raw = item.get("price", "0")

    if isinstance(price_raw, str):
      price_clean = (
          price_raw.replace("₹", "")
          .replace(",", "")
          .replace("INR", "")
          .strip()
      )
    else:
      price_clean = str(price_raw)

    try:
      price_val = float(price_clean)
    except ValueError:
      price_val = 0.0

    cleaned_rows.append({
        "Model": title,
        "Price_INR": price_val,
        "Platform": item.get("domain", "Retailer"),
    })

  df = pd.DataFrame(cleaned_rows)
  df = df[df["Price_INR"] > 0]
  df.to_csv("prices.csv", index=False)
  print("Success! Cleaned data saved to prices.csv")


if __name__ == "__main__":
  run_pipeline()
