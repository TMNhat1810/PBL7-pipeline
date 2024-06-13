import pandas as pd
from ..summarizer import get_summary

def get_new_data():
    all_data = pd.read_csv('data/news.csv')
    current = pd.read_csv('cache/current.csv')
    data = all_data.merge(current, how='left', on=['Date', 'Url', 'Title', 'Summary', 'Date', 'Categorical'], indicator=True)
    
    data = data[data['_merge'] == 'left_only'].reset_index()
    
    return data[['Title', 'Content', 'Summary', 'Date', 'Url', 'Categorical']]

def predict(_df: pd.DataFrame, version): 
    bp = _df[['Categorical', 'Date', 'Url', 'Title', 'Summary']].copy()

    bp['Pred'] = get_summary(_df['Content'].to_list(), version)
    bp = bp.assign(ModelVersion=version)
    
    return bp[['Categorical', 'Date', 'Url', 'Pred', 'Title', 'Summary', 'ModelVersion']]
