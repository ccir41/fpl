import sys
import time
import json
import csv
import getpass

from operator import itemgetter

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument('--disable-notifications')

chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.headless = True

# sys.setrecursionlimit(100000)


class FFM:
    def __init__(self, email, password, league_name):
        #self.driver = webdriver.Chrome(executable_path="./chromedriver")
        self.driver = webdriver.Chrome(
            executable_path="./chromedriver", options=chrome_options)
        self.base_url = "https://fantasy.premierleague.com/"
        self.success_url = "https://fantasy.premierleague.com/?status=success"
        self.login_failure_url = "https://fantasy.premierleague.com/?state=fail&reason=credentials"
        self.league_url = "https://fantasy.premierleague.com/leagues"
        self.email = email.lower()
        self.password = password
        self.league_name = league_name.lower()
        self.log_filename = None
        self.league_link = None
        self.start_time = time.time()
        self.details = None
        self.csv_headers = []
        self.append_header = False
        self.finished = False
        self.opened_link_file = False
        self.write_headers = False
        self.count = 0

    def sign_in(self):
        self.driver.set_page_load_timeout(30)  # Timeout of 30 seconds
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        time.sleep(3)
        try:
            game_updating = self.driver.find_element_by_css_selector("div.Copy-zj3yf2-0.bktLPz")
        except:
            game_updating = None
        if game_updating:
            print("*****************************************************************************************")
            print("\tThe game is being updated.")
            print("\tPlease try again later when the updated scores / teams will be available.")
            print("*****************************************************************************************")
            time.sleep(10)
            sys.exit()

        self.driver.find_element_by_id(
            "loginUsername").send_keys(self.email)
        self.driver.find_element_by_id(
            "loginPassword").send_keys(self.password)
        self.driver.find_element_by_tag_name('button').submit()
        current_url = str(self.driver.current_url)
        if current_url != self.login_failure_url:
            print("login successful!")
            self.extract_leagues()
        else:
            print("*****************************************************************************************")
            print("\t\tError: Invalid Email or Password!")
            print("*****************************************************************************************")
            time.sleep(10)
            sys.exit()

    def extract_leagues(self):
        while True:
            self.driver.get(self.league_url)
            time.sleep(3)
            leagues = self.driver.find_elements_by_css_selector(
                "div.sc-AykKC.jsjLzv")
            # print(len(leagues))
            league_links = self.driver.find_elements_by_xpath(
                "//div[@class='Panel__StyledPanel-sc-1nmpshp-0 eSHooN']//div//table[@class='Table-ziussd-1 MyLeagues__MyLeaguesTable-sc-3hyp7w-4 busPSm']//a[@class='Link-a4a9pd-1 hnWgWg']")
            if league_links:
                break

        for league_link in league_links:
            league_name = league_link.text.strip().lower()
            if league_name == self.league_name:
                self.league_link = league_link.get_attribute('href')
                break
        if self.league_link:
            self.extract_standings()
        else:
            print("*****************************************************************************************")
            print("\t\tError: League not found!")
            print("*****************************************************************************************")
            time.sleep(300)
            sys.exit()

    def extract_standings(self):
        self.log_filename = f"{self.league_name}_log.txt"
        while not self.opened_link_file:
            try:
                link_file = open(self.log_filename, 'r')
                lines = link_file.readlines()
                if len(lines) >= 1:
                    self.league_link = lines[-1]
                    link_file.close()
                self.opened_link_file = True
            except:
                break

        while True:
            self.driver.get(self.league_link)
            time.sleep(3)
            tables = self.driver.find_elements_by_css_selector(
                "table.Table-ziussd-1.fVnGhl")
            # first table is league table and second for new entry members
            if tables:
                standing_table = tables[0]
                table_rows = standing_table.find_elements_by_css_selector(
                    "tr.StandingsRow-fwk48s-0")
                # print(len(table_rows))
                # 50 records per each page
                for table_row in table_rows:
                    table_data = table_row.find_elements_by_tag_name("td")
                    rank = int(table_data[0].text)
                    team_manager = table_data[1].text.split('\n')
                    team = team_manager[0]
                    manager = team_manager[1]
                    gameweek_points = int(table_data[2].text)
                    total_points = int(table_data[3].text)
                    manager_link = table_data[1].find_element_by_tag_name(
                        'a').get_attribute('href')
                    transfer_cost = 100
                    transfer = 100
                    while True:
                        try:
                            self.driver.switch_to.window(
                                self.driver.window_handles[1])
                        except:
                            self.driver.execute_script("window.open('');")
                            self.driver.switch_to.window(
                                self.driver.window_handles[1])
                        self.driver.get(manager_link)
                        time.sleep(2)
                        transfer_cost_container = self.driver.find_elements_by_xpath(
                            "//div[@class='EntryEvent__ScoreboardSecondary-l17rqm-8 ltWIy']//div[@class='EntryEvent__SecondaryPanel-l17rqm-9 jQWayT']//div[@class='EntryEvent__SecondaryItem-l17rqm-10 gholFw']//div[@class='EntryEvent__SecondaryValue-l17rqm-12 gBqbeC']")
                        # print(len(transfer_cost_container)) #4
                        if transfer_cost_container:
                            try:
                                transfer_string = transfer_cost_container[3].text
                            except:
                                transfer_string = None
                            if transfer_string:
                                transfer_content = transfer_string.split(' (')
                                transfer = int(transfer_content[0])
                                if len(transfer_content) > 1:
                                    transfer_cost = int(
                                        transfer_content[1].split(' ')[0])
                                else:
                                    transfer_cost = 0
                                self.driver.switch_to.window(
                                    self.driver.window_handles[0])
                                self.count += 1
                                print(f"request number: {self.count}")
                                break
                            else:
                                continue

                    # sorting place single digit row in first place
                    net_gameweek_points = gameweek_points + transfer_cost
                    if net_gameweek_points < 10:
                        net_gameweek_points = '00' + str(net_gameweek_points)
                    else:
                        net_gameweek_points = '0' + str(net_gameweek_points)
                    if gameweek_points < 10:
                        gameweek_points = '00' + str(gameweek_points)
                    else:
                        gameweek_points = '0' + str(gameweek_points)
                    data = {
                        'rank': rank,
                        'team': team,
                        'manager': manager,
                        'transfers': transfer,
                        'transfers_cost': transfer_cost,
                        'gameweek_points': gameweek_points,
                        'net_gameweek_points': net_gameweek_points,
                        'total_points': total_points
                    }
                    print(data)
                    # self.details.append(data)
                    gw_filename_unsorted = f"{self.league_name}_unsorted_and_duplicate.csv"
                    self.append_csv(data, gw_filename_unsorted)

                page_links = self.driver.find_elements_by_css_selector(
                    "a.ButtonLink__StyledButtonLink-sc-457mfk-1.jDfjsN")

                if page_links:
                    next_link = None
                    # max 4 buttons available with same css class and name with 2 Next and 2 Previous
                    for page_link in page_links:
                        # condition for testing upto 3 pages only
                        # if page_link.text == 'Next' and 'page_standings=4' in page_link.get_attribute('href'):
                        #     break
                        if page_link.text == 'Next' and 'page_new_entries=1' in page_link.get_attribute('href'):
                            self.league_link = page_link.get_attribute('href')
                            next_link = self.league_link
                            self.append_url(self.league_link)
                            break
                    if not next_link:
                        break
                else:
                    break

        # print(self.details)
        self.read_csv(f"{self.league_name}_unsorted_and_duplicate.csv")
        removing_duplicate_time = time.time()
        self.details = [i for n, i in enumerate(self.details) if i not in self.details[n + 1:]]
        print("\n")
        print(
            f"Time for removing duplicate records is: {self.time_elapsed(removing_duplicate_time, time.time())}")
        rank_filename_csv = f"{self.league_name}_by_rank.csv"
        self.write_csv(self.details, rank_filename_csv)
        sorted_details = self.sort_by_gameweek()
        gw_filename_sorted = f"{self.league_name}_by_gameweek_points.csv"
        self.write_csv(sorted_details, gw_filename_sorted)
        print(
            f"Total time taken : {self.time_elapsed(self.start_time, time.time())}")
        time.sleep(10)
        sys.exit()

    def get_transfer_cost(self, manager_link):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
        except:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(manager_link)
        time.sleep(2)
        transfer_cost_container = self.driver.find_elements_by_xpath(
            "//div[@class='EntryEvent__ScoreboardSecondary-l17rqm-8 ltWIy']//div[@class='EntryEvent__SecondaryPanel-l17rqm-9 jQWayT']//div[@class='EntryEvent__SecondaryItem-l17rqm-10 gholFw']//div[@class='EntryEvent__SecondaryValue-l17rqm-12 gBqbeC']")
        # print(len(transfer_cost_container)) #4
        # print(transfer_cost_container[3].text)
        try:
            transfer_string = transfer_cost_container[3].text
            transfer_content = transfer_string.split(' (')
            transfer = int(transfer_content[0])
            if len(transfer_content) > 1:
                transfer_cost = int(transfer_content[1].split(' ')[0])
            else:
                transfer_cost = 0
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.count += 1
            print(f"request number: {self.count}")
            return transfer, transfer_cost
        except:
            self.get_transfer_cost(manager_link)
        return 0, 0
        """
        1
        1
        0
        2 (-4 pts)
        2 (-4 pts)
        """

    def sort_by_gameweek(self):
        sorting_time = time.time()
        sorted_details = sorted(self.details, key=itemgetter(
            'net_gameweek_points'), reverse=True)
        print(
            f"Time for sorting records is: {self.time_elapsed(sorting_time, time.time())}")
        return sorted_details

    def append_url(self, url):
        with open(self.log_filename, 'a+') as output_file:
            output_file.write(f"\n{url}")

    def write_csv(self, data, filename):
        with open(filename, 'w', encoding='utf8', newline='') as output_file:
            file = csv.DictWriter(output_file, fieldnames=self.csv_headers)
            if not self.write_headers:
                file.writeheader()
                self.write_headers = True
            file.writerows(data)

    def append_csv(self, data, filename):
        if not self.csv_headers:
            for key, value in data.items():
                self.csv_headers.append(key)
        with open(filename, 'a+', encoding='utf8', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=self.csv_headers)
            if not self.append_header:
                writer.writeheader()
                self.append_header = True
            writer.writerow(data)

    def read_csv(self, filename):
        with open(filename, 'r', encoding='utf-8', newline='') as input_file:
            reader = csv.DictReader(input_file)
            self.details = list(reader)
            return True

    def time_elapsed(self, start, end):
        time_diff = end - start
        if time_diff < 60:
            return f"{time_diff} seconds"
        elif time_diff >= 60 and time_diff < 3600:
            time_diff = time_diff / 60
            return f"{time_diff} minutes"
        elif time_diff >= 3600:
            time_diff = time_diff / 3600
            return f"{time_diff} hours"
        else:
            return "no time"

    def quit(self):
        self.driver.close()
        sys.exit()


if __name__ == "__main__":
    email = input("Email: ")
    password = getpass.getpass()
    league_name = input("Classic League Name: ")
    ffm = FFM(email, password, league_name)
    ffm.sign_in()
