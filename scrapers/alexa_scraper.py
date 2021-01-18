import os
import csv
import time
import random
import requests
import datetime
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent

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

def read_input_list(file_name):
    return_list = []

    # Try to open the file
    try:
        file = open(file_name, "r", encoding="utf-8")

        lines = file.readlines()

        for line in lines:
            return_list.append(line.strip())

        print("Input file has been read succesfully.")

    except:
        print("Error occured while reading input file.")
        print("Input filename:", file_name)

    return return_list

def set_chrome_options():
    # Set Google Chrome Option
    chromeOptions = webdriver.ChromeOptions()

    #chromeOptions.add_argument("--no-sandbox")
    # chromeOptions.add_argument("--disable-setuid-sandbox")
    # chromeOptions.add_argument("--remote-debugging-port=9222")  # this
    # chromeOptions.add_argument("--disable-dev-shm-using")
    # chromeOptions.add_argument('--disable-dev-shm-usage')
    # chromeOptions.add_argument("--disable-extensions")
    # chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("disable-infobars")
    #chromeOptions.add_argument("--headless")
    #chromeOptions.add_argument("--window-size=1000,1200")

    ua = UserAgent()
    userAgent = ua.random
    chromeOptions.add_argument(f'user-agent={userAgent}')

    return chromeOptions


if __name__ == "__main__":
    # Create output directory
    create_result_directory("alexa")


    input_file_name = "urls.txt"


    # Create result file
    output_file_name = create_result_file(directory_name="alexa", file_name="test", file_format="csv")

    # Read input list
    sites = read_input_list(input_file_name)

    # Open output file
    out_file = open(output_file_name, 'w+', encoding="utf-8", newline='')
    writer = csv.writer(out_file, delimiter=',')
    header = ["Url", "Alexa Rank"]
    writer.writerow(header)

    for site in sites:
        print(site)

        #Set chrome options
        chromeOptions = set_chrome_options()

        # Create Chrome Driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)

        driver.get("https://www.alexa.com/siteinfo")

        try:
            myElem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'input-site')))

        except:
            print(site, "Fail")

            data = [site, "Fail"]
            writer.writerow(data)

        search_area = driver.find_element_by_id("input-site")

        # Enter username and password
        search_area.send_keys(site)

        # Hit Enter Key to login on password area
        search_area.send_keys(Keys.ENTER)


        try:
            myElem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "card_rank")))


            rank = driver.find_element_by_xpath("//*[@class='big data']").text

            if "#" in rank:
                rank = rank.replace("#", "").strip()

                print(site, rank)

                data = [site, rank]
                writer.writerow(data)

            else:
                print(site, "Fail")

                data = [site, "Fail"]
                writer.writerow(data)

        except:
            print(site, "Fail")

            data = [site, "Fail"]
            writer.writerow(data)



        driver.close()


