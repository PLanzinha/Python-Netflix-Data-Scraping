# Netflix Crawler


This Netflix Crawler project, is a web scraping project made to extract information on Netflix programming from both Wikipedia and Imdb and generating Excel files with the extracted data.
It uses the Scrapy framework to crawl the page and BeautifulSoup for parsing the HTML content. The extracted data is then organized into a pandas DataFrame and exported to an Excel file.
Features

    Crawl Wikipedia HTML: Scrapes a local Wikipedia HTML file to extract information on Netflix original programming.
    Data Filtering: Filters out irrelevant sections and table headers to focus on important data.
    Data Cleaning: Cleans up the extracted text by removing references and unnecessary characters.
    Export to Excel: Saves the cleaned data into an Excel file (netflix_series.xlsx).