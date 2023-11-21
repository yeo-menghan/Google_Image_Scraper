from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os

# Your WebDriver path here
PATH = "./chromedriver"
QUERY = "stairs" # Update your search query here
URL = f"https://www.google.com/search?q={QUERY}&tbm=isch"

service = webdriver.ChromeService()
wd = webdriver.Chrome(service=service)

def download_image(image_url, save_folder, idx):
    try:
        formatted_query = QUERY.replace(' ', '_')  # Replaces spaces with underscores
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(os.path.join(save_folder, f'{formatted_query}_{idx}.jpg'), 'wb') as file:
                file.write(response.content)
    except Exception as e:
        print(f"Error - Could not download image. {e}")

def scrape_google_images(url, num_images=5, delay=2):
    wd.get(url)

    image_urls = set()
    skips = 0
    try:
        while len(image_urls) < num_images:
            thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")
            print(f"Thumbnail found: {len(image_urls)}")
            for img in thumbnails[len(image_urls) + skips:min(len(thumbnails), num_images + skips)]:
                try:
                    img.click()
                    time.sleep(delay)
                except Exception as e:
                    skips += 1
                    print(f"Skipping an image due to an error: {e}")
                    continue

                images = wd.find_elements(By.CLASS_NAME, "iPVvYb")
                for image in images:
                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        image_urls.add(image.get_attribute('src'))
                        if len(image_urls) >= num_images:
                            break
                    else:
                        skips += 1

            if len(image_urls) < num_images:
                wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(delay)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        wd.quit()
    return image_urls

# Main Execution
if __name__ == "__main__":
    images_folder = f"downloaded_images/{QUERY}"
    os.makedirs(images_folder, exist_ok=True)
    image_links = scrape_google_images(URL, num_images=10)

    for idx, img_link in enumerate(image_links):
        download_image(img_link, images_folder, idx)
