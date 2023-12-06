import requests

def receive():
    main_characters_names = []
    animes = requests.get("https://api.jikan.moe/v4/top/anime?page=4")
    anime_dict = animes.json()
    for i in range(len(anime_dict.get('data'))):
        mal_id = anime_dict.get('data')[i]['mal_id']
        characters = requests.get("https://api.jikan.moe/v4/anime/" + str(mal_id) + "/characters")
        character_dict = characters.json().get('data')
        for character in character_dict:
            if character['role'] == "Main":
                main_characters_names.append(character['character']['name'])
    for character in main_characters_names:
        print(character)
    return main_characters_names