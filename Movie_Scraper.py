# -*- coding: utf-8 -*-
"""FinalProjectPt1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1G3xXWLJeC04drkNKeVGLyqCFQ2KRCJsM

# Dependencies
Importing the following libraries:
- Selenium
- BeautifulSoup4
- Pandas
- re
- datetime
- os
"""

# import pre-downloaded dependencies
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import time
import datetime
import os

# Commented out IPython magic to ensure Python compatibility.
# download and import Google Colab Selenium (was having trouble getting Selenium)
# %pip install -q google-colab-selenium

import sys
import time
import os
import google_colab_selenium as gs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

"""# Define Constants"""

# constants
MAX_MOVIES_PER_PAGE = 30
MAX_MOVIES = 500 + MAX_MOVIES_PER_PAGE
MAX_TRIES = 5
ENTRY_URL = "https://www.rottentomatoes.com/browse/movies_at_home/critics:certified_fresh,fresh,rotten~sort:a_z?page=5"
EXPORT_DIR = './dataset/'
FILE_NAME = 'movies.csv'
HEADERS = [
  "title",
  "summary",
  "director",
  "producer",
  "screenwriter",
  "rating",
  "genre",
  "language",
  "release_date",
  "net_gross",
  "runtime",
  "critic_score",
  "audience_score",
]
CHROME_BIN = '/usr/bin/chromium-browser'
CHROMEDRIVER_BIN = '/usr/bin/chromium-driver'

# create the export directory
os.makedirs(EXPORT_DIR, exist_ok=True)

"""# Setting Up Our Scrapers

"""

def make_driver(
    options_flags: list[str] = []
) -> webdriver.Chrome:
  # Instantiate options
  options = Options()

  # Add extra options
  for flag in options_flags:
    options.add_argument(flag)
  driver = gs.Chrome(options=options)
  return driver

def get_scraper(url) -> BeautifulSoup:
  for i in range(MAX_TRIES):
    print(f"GET {url}...")
    res = requests.get(
      url,
    )
    if res.status_code == 200:
      print("Finished GET request.")
      print()
      break
    else:
      print(f"Status Code: {res.status_code}")
      print("Failed to retrieve response (1 time). Trying again." if i == 0 else f"Failed to retrieve response ({i+1} times). Trying again.")
      time.sleep(2)

  return BeautifulSoup(res.text, 'html.parser')

def parse_score(score_str):
  result = re.match(r"(\d+)%", score_str)
  if result:
    return int(result.group(1))
  return None

def parse_runtime(runtime_str):
  match = re.match(r"(\d+)h (\d+)m", runtime_str)
  if match:
    hours = int(match.group(1))
    minutes = int(match.group(2))
    return hours * 60 + minutes
  else:
    return None

def parse_rating(rating_string):
  match = re.match(r"([A-Z0-9\-]+)", rating_string)
  if match:
    return match.group(1)
  return None

def parse_release_date(date_string):
  try:
    # Split the date string by comma and take only the first two parts
    date_parts = date_string.split(',')[:2]
    # Join the parts back with a comma, reconstructing the date portion
    date_part = ','.join(date_parts).strip()
    # Parse the date using the correct format
    return datetime.datetime.strptime(date_part, '%b %d, %Y').strftime('%B %d, %Y')
  except ValueError:
    return None

def parse_gross(gross_str):
  match = re.match(r"\$(\d+\.?\d*)([BMK])", gross_str)  # Modified regex
  if match:
    amount = float(match.group(1))
    magnitude = match.group(2)  # Get magnitude (B, M, or K)
    if magnitude == "B":
      return int(amount * 1000000000)  # Calculation for billions
    elif magnitude == "M":
      return int(amount * 1000000)
    elif magnitude == "K":
      return int(amount * 1000)
  return None

"""# Scrape Rotten Tomatoes"""

