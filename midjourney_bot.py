import os
import time
from  read_prompts import read_prompts,send_prompt_to_api
from  fetch_and_upscale import multi_fetch_results,upscale_image
from  downlaod_images import download_image,save_images
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def process_prompts(prompts):
    results = []
    for index, (prompt, aspect_ratio) in enumerate(prompts):
        result = send_prompt_to_api(prompt, aspect_ratio)
        if result:
            results.append((index, result))  # Store result with index
        time.sleep(1)  # To avoid hitting rate limits
    return results


def process_results(results):
    upscaled_images = []
    task_ids_with_indices = [(index, result['task_id']) for index, result in results]
    
    fetch_response = multi_fetch_results([task_id for _, task_id in task_ids_with_indices], "fetch images")
    
    if fetch_response and 'data' in fetch_response:
        results_data = fetch_response['data']
        upscale_task_ids = []
        index_mapping = {}
        
        for index, (result_index, task_id) in enumerate(task_ids_with_indices):
            fetch_result = results_data.get(task_id)
            if fetch_result and fetch_result['status'] == "finished":
                image_urls = fetch_result['task_result']['image_urls']
                for i, _ in enumerate(image_urls):
                    upscaled_task = upscale_image(task_id, i + 1)
                    if upscaled_task:
                        upscale_task_ids.append(upscaled_task['task_id'])
                        index_mapping[upscaled_task['task_id']] = result_index
        
        # Fetch all upscaled images at once using multi-fetch
        if upscale_task_ids:
            upscaled_fetch_response = multi_fetch_results(upscale_task_ids, "upscale")
            if upscaled_fetch_response and 'data' in upscaled_fetch_response:
                upscaled_results_data = upscaled_fetch_response['data']
                for upscaled_task_id, upscaled_result in upscaled_results_data.items():
                    if upscaled_result and upscaled_result['status'] == "finished":
                        upscaled_image_url = upscaled_result['task_result']['image_url']
                        upscaled_image = download_image(upscaled_image_url)
                        if upscaled_image:
                            result_index = index_mapping[upscaled_task_id]
                            upscaled_images.append((result_index, upscaled_image))
    
    # Sort images by their original prompt indices
    upscaled_images.sort(key=lambda x: x[0])
    return [image for _, image in upscaled_images]



def main():
    print("Reading prompts from file")
    prompts = read_prompts('input_prompts.txt')
    results = process_prompts(prompts)
    upscaled_images = process_results(results)
    save_images(upscaled_images, 'output_images')

if __name__ == "__main__":
    main()
