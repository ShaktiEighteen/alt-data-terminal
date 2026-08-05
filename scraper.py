import time
import requests
import pandas as pd

# 1. Setup Credentials
API_TOKEN = "a824a81e-369b-44f4-a6b3-0c0c48af9920"  # Paste your API token here
COLLECTOR_ID = "c_msgdmhnw9ih549m7j"
TARGET_URL = "https://www.amazon.in/s?k=smartwatches"

def run_pipeline():
    print("Initiating direct API scraper pipeline...")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 2. Trigger the collection job
    trigger_url = f"https://api.brightdata.com/dca/trigger?collector={COLLECTOR_ID}"
    payload = [{"url": TARGET_URL}]
    
    print("Sending request to Scraper Studio...")
    response = requests.post(trigger_url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Trigger failed: {response.text}")
        return
        
    collection_id = response.json().get("collection_id")
    print(f"Job triggered. Collection ID: {collection_id}")
    
    # 3. Wait for the data to be ready
    dataset_url = f"https://api.brightdata.com/dca/dataset?id={collection_id}"
    print("Waiting for extraction (takes ~30-60 seconds)...")
    
    while True:
        data_response = requests.get(dataset_url, headers=headers)
        
        # 200 means success, 202 means it is still processing
        if data_response.status_code == 200:
            data = data_response.json()
            print(f"Success! {len(data)} records captured.")
            
            df = pd.DataFrame(data)
            df.to_csv("prices.csv", index=False)
            print("Pipeline complete. Data secured in prices.csv.")
            break
        elif data_response.status_code == 202:
            print("Still scraping... checking again in 10 seconds.")
            time.sleep(10)
        else:
            print(f"Error retrieving dataset: {data_response.text}")
            break

if __name__ == "__main__":
    run_pipeline()