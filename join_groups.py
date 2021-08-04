from os import close
from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options 
import argparse

parser = argparse.ArgumentParser(description="Join facebook groups with ids specified in a file")
parser.add_argument('-f','--file',help = "path to file which contains group ids")
parser.add_argument('-o','--outfile',help = "path to file which contains group ids")
args = parser.parse_args()

def login_fb(driver, usr, pwd):
    print("Logging in")
    driver.get("https://www.facebook.com/")

    username_box = driver.find_element_by_id('email')
    username_box.send_keys(usr)

    password_box = driver.find_element_by_id('pass')
    password_box.send_keys(pwd)

    login_box = driver.find_element_by_css_selector('button[name="login')
    login_box.click()

def request_join_group(driver, group_id):
    base_url = "https://m.facebook.com/groups/"

    driver.get(base_url + group_id)
    sleep(1)
    try:
        join_box = driver.find_element_by_css_selector("button[label='Tham gia nhóm']")
        join_box.click()
    except Exception as e:
        print("Can't join group because of exception: ")
        print(e)
    sleep(1)

def request_join_from_file(driver, group_ids_file):
    with open(group_ids_file, "r") as f:
        group_ids = [line[:-1] for line in f.readlines()]
    for group_id in group_ids:
        request_join_group(driver, group_id)

def joined_group(driver, group_id):
    """Check if joined group or not"""

    base_url = "https://m.facebook.com/groups/"
    driver.get(base_url + group_id)
    sleep(1)
    try:
        _ = driver.find_element_by_css_selector("a[aria-label='Đã tham gia']")
        return True
    except:
        return False

def check_joined_from_file(driver, group_ids_file, joined_groups_file):
    print("Checking if joined groups...")
    with open(group_ids_file, "r") as f:
        group_ids = [line.strip() for line in f.readlines()]
    unjoined_groups = []
    joined_groups = set()
    for group_id in group_ids:
        if joined_group(driver, group_id):
            joined_groups.add(group_id)
            print(f"Joined {group_id}")
        else:
            print(f"Didn't join {group_id}")
            unjoined_groups.append(group_id)
    
    with open(group_ids_file, "w") as f:
        for group_id in unjoined_groups:
            f.write(group_id + "\n")
    try: 
        with open(joined_groups_file, "r") as f:
            for line in f.readlines():
                joined_groups.add(line)
    except:
        "File didn't exists. Creating new file"
    with open(joined_groups_file, "w") as f:
        for group_id in joined_groups:
            f.write(str(group_id) + "\n")

if __name__ == "__main__":
    DRIVER_PATH = r"drivers\geckodriver"
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path = DRIVER_PATH, options = options)

    usr = "522160734"
    pwd = "matkhau2213"
    login_fb(driver, usr, pwd)
    request_join_from_file(driver, args.file)
    check_joined_from_file(driver, args.file, args.outfile)
    driver.close()
