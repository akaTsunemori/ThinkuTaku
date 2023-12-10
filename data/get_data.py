import requests
import pandas as pd


def receive():
    URL = "https://api.jikan.moe/v4/top/anime?filter=bypopularity&page="
    pages = 6
    df = pd.DataFrame(columns=['anime_title', 'character_name'], index=None)
    for page in range(1, pages+1):
        animes = requests.get(URL+str(page))
        anime_dict = animes.json()
        num_animes = len(anime_dict.get('data'))
        for i in range(num_animes):
            mal_id = anime_dict.get('data')[i]['mal_id']
            title = anime_dict.get('data')[i]['title_english']
            characters = requests.get("https://api.jikan.moe/v4/anime/" + str(mal_id) + "/characters")
            characters_dict = characters.json().get('data')
            if not characters_dict:
                continue
            if not title:
                continue
            for character in characters_dict:
                if character['role'] == "Main":
                    character_name = character['character']['name']
                    row = {'anime_title': title, 'character_name': character_name}
                    df.loc[len(df)] = row
                    print(title, character_name)
    df = df.drop_duplicates(subset='character_name')
    df.to_excel('data/characters_new.xlsx', index=False)
    return df


if __name__ == '__main__':
    receive()
