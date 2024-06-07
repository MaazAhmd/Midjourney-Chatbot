import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')


def read_prompts(file_path):
    with open(file_path, 'r') as file:
        prompts = file.readlines()
    return [parse_prompt(prompt.strip()) for prompt in prompts if prompt.strip()]

def parse_prompt(prompt):
    if "--ar" in prompt:
        main_prompt, aspect_ratio = prompt.split("--ar")
        main_prompt = main_prompt.strip()
        aspect_ratio = aspect_ratio.strip()
    else:
        main_prompt = prompt.strip()
        aspect_ratio = "4:3"  # Default aspect ratio if not specified
    return main_prompt, aspect_ratio

def send_prompt_to_api(prompt, aspect_ratio):
    print(f"Sending prompt to API: {prompt} with aspect ratio {aspect_ratio}")
    url = "https://api.midjourneyapi.xyz/mj/v2/imagine"
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "process_mode": "relax"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send prompt: {e}")
        return None
