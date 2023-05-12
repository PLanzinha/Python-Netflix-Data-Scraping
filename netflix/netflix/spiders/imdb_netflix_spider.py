from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import os


class IMDBNetflixSpider(CrawlSpider):
    name = 'imdbspider'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/search/title/?companies=co0144901&sort=release_date,'
                  'desc&after=WzE0MzgzMDA4MDAwMDAsOTg0MywidHQ0MzQxNTAwIiwyODQ4OV0%3D']

    def __init__(self, *args, **kwargs):
        super(IMDBNetflixSpider, self).__init__(*args, **kwargs)
        self.titles = []
        self.release_years = []
        self.episode_titles = []
        self.episode_years = []
        self.certificates = []
        self.runtimes = []
        self.genres = []
        self.ratings = []
        self.descriptions = []
        # directors_list = []
        # stars_list = []

    def parse_start_url(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')

        exclude_class = ['inline-block ratings-user-rating', 'sort-num_votes-visible',
                         'lister-item-index unbold text-primary',
                         'wl-ribbon standalone not-inWL', 'global-sprite rating-star no-rating', 'ghost',
                         'text-primary unbold']
        exclude_text = ['Director:', 'Directors:', 'Stars:', 'Star:', 'See full summary']

        element_class = soup.find_all('div', class_='lister-item mode-advanced')

        for element_div in element_class:
            item_list = element_div.find('div', class_='lister-item-content')
            if item_list:
                for class_to_exclude in exclude_class:
                    elements_to_remove = item_list.find_all(class_=class_to_exclude)
                    for element in elements_to_remove:
                        element.decompose()
                for p_element in soup.find_all('p'):
                    for text in exclude_text:
                        if text in p_element.get_text():
                            for element in p_element.find_all(text=True):
                                if text in element:
                                    element.replace_with('')

                # title
                element_title = item_list.find('h3', class_='lister-item-header')
                title_element = element_title.find('a')
                title = title_element.get_text(strip=True)
                self.titles.append(title)

                # year of release
                element_release_year = element_title.find_all('span', class_='lister-item-year text-muted unbold')
                if len(element_release_year) >= 2:
                    release_year = element_release_year[0].get_text()
                else:
                    release_year = 'N/A'
                self.release_years.append(release_year)

                # title episode
                episode_element = title_element.find_next('a')
                episode_title = episode_element.get_text(strip=True)
                if not episode_title or episode_title == 'Add a Plot':
                    episode_title = 'N/A'
                self.episode_titles.append(episode_title)

                # episode release year
                if len(element_release_year) >= 2:
                    episode_year = element_release_year[1].get_text()
                else:
                    episode_year = 'N/A'
                self.episode_years.append(episode_year)

                # pg certificate
                certificate_element = item_list.find('p', class_='text-muted').find_all('span', class_='certificate')

                certificate_values = []

                if not certificate_element:
                    certificate_values = 'N/A'
                else:
                    for certificate in certificate_element:
                        certificate_values.append(certificate.get_text(strip=True))
                self.certificates.append(certificate_values)

                # movie / series runtime
                element_runtime = item_list.find('p', class_='text-muted')
                runtime_elements = element_runtime.find_all('span', class_='runtime')
                runtime_values = []
                if not runtime_elements:
                    runtime_values = 'N/A'
                else:
                    for runtime in runtime_elements:
                        text = runtime.get_text(strip=True)
                        if "min" in text:
                            text = text.replace(",", "")
                            runtime_values.append(int(text.replace(" min", "")) if text.isdigit() else 'N/A')
                        else:
                            runtime_values.append('N/A')
                self.runtimes.append(runtime_values)

                # genres
                element_genre = item_list.find('p', class_='text-muted')
                genre_elements = element_genre.find_all('span', class_='genre')
                genre_values = []
                if not genre_elements:
                    genre_values = 'N/A'
                else:
                    for genre in genre_elements:
                        genre_values.append(genre.get_text(strip=True))

                self.genres.append(genre_values)

                # rating
                rating_element = item_list.find('div', class_='inline-block ratings-imdb-rating')
                rating = rating_element.find('strong').get_text(
                    strip=True) if rating_element and 'Rate this' not in rating_element.get_text() else 'N/A'
                self.ratings.append(rating)

                # description
                ratings_bar = item_list.find('div', class_='ratings-bar')
                if ratings_bar:
                    text_muted_element = ratings_bar.find_next('p', class_='text-muted')
                    if text_muted_element:
                        description = text_muted_element.get_text(strip=True)
                        if not description or 'Add a Plot' in description:
                            description = 'N/A'
                    else:
                        description = 'N/A'
                else:
                    description = 'N/A'

                self.descriptions.append(description)
                '''''
                # directors and stars
                directors = []
                stars = []
                for element in item_list.find_all(['a', 'span']):
                    if element.name == 'a':
                        if 'adv_li_dr' in element.get('href'):
                            directors.append(element.text)
                        elif 'adv_li_st' in element.get('href'):
                            stars.append(element.text)
                directors_list.append(directors or 'N/A')
                stars_list.append(stars or 'N/A')
                '''''

        data = {
            'Title': self.titles,
            'Release Year': self.release_years,
            'Episode Title': self.episode_titles,
            'Episode Year': self.episode_years,
            'Certificates': self.certificates,
            'Runtime': self.runtimes,
            'Genre': self.genres,
            'Rating': self.ratings,
            'Description': self.descriptions,
        }

        df = pd.DataFrame(data)

        if os.path.exists("imdb_netflix_catalog.xlsx"):
            existing_df = pd.read_excel("imdb_netflix_catalog.xlsx")
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_excel("imdb_netflix_catalog.xlsx", index=False)
        else:
            df.to_excel("imdb_netflix_catalog.xlsx", index=False)

        button_next = soup.find('a', class_='lister-page-next next-page')

        if button_next:
            relative_url = button_next['href']
            next_page_url = f'https://www.imdb.com{relative_url}'
            print(next_page_url)

            delay = 5 + 15 * random.random()
            time.sleep(delay)

            yield response.follow(next_page_url, callback=self.parse_start_url)
