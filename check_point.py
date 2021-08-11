from time import sleep
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options 
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Join facebook groups with ids specified in a file")
parser.add_argument('-a','--accountfile',help = "path to csv file which contains facebook accounts")
args = parser.parse_args()

def login_fb(driver, usr, pwd):
    """
    Logging in a facebook account given an user name and password
    Parameters:
        - driver (selenium web driver object)
        - usr (string): user name for fb account
        - pwd (string): password 
    """
    print("_"*60)
    print("Logging in")
    driver.get("https://www.facebook.com/")

    username_box = driver.find_element_by_id('email')
    username_box.send_keys(usr)

    password_box = driver.find_element_by_id('pass')
    password_box.send_keys(pwd)

    login_box = driver.find_element_by_css_selector('button[name="login')
    login_box.click()
    sleep(1)
    if driver.current_url == r"https://www.facebook.com/":
        print(f"Logged in successfully with {usr}")
        return True
    else: 
        print(f"Log in failed! Please check user name {usr}")
        return False
def check_if_blocked(usr, pwd):
    options = Options()
    options.headless = True
    DRIVER_PATH = r"drivers/geckodriver"
    driver = webdriver.Firefox(executable_path = DRIVER_PATH, options = options)
    logged_in = login_fb(driver, usr, pwd)
    if not logged_in:
        driver.close()
        return True
    driver.get("https://m.facebook.com/groups/432100910224405")
    sleep(1)
    body_html = driver.find_element_by_tag_name('body').text
    if body_html.find("Có vẻ như bạn đang dùng nhầm tính năng này do sử dụng quá nhanh") >= 0:
        driver.close()
        return True
    driver.close()
    return False

def check_block_multiple_accounts(fb_accounts_file):
    accounts_df = pd.read_csv(fb_accounts_file)
    is_checkpointed = []
    check_time = []
    for _, row in accounts_df.iterrows():
        usr, pwd = str(row['user']).strip(), str(row['pw']).strip()
        is_checkpointed.append(check_if_blocked(usr, pwd))
        check_time.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    accounts_df['is_checkpointed'] = is_checkpointed
    accounts_df['check_time'] = check_time
    accounts_df.to_csv(fb_accounts_file, index = False)
if __name__ == "__main__":
    check_block_multiple_accounts(args.accountfile)