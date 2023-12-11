import pandas as pd
from random import randrange, choice, choices, shuffle


# SUBSET = [
#     'Cor do cabelo',
#     'Cor dos olhos',
#     'Roupa superior',
#     'Roupa inferior',
#     'Cor dos sapatos',
#     'Acessório 1',
#     'Acessório 2']


SUBSET = [
          'Comprimento do cabelo',
          'Cor do cabelo',
          'Cor dos olhos',
          'Roupa superior',
          'Acessório 1',
          'Acessório 2']


def get_empty(df: pd.DataFrame) -> dict:
    empty_rows = df[SUBSET].isna().all(axis=1)
    empty_rows = df[empty_rows]
    result = dict()
    for row in empty_rows.itertuples(index=False, name=None):
        char_name = row[1]
        anime_name = row[0]
        char_name = fix_name(char_name)
        if anime_name not in result:
            result[anime_name] = []
        result[anime_name].append(char_name)
    return result


def get_duplicated(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.duplicated(keep=False, subset=SUBSET)]


def fix_name(char_name: str) -> str:
    if ',' not in char_name:
        return char_name
    char_name = char_name.split(', ')
    char_name = char_name[1:] + [char_name[0]]
    char_name = ' '.join(char_name)
    return char_name


def gen_causes_dataset(df: pd.DataFrame):
    lines = []
    for row in df.itertuples(index=False, name=None):
        char_name = row[1]
        char_name = fix_name(char_name)
        symptoms = row[2:]
        symptoms = [f'"{i}"' for i in symptoms if type(i) == str]
        probability = randrange(70, 101) / 100
        line = f'"C {char_name}", ({"; ".join(symptoms)}), {probability:.2f}'
        lines.append(line)
    return lines


def gen_symptoms_dataset_random(causes: list, relative_size: int):
    symptoms = []
    causes = [i.split(', ') for i in causes]
    for _, s, __ in causes:
        s = s.strip('(')
        s = s.strip(')')
        s = s.split("; ")
        symptoms.extend(s)
    symptoms = set(symptoms)
    symptoms = list(symptoms)
    size = (relative_size / 100) * len(symptoms)
    size = int(size)
    symptoms_dataset = []
    for _ in range(size):
        k = randrange(2, 6)
        sample = choices(symptoms, k=k)
        symptom = sample[0]
        sample = set(sample)
        while symptom in sample:
            symptom = choice(symptoms)
        probability = randrange(5, 51) / 100
        sample = list(sample)
        shuffle(sample)
        symptoms_relationship = f'"S {symptom.strip(chr(34))}", ({"; ".join(sample)}), {probability:.2f}'
        symptoms_dataset.append(symptoms_relationship)
    shuffle(symptoms_dataset)
    return symptoms_dataset


def gen_symptoms_dataset_deterministic(causes: list, relative_size: int):
    causes = [i.split(', ') for i in causes]
    for i in range(len(causes)):
        cause, symptoms, probability = causes[i][0], causes[i][1], causes[i][2]
        symptoms = symptoms.strip('(').strip(')')
        symptoms = symptoms.split("; ")
        causes[i] = [cause, symptoms, probability]
    size = (relative_size / 100) * len(causes)
    size = int(size)
    symptoms_dataset = []
    visited = set()
    while size:
        cause, symptoms, probability = choice(causes)
        if cause in visited:
            continue
        else:
            visited.add(cause)
        if len(symptoms) < 3:
            continue
        k = randrange(1, len(symptoms) - 1)
        sample = choices(symptoms, k=k)
        sample = set(sample)
        symptom = choice(symptoms)
        while symptom in sample:
            symptom = choice(symptoms)
        sample = list(sample)
        shuffle(sample)
        probability = randrange(5, 51) / 100
        symptoms_relationship = f'"S {symptom.strip(chr(34))}", ({"; ".join(sample)}), {probability:.2f}'
        symptoms_dataset.append(symptoms_relationship)
        size -= 1
    return symptoms_dataset


def gen_csv(causes, symptoms_random, symptoms_deterministic):
    dataset = []
    dataset.extend(causes)
    dataset.extend(symptoms_random)
    dataset.extend(symptoms_deterministic)
    shuffle(dataset)
    with open('ThinkTaku_Dataset_formatted.csv', 'a') as file:
        for line in dataset:
            print(line, file=file)


def main():
    df = pd.read_excel('data/4_dataset_polished.xlsx')
    # empty = get_empty(df)
    # print(sum(len(empty[i]) for i in empty))
    df = df.dropna(subset=SUBSET, how='all')
    causes = gen_causes_dataset(df)
    # print(*causes, sep='\n')
    # print('')
    symptoms_random = gen_symptoms_dataset_random(causes, 5)
    # print(*symptoms_random, sep='\n')
    # print('')
    symptoms_deterministic = gen_symptoms_dataset_deterministic(causes, 25)
    # print(*symptoms_deterministic, sep='\n')
    # print('')
    gen_csv(causes, symptoms_random, symptoms_deterministic)


if __name__ == '__main__':
    main()
