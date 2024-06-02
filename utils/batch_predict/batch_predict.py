import pandas as pd
from ..summarizer import get_summary

def get_new_data():
    all_data = pd.read_csv('data/news.csv')
    current = pd.read_csv('cache/current.csv')
    data = all_data.merge(current, how='left', on=['Date', 'Url'], indicator=True)
    
    data = data[data['_merge'] == 'left_only'].reset_index()
    
    return data[['Title', 'Content', 'Summary', 'Date', 'Url', 'Categorical_x']].rename(columns={'Categorical_x': 'Categorical'})

def predict(_df: pd.DataFrame): 
    bp = _df[['Categorical', 'Date', 'Url']].copy()
    # bp['Pred'] = df['Content'].apply(summarizer_wrapper)
    bp['Pred'] = get_summary(_df['Content'].to_list())
    
    return bp
