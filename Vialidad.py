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
    df = extract(2) # 1 for api, 2 for csv
    df = clean(df)
    analyze(df)
    #DE QUE FECHA A QUE FECHA?

def extract (source):
    if (source==1):
        city = 'guadalupe'
        limit = 100
        url = f'https://nuevoleon.opendatasoft.com/api/explore/v2.1/catalog/datasets/indices-de-estadisticas-de-accidentes-viales-{city}/records'
       
        response = requests.get(url, {'limit': limit}).json()
        df = pd.DataFrame(response['results'])
        
    if(source==2):
        df=pd.read_csv('indices-de-estadisticas-de-accidentes-viales-guadalupe.csv')
    
    return df

def clean (df):
    df = df.rename(columns=lambda x: x.strip())
    df = df.drop(['Folio', 'Ejercicio', 'Mes','Resolución','Origen_de_reporte', 'Nota'], axis = 1)
    
    print("Null Rows dropped: ", df.isna().any(axis=1).sum())
    df = df.dropna()
    
    print("Duplicated rows dropped: ",df.duplicated().sum())
    df = df.drop_duplicates()
    
    df['Dia'] = pd.to_datetime(df['Fecha']).dt.day_name(locale='es_MX')


    df['Tipo_de_accidente'] = cleanTypeOfAccidents(df)

    return df


def cleanTypeOfAccidents(df):
    print("Types of accidents", df['Tipo_de_accidente'].nunique())

    #DELETE ACCENTS
    df['Tipo_de_accidente'] = df['Tipo_de_accidente'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    #DELETE UNNECESARY DESCRIPTION
    df['Tipo_de_accidente'] = df['Tipo_de_accidente'].str.split(" SIN", n=1, expand = True)[0]

    #FORMATING TO SPLIT
    df['Tipo_de_accidente']= df['Tipo_de_accidente'].str.replace(' CON ', ' - ')
    df['Tipo_de_accidente']= df['Tipo_de_accidente'].str.replace(' Y ', ' - ')
    df['Tipo_de_accidente']= df['Tipo_de_accidente'].str.replace('DE ', '')

    #SPLIT TYPE AND SUBTYE
    dfTiposSplit = df['Tipo_de_accidente'].str.split(" -", n=1, expand = True)
    df['Tipo_de_accidente'] = dfTiposSplit[0]
    df['Subtipo_accidente'] = dfTiposSplit[1]

    '''
    WATCH ALL TYPES
    print( df['Tipo_de_accidente'].sort_values().value_counts(sort=True))
    '''
    print("Type of Accidents Clean ",df['Tipo_de_accidente'].nunique())
    return df['Tipo_de_accidente']

def analyze(df):
    print('\nCount of accidents by day:\n', df['Dia'].value_counts())
    print('\nMost Type of accidents:\n', df['Tipo_de_accidente'].value_counts().head(12))

    
def export(df):
    df.to_excel("output.xlsx") 


main()
