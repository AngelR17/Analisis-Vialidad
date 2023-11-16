# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 13:52:24 2023

@author: angel
"""

import requests
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option("display.max_rows", None)


def main():
    df = extract(2)  # 1 for api, 2 for csv
    df = clean(df)
    analyze(df)
    # DE QUE FECHA A QUE FECHA?


def extract(source):
    df = pd.DataFrame()
    if source == 1:
        city = 'guadalupe'
        limit = 100
        url = f'https://nuevoleon.opendatasoft.com/api/explore/v2.1/catalog/datasets/indices-de-estadisticas-de-accidentes-viales-{city}/records'

        response = requests.get(url, {'limit': limit}).json()
        df = pd.json_normalize(response['results'])

    if source == 2:
        df = pd.read_csv('indices-de-estadisticas-de-accidentes-viales-guadalupe.csv')

    return df


def clean(df):
    df = df.rename(columns=lambda x: x.strip())

    df.columns = df.columns.str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df = df.drop(['folio', 'ejercicio', 'mes', 'resolucion', 'origen_de_reporte', 'nota'], axis=1)

    print("Null Rows dropped: ", df.isna().any(axis=1).sum())
    df = df.dropna()

    print("Duplicated rows dropped: ", df.duplicated().sum())
    df = df.drop_duplicates()

    df['dia'] = pd.to_datetime(df['fecha']).dt.day_name(locale='es_MX')

    df['tipo_de_accidente'] = clean_types(df)

    return df


def clean_types(df):
    print("Types of accidents", df['tipo_de_accidente'].nunique())

    # DELETE ACCENTS
    df['tipo_de_accidente'] = df['tipo_de_accidente'].str.normalize('NFKD').str.encode('ascii',
                                                                                       errors='ignore').str.decode(
        'utf-8')

    # FORMATING TO SPLIT
    df['tipo_de_accidente'] = df['tipo_de_accidente'].replace([' Y ', ' CON ', '/'], ' - ', regex=True)
    df['tipo_de_accidente'] = df['tipo_de_accidente'].replace(
        ['DE ', 'CON ', 'DOBLE', 'MULTIPLE', r'\d+', r'\ SIN(.*)'], '', regex=True)

    # SPLIT TYPE AND SUBTYE
    df_types_split = df['tipo_de_accidente'].str.split(" -", n=1, expand=True)
    df['tipo_de_accidente'] = df_types_split[0]
    df['subtipo_accidente'] = df_types_split[1]

    # Grammar Correction
    var_estrellamiento = ['ESTRELLMIENTO', 'ESTRELLAMIETO', 'ESTRELLAMIENO']
    var_alcance = ['ALCANSE']
    var_lateral = ['LATARAL', 'LARETAL']
    df['tipo_de_accidente'] = df['tipo_de_accidente'].replace(var_estrellamiento, "ESTRELLAMIENTO")
    df['tipo_de_accidente'] = df['tipo_de_accidente'].replace(var_alcance, "ALCANCE")
    df['tipo_de_accidente'] = df['tipo_de_accidente'].replace(var_lateral, "LATERAL")
    df['tipo_de_accidente'] = df['tipo_de_accidente'].str.strip()

    print(df['tipo_de_accidente'].sort_values().value_counts(sort=True))

    print("Type of Accidents Clean ", df['tipo_de_accidente'].nunique())
    return df['tipo_de_accidente']


def analyze(df):
    print('\nCount of accidents by day:\n', df['dia'].value_counts())
    print('\nMost Type of accidents:\n', df['tipo_de_accidente'].value_counts().head(12))


def export(df):
    df.to_excel("output.xlsx")


main()
