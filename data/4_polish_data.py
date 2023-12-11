import pandas as pd


def main():
    df = pd.read_excel('data/dataset_filledNA.xlsx')
    to_replace_gender = {
        'Female': 'Sexo feminino',
        'Male': 'Sexo masculino',
    }
    genders = list(to_replace_gender.keys()) + list(to_replace_gender.values())
    to_replace_age = {
        'Child': 'Idade aparente: Criança',
        'Teen': 'Idade aparente: Adolescente',
        'Adult': 'Idade aparente: Adulto',
        'Senior': 'Idade aparente: Senhor',
    }
    ages = list(to_replace_age.keys()) + list(to_replace_gender.values())
    to_replace_hair_length = {
        'No Hair': 'Careca',
        'To Neck': 'Cabelo até o pescoço',
        'To Ears': 'Cabelo até as orelhas',
        'To Shoulders': 'Cabelo até os ombros',
        'To Chest': 'Cabelo até as costas',
        'To Waist': 'Cabelo até a cintura',
        'Hip / Past Hip': 'Cabelo até a cintura ou abaixo',
    }
    lengths = list(to_replace_hair_length.keys()) + list(to_replace_hair_length.values())
    df.loc[~df['Gender'].isin(genders), 'Gender'] = pd.NA
    df.loc[~df['Apparent Age'].isin(ages), 'Apparent Age'] = pd.NA
    df.loc[~df['Hair Length'].isin(lengths), 'Hair Length'] = pd.NA
    for gender in to_replace_gender:
        df.loc[df['Gender'] == gender, 'Gender'] = to_replace_gender[gender]
    for age in to_replace_age:
        df.loc[df['Apparent Age'] == age, 'Apparent Age'] = to_replace_age[age]
    for hair in to_replace_hair_length:
        df.loc[df['Hair Length'] == hair, 'Hair Length'] = to_replace_hair_length[hair]
    df = df.rename(
        columns={'Gender': 'Gênero biológico', 'Apparent Age': 'Idade aparente', 'Hair Length': 'Comprimento do cabelo'}
    )
    df = df.drop([df.columns[0], df.columns[1]], axis=1)
    df.to_excel('data/dataset_polished.xlsx', index=False)


if __name__ == '__main__':
    main()