import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')



def multi_fetch_results(task_ids, task, retry_delay=40):
    if(task=="upscale"):
        retry_limit=len(task_ids)*2
    else:
        retry_limit=len(task_ids)*4
    url = "https://api.goapi.xyz/mj/v2/multi_fetch"
    data = {"task_ids": task_ids}
    message = "Upscaling images" if task == "upscale" else "Getting images from prompt"


    for attempt in range(retry_limit):
        with requests.Session() as session:
            try:
                response = session.post(url, json=data)
                
                result = response.json()
                all_finished = True
                for task_id, task_result in result['data'].items():
                    if task_result is None or task_result['status'] != "finished":
                        all_finished = False
                        break
                if all_finished:
                    return result
                else:
                    print(f"{message} Wait for 40 sec...  Attempt {attempt + 1}/{retry_limit}.")
                    time.sleep(retry_delay)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                print("Wait and ensure your internet connection.")
                time.sleep(retry_delay)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                print(f"RequestException on attempt {attempt + 1}: {e}")
    
    print(f"Exceeded retry limit for task_ids: {task_ids}")
    return None



def upscale_image(origin_task_id, index):
    url = "https://api.midjourneyapi.xyz/mj/v2/upscale"
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "origin_task_id": origin_task_id,
        "index": str(index)
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to upscale image for task_id: {origin_task_id} - {e}")
        return None
