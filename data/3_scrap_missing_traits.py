import requests
import pandas as pd
from time import sleep
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from deep_translator import GoogleTranslator


def fix_name(char_name: str) -> str:
    if ',' not in char_name:
        return char_name
    char_name = char_name.split(', ')
    char_name = char_name[1:] + [char_name[0]]
    char_name = ' '.join(char_name)
    return char_name


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def receive():
    URL_CHARACTER = "https://www.animecharactersdatabase.com/api_series_characters.php?character_q="
    URL_CHAR_BY_ID = "https://www.animecharactersdatabase.com/characters.php?id="
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    }
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    df = pd.read_excel('data/dataset_scrapped.xlsx')
    animes = df[['Título do anime', 'Nome do personagem']]
    for anime, character_ in animes.values[200:]:
            character = fix_name(character_)
            try:
                query_character = requests.get(url=URL_CHARACTER+character, headers=HEADERS).json()
            except Exception:
                print(URL_CHARACTER+character, 'Exception on query')
                continue
            sleep(0.5)
            if query_character == -1:
                continue
            query_character = query_character['search_results']
            similarity_index = 0.0
            resulting_character = -1
            TITLE_THRESHOLD = 0.8
            resulting_id = ''
            for result in query_character:
                character_name = result['name']
                anime_name = result['anime_name']
                test_index = similar(character, character_name)
                title_index = similar(anime, anime_name)
                if similarity_index < test_index and title_index > TITLE_THRESHOLD:
                    similarity_index = test_index
                    resulting_character = character_name
                    resulting_id = result['id']
            if not resulting_character:
                continue
            driver.get(URL_CHAR_BY_ID+str(resulting_id))
            try:
                table = driver.find_element(By.CSS_SELECTOR, "html body#body div.sitecontainer div#mainframe1.outframe div#characterzone.characters_side div.characters_side_b table.zero.pad.left.bo2")
            except Exception:
                continue
            condition = (df['Título do anime'] == anime) & (df['Nome do personagem'] == character_)
            trait_map = {
                'Hair Color': 'Cor do cabelo',
                'Eye Color': 'Cor dos olhos'
            }
            for row in table.find_elements(By.CSS_SELECTOR, "tr"):
                try:
                    cell0 = row.find_element(By.CSS_SELECTOR, "th")
                    trait = cell0.text.strip().strip('\n')
                    cell1 = row.find_elements(By.CSS_SELECTOR, "td")
                    appears = cell1[0].text
                    if trait in trait_map and pd.isna(df.loc[condition, trait_map[trait]].values[0]):
                        if trait == 'Hair Color':
                            appears += ' hair'
                        elif trait == 'Eye Color':
                            appears += ' eyes'
                        print(appears)
                        translated = GoogleTranslator(source='en', target='pt').translate(text=appears).capitalize()
                        print(translated)
                        df.loc[condition, trait_map[trait]] = translated
                except Exception:
                    continue
            print(df.loc[condition])
            print('')
    df.to_excel('data/dataset_filledNA.xlsx')
    driver.quit()


if __name__ == '__main__':
    receive()
