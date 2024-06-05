import pandas as pd
from .vtv import vtv_crawl,  vtv_merge
from .tuoitre import tuoitre_crawl, tuoitre_merge

def merge_data():
    vtv_news = vtv_merge()
    tuoitre_news = tuoitre_merge()
    
    pd.concat([vtv_news, tuoitre_news], axis=0).to_csv('data/news.csv', index=False)
    