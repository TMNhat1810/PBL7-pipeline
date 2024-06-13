import pandas as pd
import os
import datetime
import uuid
from ...service.database import connection

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

def convert_datetime(datetime: str):
    [d, t, _] = datetime.split(' ')
    [dd, mm, yyyy] = d.split('/')
    return '-'.join([yyyy, mm, dd]) + ' ' + t + ':00'

def apply_convert(_df: pd.DataFrame):
    df = _df.copy()
    df['Categorical'] = df['Categorical'].apply(convert_category)
    df['Date'] = df['Date'].apply(convert_datetime)
    return df.reset_index().drop(columns='index', axis=1)

def import_db(data: pd.DataFrame):
    if len(data) == 0: return
    
    path_to_csv = os.path.abspath('cache/import.csv')

    data.to_csv('cache/import.csv', index=False)

    cur = connection.cursor()
    
    # try:
    cur.execute('''
                COPY "PBL7".news("categoryId", "date", "url", "summary", "title", "orgSummary", "modelVersion", "id") 
                FROM '{}'
                DELIMITER ','
                CSV HEADER;
                '''.format(path_to_csv))
    
    connection.commit()
    # except: pass
    
    cur.close()

def back_up_data(data: pd.DataFrame):
    data.to_csv('cache/current.csv', index=False, header=False, mode='a')

def get_version_data():
    version_data = []

    for version in os.listdir('model'):
        evaluate = pd.read_csv('model/' + version + '/evaluate.csv')
        evaluate['version'] = version
        evaluate['date'] = datetime.datetime.now()
        version_data.append(evaluate)
        
    version_data = pd.concat(version_data, axis=0)[['version', 'date', 'rouge1', 'rouge2', 'rougeL']]
    current = pd.read_csv('cache/version_data.csv')['version']
    version_data = version_data.merge(current, how='left', on=['version'], indicator=True)
    version_data = version_data[version_data['_merge'] == 'left_only'].reset_index()
    version_data['id'] = [str(uuid.uuid4()) for _ in range(len(version_data))]
        
    return version_data[['version', 'date', 'rouge1', 'rouge2', 'rougeL', 'id']]

def import_version_data(data: pd.DataFrame):
    if len(data) == 0: return
    
    data.to_csv('cache/version_import.csv', index=False)
    
    path_to_csv = os.path.abspath('cache/version_import.csv')

    cur = connection.cursor()

    # try: 
    cur.execute('''
            COPY "PBL7".model_version("name", "date", "rouge1", "rouge2", "rougeL", "id") 
            FROM '{}'
            DELIMITER ','
            CSV HEADER;
            '''.format(path_to_csv))

    connection.commit()
    data.to_csv('cache/version_data.csv', index=False, header=False, mode='a')
        
    # except: pass
    
    cur.close()
    
def get_feedbacks_data():
    cur = connection.cursor()
    
    cur.execute('''
                SELECT feedback.content, news.url, news.title FROM "PBL7".feedback INNER JOIN "PBL7".news
                ON feedback."newsId"=news.id
                WHERE feedback.status='APPROVED'
                ORDER BY feedback."createdAt" ASC 
                ''')
    
    data = cur.fetchall()
    
    cur.close()
    return data

def export_feedback_data():
    data = get_feedbacks_data()
    feedbacks = []
    urls = []
    titles = []

    for fb in data:
        feedback_content, url, title = fb
        feedbacks.append(feedback_content)
        urls.append(url)
        titles.append(title)
    
    df = pd.DataFrame({'Summary': feedbacks, 'Url': urls, 'Title': titles})
    all_data = pd.read_csv('data/news.csv')
    export_data = df.merge(all_data, on=['Title', 'Url']).drop(columns='Summary_y')
    export_data = export_data.dropna().drop_duplicates()
    export_data.rename(columns={'Summary_x': 'Summary'}, inplace=True)
    export_data[['Title', 'Content', 'Summary', 'Date', 'Url', 'Categorical']].to_csv(
        'data/feedback' + datetime.datetime.now().strftime('_%m-%d-%Y_%H-%M-%S') + '.csv', index=False)