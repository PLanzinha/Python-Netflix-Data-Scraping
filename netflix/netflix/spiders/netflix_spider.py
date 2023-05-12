from scrapy.spiders import CrawlSpider
from bs4 import BeautifulSoup
import pandas as pd
import re
# needs this else it won't create the excel file - pip install openpyxl


class NetflixCrawler(CrawlSpider):
    name = "netflixcrawler"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = [
        'file:///D:/pycharm/Projects/GUIPythonProjects/NetflixScrapping/List_of_Netflix_original_programming.htm']
    # https://en.wikipedia.org/wiki/List_of_Netflix_original_programming

    def parse_start_url(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')

        excluded_span = ["Contents", "Notes", "References", "External links", "Upcoming original programming"]
        excluded_table_header = ["Runtime", "Status"]

        element_h2 = soup.find_all('h2')
        data_list = []

        for h2 in element_h2:
            element_span = h2.find('span')
            if element_span:
                span_text = element_span.get_text()
                if span_text not in excluded_span:
                    second_span = h2.find('span', class_='mw-headline')
                    if second_span:
                        span_text = second_span.get_text()
                        print(span_text)

            element_table = h2.find_next('table', class_='wikitable')
            if h2.find('span', text='Upcoming original programming'):
                break

            if element_table:
                rows = element_table.find_all('tr')
                for row in rows:
                    table_cells = row.find_all('td')
                    data = {}
                    for i, table_cell in enumerate(table_cells):
                        if table_cell in excluded_table_header:
                            continue
                        cell_text = table_cell.get_text().strip()
                        cell_text = re.sub(r'\[[0-9]+\]', '', cell_text)
                        if "Upcoming original programming" in cell_text:
                            break
                        data[f"{i}"] = cell_text
                    else:
                        for key, value in data.items():
                            data_list.append(data)
                            # print(f"{value}")

        data_frame = pd.DataFrame(data_list)
        data_frame.to_excel("netflix_series.xlsx", index=False)