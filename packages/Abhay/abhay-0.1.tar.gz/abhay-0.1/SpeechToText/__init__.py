# pip install selenium webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options,
)

website = f"{getcwd()}\\index.html"
driver.get(website)

rec_file = f"{getcwd()}\\input.txt"


def listen():
    try:
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        start_button.click()
        print("Listening...")

        last_text = ""

        while True:
            output_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "output"))
            )

            current_text = output_element.text.strip()

            # When JS sets back to "Start Listening"
            if "Start Listening" in start_button.text:
                if current_text and current_text != last_text:
                    last_text = current_text

                    with open(rec_file, "w", encoding="utf-8") as file:
                        file.write(current_text.lower())

                    print("USER:", current_text)

    except KeyboardInterrupt:
        print("Stopped manually")

    except Exception as e:
        print("ERROR:", e)


listen()

    
