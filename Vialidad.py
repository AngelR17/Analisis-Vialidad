# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 13:52:24 2023

@author: angel
"""

import requests
import pandas as pd

def main():
    df = extract(2) # 1 for api, 2 for csv
    df = clean(df)
    analyze(df)
    #DE QUE FECHA A QUE FECHA?

def extract (source):
    if (1):
        city = 'guadalupe'
        limit = 100
        url = f'https://nuevoleon.opendatasoft.com/api/explore/v2.1/catalog/datasets/indices-de-estadisticas-de-accidentes-viales-{city}/records'
       
        response = requests.get(url, {'limit': limit}).json()
        df = pd.DataFrame(response['results'])
        
    if(2):
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

    return df

def analyze(df):
    print('Count of accidents by day:\n', df['Dia'].value_counts())
    
def export(df):
    df.to_excel("output.xlsx") 


main()

    