def scrape_info_from_url(
    url: str,
    movie_info: dict,
    max_tries: int = MAX_TRIES,
) -> dict:
  scraper = get_scraper(url)
  keys_found = set()

  # first, get the critic and audience scores
  critic_container = scraper.select_one("rt-text[slot='criticsScore']")
  raw_critics_score = critic_container.text
  audience_container = scraper.select_one("rt-text[slot='audienceScore']")
  raw_audience_score = audience_container.text
  movie_info["critic_score"].append(parse_score(raw_critics_score))
  movie_info["audience_score"].append(parse_score(raw_audience_score))

  # next, get the title and summary of the movie
  movie_title = scraper.select_one("div#movie-overview rt-text[slot='title']").text
  movie_info["title"].append(movie_title)
  summary = scraper.select_one("rt-text[data-qa='synopsis-value']")
  summary = "" if summary is None else summary.text
  movie_info["summary"].append(summary)

  # track which fields we've found for this movie
  found_keys = {
      "director": False,
      "producer": False,
      "screenwriter": False,
      "runtime": False,
      "rating": False,
      "genre": False,
      "release_date": False,
      "language": False,
      "net_gross": False
  }

  # now, for the rest, all of our info will be coming from the bottom of the page
  info_containers = scraper.select("div.content-wrap dl > div.category-wrap")

  for container in info_containers:
      key_element = container.select_one("dt")
      value_element = container.select_one("dd")

      if not key_element or not value_element:
          continue

      key = key_element.text.strip().lower()
      value = value_element.text.strip().replace('\n', '')
      # print(key)

      if value.find(",") != -1:
          value = ";".join(value.split(","))
      # print(value)

      if key == "director":
          movie_info[key].append(value)
          found_keys[key] = True

      elif key == "producer":
          movie_info[key].append(value)
          found_keys[key] = True

      elif key == "screenwriter":
          movie_info[key].append(value)
          found_keys[key] = True

      elif key == "runtime":
          value = parse_runtime(value)
          movie_info[key].append(value)
          found_keys[key] = True

      elif key == "rating":
          value = parse_rating(value)
          movie_info[key].append(value)
          found_keys[key] = True

      elif key == "genre":
          movie_info[key].append(value)
          found_keys[key] = True

      elif key.startswith("release date"):
          value = value.replace(';', ',')
          if (key.find("theaters") != -1 or key.find("streaming") != -1) and not found_keys["release_date"]:
              movie_info["release_date"].append(parse_release_date(value))
              found_keys["release_date"] = True

      elif key == "original language":
          movie_info["language"].append(value)
          found_keys["language"] = True

      elif key.startswith("box office"):
          movie_info["net_gross"].append(parse_gross(value))
          found_keys["net_gross"] = True

  # for any keys that weren't found for this movie, just put an empty value
  for key, was_found in found_keys.items():
      if not was_found:
          movie_info[key].append("")

  return movie_info

# i came up with the logic for this on my own
def scrape_urls_from_entry(
    url: str,
    driver: webdriver.Chrome,
    max_movies: int,
    delay: int = 15
) -> list[str]:
    driver.get(url)
    time.sleep(delay)

    try:
        page_count = int(re.search(r"page=(\d+)", url).group(1))
    except AttributeError:
        page_count = 1

    print(f"Starting the scrape from page {page_count}...")
    num_movies = 0
    urls = set()

    while num_movies < max_movies:
        # wait for page load
        time.sleep(5)
        try:
            WebDriverWait(driver, delay).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.js-tile-link'))
            )
        except TimeoutException:
            print("Timeout waiting for links to load. Continuing with available links.")

        # to avoid stale element references
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1) # to allow for lazy loading

        try:
            # we can use JS to run scripts to avoid lazy loading
            potential_links_hrefs = driver.execute_script("""
                const links = document.querySelectorAll('.js-tile-link');
                const urls = [];
                for (let link of links) {
                    if (link.tagName === 'A') {
                        urls.push(link.href);
                    } else {
                        const a = link.querySelector('a');
                        if (a) {
                            urls.push(a.href);
                        }
                    }
                }
                return urls;
            """)

            for href in potential_links_hrefs:
                if href and href not in urls:
                    urls.add(href)
                    num_movies += 1
                    if num_movies >= max_movies:
                        break

            if num_movies >= max_movies:
                break

            # click the "Load More" button if needed
            try:
                # using JS, we can tell if the button exists or not
                button_exists = driver.execute_script("""
                    const button = document.querySelector('button[data-qa="dlp-load-more-button"]');
                    if (button && !button.disabled && button.offsetParent !== null) {
                        button.click();
                        return true;
                    }
                    return false;
                """)

                if button_exists:
                    print("Clicked the 'Load More' button.")
                    page_count += 1
                    print(f"Scraping from page {page_count}.")
                    time.sleep(delay / 2)  # Wait for new content to load
                else:
                    print('No more reviews or button not clickable. Exiting the loop.')
                    break

            except Exception as ex:
                print(f'Error clicking "Load More" button: {ex}. Exiting the loop.')
                break

        except Exception as ex:
            print(f"Error processing links: {ex}")
            break

    print(f"Found {len(urls)} movie URLs")
    return list(urls)

def scrape(
    driver = None,
    url: str = ENTRY_URL,
    max_movies: int = MAX_MOVIES,
    export_dir: str = EXPORT_DIR,
    file_name: str = FILE_NAME,
    delay: int = 15,
    max_tries: int = MAX_TRIES,
) -> None:
    if not driver:
        driver = make_driver()

    try:
        urls = scrape_urls_from_entry(url, driver, max_movies, delay)
        driver.quit()

        print(f"Scraping {len(urls)} movies...")
        movies_dict = {}
        for header in HEADERS:
            movies_dict[header] = []

        for url in urls:
            print(f"Scraping {url}...")
            try:
                movies_dict = scrape_info_from_url(url, movies_dict, max_tries)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                # Add empty values for this movie to keep lengths consistent
                for header in HEADERS:
                    if header not in ["critic_score", "audience_score"]:  # These were already handled
                        movies_dict[header].append("")

        df = pd.DataFrame(movies_dict)

        # Make sure the export directory exists
        os.makedirs(export_dir, exist_ok=True)
        df.to_csv(os.path.join(export_dir, file_name), index=False, encoding='utf-8')
        print(f"Successfully exported data to {os.path.join(export_dir, file_name)}")

        return df

    except Exception as e:
        print(f"Error during scraping: {e}")
        if driver:
            driver.quit()
        raise

driver = make_driver()

df = scrape(driver)