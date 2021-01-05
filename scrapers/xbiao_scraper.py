import os
import time
import numpy as np
import requests
import threading
from datetime import datetime
from bs4 import BeautifulSoup, Comment

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

def get_bsObj(url):


    # Headers for request, without these the server can reject us
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        "Cookie": "deviceType=desktop_57c2b4c157dca444b0d506e0ab9928a2m",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1"}


    try:
        response = requests.get(url, headers=headers, proxies=None)
        bsObj = BeautifulSoup(response.content, "html.parser")

    except:
        bsObj = BeautifulSoup(" ", "html.parser")

    return bsObj

def comment_scraper(url):
    # Pull page source
    bsObj = get_bsObj(url)

    comment_boxes = bsObj.find_all("table", {"class":"plhin"})

    result_lines = []

    for comment in comment_boxes:
        date_text_raw = comment.find("td", {"class":"plc"}).find("div", {"class":"authi"}).find("em").text

        date = date_text_raw.split(" ")[1]

        try:
            comment_element = comment.find("td", {"class":"plc"}).find("div", {"class":"pct"}).find("td", {"class":"t_f"}).find_all(text=True, recursive=False)
            #comment_element = comment.find("td", {"class": "plc"}).find("div", {"class": "pct"}).find_all(text=True, recursive=False)

            comment_text_final = ""

            for comment_text_element in comment_element:
                if not isinstance(comment_text_element, Comment):
                    comment_text_final += str(comment_text_element).replace("\n", "").replace("\r", "").replace("  ", " ").lstrip() + " "


            comment_text_final = comment_text_final.lstrip().rstrip()

            result_line = f'"{url}";"{comment_text_final}";"{date}"\n'

            result_lines.append(result_line)

        except:
            pass


    # Search for next url
    try:
        next_url = bsObj.find("a", {"class":"nxt"}, href=True)['href']

    except:
        next_url = None


    return next_url, result_lines


def get_post_urls(base_urls):
    "crawl over result pages and return and store post urls on file."
    post_urls = []

    for url in base_urls:
        continue_flag = True

        while continue_flag:
            # Pull page content
            bsObj = get_bsObj(url)
            print(url)

            search_result_divs = bsObj.find_all("div", {"class":"s_url left"})

            for result_div in search_result_divs:
                post_url = result_div.find("a", href=True)['href']
                post_urls.append(post_url)

            # Check next page button
            try:
                next_button = bsObj.find("a", {"class":"ar next right"}, href=True)
                url = "http://www.xbiao.com" + next_button['href']

            except:
                continue_flag = False

            time.sleep(1)


    # Write post urls to file

    post_file = open("post_urls_file.csv", "a+", encoding="utf-8")

    for post in post_urls:
        post_file.writelines(post)
        post_file.flush()

    post_file.close()

    return post_urls

def scrape_post(post_url):
    continue_flag = True

    print("Scraping post:", post_url)

    result_lines = []

    while continue_flag:

        next_url, result_lines_rt = comment_scraper(post_url)

        if next_url is None:
            continue_flag = False
        else:
            post_url = next_url

        result_lines.append(result_lines_rt)

        time.sleep(1)

    return result_lines

def main_scraper(scraper_id, post_urls):

    # Create output file
    out_file_name = create_result_file(directory_name="Result", file_name=f"{scraper_id}", file_format="csv")

    # Initialize output file
    initialize_result_file(out_file_name)

    # Open output file
    out_file = open(out_file_name, "a+", encoding="utf-8")

    for post in post_urls:
        post = post.strip()

        all_result_lines = scrape_post(post)

        # Write results lines to file
        for result_line in all_result_lines:
            out_file.writelines(result_line)
            out_file.flush()

        time.sleep(1)

    out_file.close()


if __name__ == "__main__":

    create_result_directory("Result")

    # Scrape post urls
    #base_urls = ["http://www.xbiao.com/search/index?wd=%E5%8A%B3%E5%8A%9B%E5%A3%AB&cp=963"]
    #post_urls = get_post_urls(base_urls)

    # Read post urls from file
    post_urls_file = open("post_urls_file.csv", "r", encoding="utf-8")

    post_urls = post_urls_file.readlines()

    splits = np.array_split(post_urls[1000:], 20)

    t0 = threading.Thread(target=main_scraper, args=(0, splits[0]))
    t1 = threading.Thread(target=main_scraper, args=(1, splits[1]))
    t2 = threading.Thread(target=main_scraper, args=(2, splits[2]))
    t3 = threading.Thread(target=main_scraper, args=(3, splits[3]))
    t4 = threading.Thread(target=main_scraper, args=(4, splits[4]))
    t5 = threading.Thread(target=main_scraper, args=(5, splits[5]))
    t6 = threading.Thread(target=main_scraper, args=(6, splits[6]))
    t7 = threading.Thread(target=main_scraper, args=(7, splits[7]))
    t8 = threading.Thread(target=main_scraper, args=(8, splits[8]))
    t9 = threading.Thread(target=main_scraper, args=(9, splits[9]))
    t10 = threading.Thread(target=main_scraper, args=(10, splits[10]))
    t11 = threading.Thread(target=main_scraper, args=(11, splits[11]))
    t12 = threading.Thread(target=main_scraper, args=(12, splits[12]))
    t13 = threading.Thread(target=main_scraper, args=(13, splits[13]))
    t14 = threading.Thread(target=main_scraper, args=(14, splits[14]))
    t15 = threading.Thread(target=main_scraper, args=(15, splits[15]))
    t16 = threading.Thread(target=main_scraper, args=(16, splits[16]))
    t17 = threading.Thread(target=main_scraper, args=(17, splits[17]))
    t18 = threading.Thread(target=main_scraper, args=(18, splits[18]))
    t19 = threading.Thread(target=main_scraper, args=(19, splits[19]))





    t0.start()
    time.sleep(5)

    t1.start()
    time.sleep(5)

    t2.start()
    time.sleep(5)

    t3.start()
    time.sleep(5)

    t4.start()
    time.sleep(5)

    t5.start()
    time.sleep(5)

    t6.start()
    time.sleep(5)

    t7.start()
    time.sleep(5)

    t8.start()
    time.sleep(5)

    t9.start()
    time.sleep(5)

    t10.start()
    time.sleep(5)

    t11.start()
    time.sleep(5)

    t12.start()
    time.sleep(5)

    t13.start()
    time.sleep(5)

    t14.start()
    time.sleep(5)

    t15.start()
    time.sleep(5)

    t16.start()
    time.sleep(5)

    t17.start()
    time.sleep(5)

    t18.start()
    time.sleep(5)

    t19.start()
    time.sleep(5)

    t0.join()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    t9.join()
    t10.join()
    t11.join()
    t12.join()
    t13.join()
    t14.join()
    t15.join()
    t16.join()
    t17.join()
    t18.join()
    t19.join()






