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
parser.add_argument('-a','--accountfile',help = "path to csv file which contains facebook accounts")
parser.add_argument('-m','--mode', help = "choose working mode: 0 = join, 1 = check join, 2 = join then check join ")
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

def request_join_group(driver, group_id):
    """
    Join a facebook group. 
    ALERT!: This function must be called after calling login_fb()
    Parameters:
        - driver (selenium webdriver object)
        - group_id (string, int): the uid of a facebook group
    """

    # if found the "Join group" button -> click it
    # else: 
    #   check if joined group or if the group exists then print out the log
    base_url = "https://m.facebook.com/groups/"
    driver.get(base_url + str(group_id))
    sleep(1)
    
    try:
        join_box = driver.find_element_by_css_selector("button[label='Tham gia nhóm']")
        join_box.click()
        print(f"Requested to join group {group_id}")
    except Exception as e:
        try:
            cancel_request_box = driver.find_element_by_css_selector('button[label = "Hủy yêu cầu"]')
            if cancel_request_box != None:
                print(f"Already requested {group_id}, waiting to be approved!") 
        except:
            x = driver.find_element_by_tag_name('body').text
            if x.find("Không thể xử lý yêu cầu của bạn") >= 0 :
                print(f"Group doesn't exists. Please check group id {group_id}")
            else:
                print(f"Can't join group {group_id} because of exception: ")
                print(e)
    sleep(1)

def request_join_from_csv(driver, groups_file, usr):
    """
    Join a list of groups specified in a csv file. 
    ALERT!: This function must be called after calling login_fb()
    The csv must have atleast 3 columns:
        - group_id (string, int): contains the uid of the groups
        - joined_accounts (string) : contains the usernames of accounts which joined the groups, separated by comma
    Parameters:
        - driver (selenium web driver object)
        - groups_file (string): path to csv file containing group ids
        - usr (string): username of the fb account used to join
    """
    groups_df = pd.read_csv(groups_file, na_values="")
    groups_df['group_id'] = groups_df['group_id'].astype(str)
    for _, row in groups_df.iterrows():
        if usr in str(row['joined_accounts']).split(','):
            print(f"Aready joined group {row['group_id']}")
            return
        request_join_group(driver, row['group_id'])        
def check_joined_group(driver, group_id):
    """
    Return True if joined group, else return False
    ALERT!: This function must be called after calling login_fb()
    Parameters:
        - driver (selenium web driver object)
        - group_id (string, int): the uid of a facebook group
    """

    base_url = "https://m.facebook.com/groups/"
    driver.get(base_url + str(group_id))
    sleep(1)
    try:
        _ = driver.find_element_by_css_selector("a[aria-label='Đã tham gia']")
        return True
    except:
        return False

def check_joined_from_csv(driver, groups_file, usr):
    """
    Check if joined a list of groups specified in a csv file.
    ALERT!: This function must be called after calling login_fb()
    The csv must have atleast 3 columns:
        - group_id (string, int): contains the uid of the groups
        - joined_accounts (string) : contains the usernames of accounts which joined the groups, separated by comma
        - joined (boolean): True if len(joined_accounts) > 0
    Parameters:
        - driver (selenium web driver object)
        - groups_file (string): path to csv file containing group ids
        - usr (string): username of the fb account used to join
    """

    #loop through uids
    #if username already in "joined_groups" column --> skip this uid
    # --> call check_joined_group
    # --> write to file if joined
    print("Checking if joined groups...")
    groups_df = pd.read_csv(groups_file)
    groups_df['joined_accounts'] = groups_df['joined_accounts'].astype(str)

    for index, row in groups_df.iterrows():
        joined_accounts = set(str(row['joined_accounts']).replace('nan', '').split(','))
        if usr in joined_accounts:
            print(f"Aready joined group {row['group_id']}")
            continue
        group_id = row['group_id']
        if check_joined_group(driver, group_id):
            joined_accounts.add(usr)
            if not row['joined']:
                groups_df.at[index, 'joined'] = True
            print(f"Joined {group_id}")
        else:
            print(f"Didn't join {group_id}")
        groups_df.at[index, 'joined_accounts'] = ','.join([account for account in joined_accounts])
    groups_df.to_csv(groups_file, index = False)
def write_unjoined_groups(unjoined_groups, group_ids_file):
    """USELESS FUNCTION"""
    with open(group_ids_file, 'w') as f:
        for group_id in unjoined_groups:
            f.write(str(group_id) + "\n")
def write_joined_groups(joined_groups, joined_groups_file, usr, pwd):
    """USELESS FUNCTION"""
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
    """USELESS FUNCTION"""
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
def join_multiple_accounts(groups_file, fb_accounts_file, mode):
    """
    Join groups, check if joined groups with multiple accounts given in a csv file.
    Groups are specified in a csv file which has at least 3 columns:
        - group_id (string, int): contains the uid of the groups
        - joined_accounts (string) : contains the usernames of accounts which joined the groups, separated by comma
        - joined (boolean): True if len(joined_accounts) > 0
    Account file has at least 2 columns:
        - user (string, int): user name of facebook account
        - pw (string, int): password of the corresponding account
    Parameters:
        - groups_file (string): path to csv file containing groups info
        - fb_accounts_file (string): path to csv file containing user name & password
        - mode (int, string):
            mode == 0: only join groups
            mode == 1: only check join groups
            mode == 2: join groups then check join groups
    """
    if str(mode) == '0':
        print("***WORKING IN MODE 0: ONLY JOIN GROUPS***")
    elif str(mode) == '1':
        print("***WORKING IN MODE 1: ONLY CHECK IF JOINED GROUPS***")
    elif str(mode) == '2':
        print("***WORKING IN MODE 2: JOINING GROUPS THEN CHECKING IF JOINED GROUPS***")
    else:
        print("Wrong mode! mode parameter only accept 3 values: 0, 1 or 2. Please choose one of the 3 modes:")
        print("mode == 0: only join groups")
        print("mode == 1: only check if joined groups")
        print("mode == 2: join groups then check if joined")
        return
    options = Options()
    options.headless = True
    DRIVER_PATH = r"drivers/geckodriver"
    accounts_df = pd.read_csv(fb_accounts_file)
    for _, row in accounts_df.iterrows():
        usr, pwd = str(row['user']).strip(), str(row['pw']).strip()
        driver = webdriver.Firefox(executable_path = DRIVER_PATH, options = options)
        logged_in = login_fb(driver, usr, pwd)
        if logged_in:
            if str(mode) == '0':
                request_join_from_csv(driver, groups_file, usr)
            elif str(mode) == '1':
                check_joined_from_csv(driver, groups_file, usr)
            elif str(mode) == '2':
                check_joined_from_csv(driver, groups_file, usr)
                request_join_from_csv(driver, groups_file, usr)
        driver.close()
if __name__ == "__main__":
    # options = Options()
    # options.headless = False
    # DRIVER_PATH = r"drivers/geckodriver.exe"
    # driver = webdriver.Firefox(executable_path = DRIVER_PATH, options = options)
    # logged_in = login_fb(driver, "minh.moc.2000", "dataemgomeer")
    # request_join_from_csv(driver, "test_groups.csv", "minh.moc.2000")
    # driver.close()
    join_multiple_accounts(fb_accounts_file= args.accountfile, groups_file=args.file, mode=args.mode)
    # print("do nothing")