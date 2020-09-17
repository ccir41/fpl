import sys
import time
import csv
from operator import itemgetter

from decouple import config

from selenium import webdriver


class FFM:
    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.base_url = "https://fantasy.premierleague.com/"
        self.league_url = "https://fantasy.premierleague.com/leagues"
        self.league_name = None
        self.details = []

    def sign_in(self):
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        # wait 2s to load page
        time.sleep(2)
        self.driver.find_element_by_id(
            "loginUsername").send_keys(config("EMAIL"))
        self.driver.find_element_by_id(
            "loginPassword").send_keys(config("PASSWORD"))
        self.driver.find_element_by_tag_name('button').submit()
        time.sleep(2)
        self.extract_leagues()
        #current_url = driver.current_url

    def extract_leagues(self):
        self.driver.get(self.league_url)
        time.sleep(2)
        leagues = self.driver.find_elements_by_css_selector(
            "div.sc-AykKC.jsjLzv")
        # print(len(leagues))
        data = []

        # skip first sections of tile "My Leagues"
        for league in leagues[1:]:
            league_title = league.find_element_by_tag_name("h4").text
            league_title_links = league.find_elements_by_css_selector(
                "a.Link-a4a9pd-1.hnWgWg")

            league_details = []

            for league_title_link in league_title_links:
                league_detail = {
                    "title": league_title_link.text,
                    "link": league_title_link.get_attribute('href')
                }
                league_details.append(league_detail)

            data.append({'league': league_title, 'details': league_details})

        # print(data)
        self.user_choice(data)

    def user_choice(self, data):
        for record in data:
            print("\n###################################################################")
            print("##### Do you want to extract {} records? #####".format(
                record['league']))
            print("###################################################################\n")
            user_input = input(
                "Press Y and Enter key for Yes else other keys for deny: ")
            if user_input == 'Y' or user_input == 'y':
                self.user_league_choice(record['details'])
            else:
                continue
        self.driver.close()

    def user_league_choice(self, details):
        for detail in details:
            print("\n\t##############################################################")
            print("\t##### Do you want to extract {} records? #####".format(
                detail['title']))
            print("\t##############################################################\n")
            user_input = input(
                "\tPress Y and Enter key for Yes else other keys for deny: ")
            if user_input == 'Y' or user_input == 'y':
                self.league_name = detail['title']
                self.extract_standings(detail['link'])
            else:
                continue
        self.driver.close()

    def extract_standings(self, link):
        self.driver.get(link)
        time.sleep(2)
        tables = self.driver.find_elements_by_css_selector(
            "table.Table-ziussd-1.fVnGhl")
        if tables:
            # first table is league table and second for new entry members
            standing_table = tables[0]
            table_rows = standing_table.find_elements_by_css_selector(
                "tr.StandingsRow-fwk48s-0.GxMKk")
            # print(len(table_rows))
            # 50 records per each page
            for table_row in table_rows:
                table_data = table_row.find_elements_by_tag_name("td")
                team_manager = table_data[1].text.split('\n')
                self.details.append({
                    'rank': int(table_data[0].text),
                    'team': team_manager[0],
                    'manager': team_manager[1],
                    'gameweek_points': int(table_data[2].text),
                    'total_points': int(table_data[3].text)
                })

            page_links = self.driver.find_elements_by_css_selector(
                "a.ButtonLink__StyledButtonLink-sc-457mfk-1.jDfjsN")

            if page_links:
                # max 4 buttons available with same css class and name with 2 Next and 2 Previous
                for page_link in page_links:
                    # condition for testing upto 3 pages only
                    # if page_link.text == 'Next' and 'page_standings=4' in page_link.get_attribute('href'):
                    #     break
                    if page_link.text == 'Next' and 'page_new_entries=1' in page_link.get_attribute('href'):
                        link = page_link.get_attribute('href')
                        self.extract_standings(link)

        # print(self.details)
        rank_filename = f"{self.league_name}_league_by_rank.csv"
        self.write_csv(self.details, rank_filename)

        sorted_details = self.sort_by_gameweek()
        gw_filename = f"{self.league_name}_league_by_gameweek_points.csv"
        self.write_csv(sorted_details, gw_filename)

        self.quit()

    def sort_by_gameweek(self):
        sorted_details = sorted(self.details, key=itemgetter(
            'gameweek_points'), reverse=True)
        return sorted_details

    def write_csv(self, data, filename):
        with open(filename, 'w', encoding='utf8', newline='') as output_file:
            file = csv.DictWriter(output_file, fieldnames=data[0].keys())
            file.writeheader()
            file.writerows(data)

    def quit(self):
        self.driver.close()
        sys.exit()


ffm = FFM()
ffm.sign_in()
