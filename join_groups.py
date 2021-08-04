from os import close
from time import sleep
import pandas as pd
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options 
import argparse

parser = argparse.ArgumentParser(description="Join facebook groups with ids specified in a file")
parser.add_argument('-f','--file',help = "path to text file which contains group ids that we need to join")
parser.add_argument('-o','--outfile',help = "path to json file which contains joined group ids")
parser.add_argument('-a','--accountfile',help = "path to csv file which contains facebook accounts")
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
    print("Logged in")

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

def request_join_from_file(driver, group_ids_file, already_joined_groups = []):
    with open(group_ids_file, "r") as f:
        group_ids = [line[:-1] for line in f.readlines()]
    for group_id in group_ids:
        if group_id in already_joined_groups:
            continue
        request_join_group(driver, group_id)

def check_joined_group(driver, group_id):
    """Check if joined group or not"""

    base_url = "https://m.facebook.com/groups/"
    driver.get(base_url + group_id)
    sleep(1)
    try:
        _ = driver.find_element_by_css_selector("a[aria-label='Đã tham gia']")
        return True
    except:
        return False

def check_joined_from_file(driver, group_ids_file):
    print("Checking if joined groups...")
    with open(group_ids_file, "r") as f:
        group_ids = [line.strip() for line in f.readlines()]
    unjoined_groups = []
    joined_groups = []
    for group_id in group_ids:
        if check_joined_group(driver, group_id):
            joined_groups.append(group_id)
            print(f"Joined {group_id}")
        else:
            print(f"Didn't join {group_id}")
            unjoined_groups.append(group_id)
    return unjoined_groups, joined_groups
def write_unjoined_groups(unjoined_groups, group_ids_file):
    with open(group_ids_file, 'w') as f:
        for group_id in unjoined_groups:
            f.write(str(group_id) + "\n")
def write_joined_groups(joined_groups, joined_groups_file, usr, pwd):
    groups_info = {}
    account = {usr: pwd}
    try:
        with open(joined_groups_file, 'r') as f:
            groups_info =json.load(f)
    except:
        "File doesn't exist. Creating new file"
    for group_id in joined_groups:
        print(group_id)
        print(groups_info.keys)
        if not group_id in groups_info.keys():
            groups_info[group_id] = [account]
        else:
            if not account in groups_info[group_id]:
                groups_info[group_id].append(account)
    print(type(groups_info))
    with open(joined_groups_file, 'w') as f:
        json.dump(groups_info, f)
def get_already_joined_groups(joined_groups_file, usr, pwd):
    account = {usr:pwd}
    joined_groups_info = {}
    joined_groups = []
    try:
        with open(joined_groups_file, 'r') as f:
            joined_groups_info = json.load(f)
    except:
        return []

    for group_id in joined_groups_info:
        if account in joined_groups_info[group_id]:
            joined_groups.append(group_id)   
    return joined_groups
def join_multiple_accounts(group_ids_file, joined_groups_file, fb_accounts_file):
    options = Options()
    options.headless = True
    DRIVER_PATH = r"drivers/geckodriver"
    accounts_df = pd.read_csv(fb_accounts_file)
    for _, row in accounts_df.iterrows():
        driver = webdriver.Firefox(executable_path = DRIVER_PATH, options = options)
        login_fb(driver, row['user'], row['pw'])

        joined_groups = get_already_joined_groups(joined_groups_file, row['user'], row['pw'])
        request_join_from_file(driver, group_ids_file, joined_groups)
        unjoined, joined = check_joined_from_file(driver, group_ids_file)

        # write_unjoined_groups(unjoined, group_ids_file)
        write_joined_groups(joined, joined_groups_file, row['user'], row['pw'])
        driver.close()
if __name__ == "__main__":
    
    join_multiple_accounts(fb_accounts_file= args.accountfile,joined_groups_file= args.outfile, group_ids_file=args.file)
    # print("do nothing")