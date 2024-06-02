import numpy as np
import pandas as pd
import os
import psycopg2 

connection = psycopg2.connect(database='postgres',
                              user='postgres',
                              password='123456a@A',
                              host='localhost',
                              port='5432',
                              options="-c search_path=pbl7,public")

def get_categories():
    cur = connection.cursor()
    cur.execute('select * from "PBL7".category')
    categories = cur.fetchall()
    
    return categories

categories = get_categories()

def getCategoryId(name):
    for category in categories:
        if category[1] == name: return category[0]
    
    return ''

def convert_category(category: str):
    if category == 'economic': 
        return getCategoryId('Kinh tế')
    if category == 'social':
        return getCategoryId('Xã hội')
    
    return getCategoryId(category)

def convert_date(date: str):
    [dd, mm, yyyy] = date.split('/')
    return '-'.join([yyyy, mm, dd])

def apply_convert(_df: pd.DataFrame):
    df = _df.copy()
    df['Categorical'] = df['Categorical'].apply(convert_category)
    df['Date'] = df['Date'].apply(convert_date)
    return df.reset_index().drop(columns='index', axis=1)

def import_db(data: pd.DataFrame):
    
    path_to_csv = os.path.abspath('cache/import.csv')

    data.to_csv('cache/import.csv', index=False)

    cur = connection.cursor()

    cur.execute('''
                COPY "PBL7".news("categoryId", "Date", "url", "summary", "id") 
                FROM '{}'
                DELIMITER ','
                CSV HEADER;
                '''.format(path_to_csv))
    
    connection.commit()
    cur.close()

def back_up_data(data: pd.DataFrame):
    data.to_csv('cache/current.csv', index=False, header=False, mode='a')
