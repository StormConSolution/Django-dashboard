import os
import sys
import time
import requests
import datetime
import threading
from requests_html import HTMLSession
import os
import time
import numpy as np
import requests
import threading
from datetime import datetime
from bs4 import BeautifulSoup, Comment
import os
import time
import random
import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import numpy as np
import simpleaudio as sa

def create_result_directory(directory_name):
    """
    Creates a directory named directory_name. If it is already exist it passes.
    :return:
    """
    try:
        os.mkdir(directory_name)
        print(f"{directory_name} directory has been created succesfully.")
    except FileExistsError:
        print(f"{directory_name} directory already exist.")
        pass

def create_result_file(directory_name="", file_name="", file_format="xlsx"):
    if file_name == "":
        file_name = f"{directory_name}/result_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.{file_format}"

        f = open(file_name, "w+", encoding="utf-8")
        f.close()

        print("Result file has been created.")
        print("Results will be written to:")
        print("\t{}".format(file_name))

        return file_name

    else:
        file_name = f"{directory_name}/result_{file_name}.{file_format}"

        f = open(file_name, "w+", encoding="utf-8")
        f.close()

        print("Result file has been created.")
        print("Results will be written to:")
        print("\t{}".format(file_name))

        return file_name

def initialize_result_file(file_name):
    f = open(file_name, 'w+', encoding='utf-8')

    # Create header line
    header_line = '"Url";"Comment";"Date"'

    header_line = header_line + "\n"

    f.writelines(header_line)
    f.close()

    print("Result file has been initialized.")
    print("------------------------------------")



def set_chrome_options():
    # Set Google Chrome Option
    chromeOptions = webdriver.ChromeOptions()

    chromeOptions.add_argument("--no-sandbox")
    # chromeOptions.add_argument("--disable-setuid-sandbox")
    # chromeOptions.add_argument("--remote-debugging-port=9222")  # this
    # chromeOptions.add_argument("--disable-dev-shm-using")
    # chromeOptions.add_argument('--disable-dev-shm-usage')
    # chromeOptions.add_argument("--disable-extensions")
    # chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("disable-infobars")
    #chromeOptions.add_argument("--headless")

    return chromeOptions

def extract_video_url(page_source):
    pass

def get_all_video_urls(driver, base_url, crawl_delay):
    # Go to base url page

    driver.get(base_url)

    video_urls = []

    # Wait till the page is loaded
    delay = 60  # seconds
    success = True

    while True:
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pack-box_1Myuf')))


        # Print all video urls

        video_divs = driver.find_elements_by_class_name("pack-box_1Myuf")

        for video in video_divs:
            video_link = video.find_element_by_tag_name("a").get_attribute('href')
            print(video_link)
            video_urls.append(video_link)

        time.sleep(crawl_delay)
        next_button = driver.find_element_by_xpath("//*[contains(text(), '下一页')]").click()

        if len(video_divs) < 1:
            success = False



if __name__ == "__main__":

    create_result_directory("Result")

    crawl_delay = 1 #Seconds

    # Create output file
    out_file_name = create_result_file(directory_name="Result", file_name="test", file_format="csv")

    # Initialize output file
    initialize_result_file(out_file_name)

    # Open output file
    out_file = open(out_file_name, "a+", encoding="utf-8")

    base_url = "https://so.youku.com/search_video/q_rolex?searchfrom=3"
    base_url_2 = "https://so.youku.com/search_video/q_%25E5%258A%25B3%25E5%258A?searchfrom=3"

    # Initialize chrome setting
    # Set chrome options
    chromeOptions = set_chrome_options()

    # Create Chrome Driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)

    #video_urls = get_all_video_urls(driver, base_url_2, crawl_delay)

    # Read post urls from file
    video_urls_file = open("video_urls_rolex.txt", "r", encoding="utf-8")

    video_urls = video_urls_file.readlines()

    for video_url in video_urls:

        video_url = video_url.strip()



        try_counter = 0
        success = False

        while not success:
            if try_counter < 3:

                try:
                    driver.get(video_url)
                    myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'desc')))
                    success = True

                except:
                    pass

            if try_counter >= 3:
                    try:
                        driver.close()
                        time.sleep(2)
                        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)

                        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'desc')))
                        success = True

                    except:
                        try:
                            driver.get(video_url)
                            myElem = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'desc')))
                            success = True
                        except:
                            try:
                                driver.get(video_url)
                                myElem = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'desc')))
                                success = True
                            except:
                                print("fail:", video_url)
                                continue

            try_counter += 1


        date = driver.find_element_by_class_name("desc").text

        date = date.replace("上传于 ", "")

        # Get comments
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(2)

        all_comments = driver.find_elements_by_class_name("comment-list-content-text")

        if len(all_comments) > 0:
            for comment in all_comments:

                result_line = f'"{video_url}";"{comment.text};"{date}"\n'
                out_file.writelines(result_line)

                out_file.flush()

                print(result_line)


        else:
            result_line = f'"{video_url}";"N/A";"{date}"\n'
            out_file.writelines(result_line)

            out_file.flush()

            print(result_line)

        time.sleep(random.randint(5, 10))

    driver.close()
    out_file.close()

