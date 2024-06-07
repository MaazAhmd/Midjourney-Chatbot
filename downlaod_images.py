from PIL import Image
import requests
import io
import os

def download_image(image_url):
    try:
        response = requests.get(image_url)
        return Image.open(io.BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image from: {image_url} - {e}")
        return None


def save_images(images, output_dir):
    print(f"Saving images to directory: {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"image_{i + 1}.png")
        image.save(image_path)
