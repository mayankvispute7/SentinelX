# load_test.py
import asyncio
import httpx
import time

URL = "http://localhost:8000/predict"
HEADERS = {"X-API-KEY": "prod-super-secret-key-999"}
PAYLOAD = {
    "Time": 0, "Amount": 150.0, "V1": 0.0, "V2": 0.0, "V3": 0.0, "V4": 0.0, 
    "V5": 0.0, "V6": 0.0, "V7": 0.0, "V8": 0.0, "V9": 0.0, "V10": 0.0, 
    "V11": 0.0, "V12": 0.0, "V13": 0.0, "V14": 0.0, "V15": 0.0, "V16": 0.0, 
    "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0, "V21": 0.0, "V22": 0.0, 
    "V23": 0.0, "V24": 0.0, "V25": 0.0, "V26": 0.0, "V27": 0.0, "V28": 0.0
}

async def send_request(client, req_id):
    try:
        response = await client.post(URL, json=PAYLOAD, headers=HEADERS)
        return response.status_code
    except Exception as e:
        return str(e)

async def run_load_test():
    async with httpx.AsyncClient() as client:
        print("🚀 Starting Load Test: 500 Concurrent Requests...")
        start_time = time.time()
        
        tasks = [send_request(client, i) for i in range(500)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        successes = results.count(200)
        rate_limits = results.count(429)
        total_time = end_time - start_time
        avg_latency = (total_time / 500) * 1000
        
        print(f"✅ Success (200 OK): {successes}/500")
        print(f"🛑 Blocked by Rate Limit (429): {rate_limits}/500")
        print(f"⏱️ Total Execution Time: {total_time:.2f} seconds")
        print(f"⚡ Average Latency: {avg_latency:.2f} ms/request")

if __name__ == "__main__":
    asyncio.run(run_load_test())