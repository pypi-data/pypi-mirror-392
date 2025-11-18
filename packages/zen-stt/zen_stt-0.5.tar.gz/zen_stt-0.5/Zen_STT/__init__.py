# Zen_STT/__init__.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd
import time

def _create_driver(headless=True, fake_video="fake.y4m"):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--auto-select-desktop-capture-source=Screen 1")
    chrome_options.add_argument("--allow-file-access-from-files")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument(f"--use-file-for-fake-video-capture={fake_video}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def listen(driver=None, website="https://allorizenproject1.netlify.app/", rec_file=None, timeout=20):
    """
    Starts listening on the given website and writes recognized text to rec_file.
    - driver: a selenium webdriver instance. If None, a new driver will be created.
    - rec_file: path to write recognized text (default: current working dir / input.txt)
    - timeout: wait timeout for selenium waits
    """
    close_driver_when_done = False
    if driver is None:
        driver = _create_driver()
        close_driver_when_done = True

    if rec_file is None:
        rec_file = getcwd() + r"\input.txt"

    try:
        driver.get(website)

        start_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, 'startButton'))
        )
        start_button.click()
        print("Listening...")

        output_text = ""
        is_second_click = False

        while True:
            # Re-locate button so .text updates
            start_button = driver.find_element(By.ID, 'startButton')

            output_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'output'))
            )
            current_text = output_element.text.strip()

            # BUTTON RESET CHECK
            if "Start Listening" in start_button.text and is_second_click:
                if output_text:
                    is_second_click = False

            # LISTENING ACTIVE
            elif "Listening" in start_button.text:
                is_second_click = True

                if current_text != output_text:
                    output_text = current_text

                    with open(rec_file, "w", encoding="utf-8") as file:
                        file.write(output_text.lower())

                    print("USER : " + output_text)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print("Error in listen():", e)
    finally:
        if close_driver_when_done:
            try:
                driver.quit()
            except Exception:
                pass
