from .crawl import vtv_crawl, tuoitre_crawl, merge_data
from .batch_predict import get_new_data, predict
from .import_db import apply_convert, import_db, back_up_data

import datetime
import uuid

def start_pipeline(crawl_until_date: datetime.date, using_version: str):
    vtv_crawl('social', crawl_until_date)
    vtv_crawl('eco', crawl_until_date)
    tuoitre_crawl()
    merge_data()
    print('crawl completed, process to batch predict')
    
    new_data = get_new_data()
    preds = predict(new_data, using_version)
    print('batch predict completed, importing data to db')
    
    import_data = apply_convert(preds)
    import_data['id'] = [str(uuid.uuid4()) for _ in range(len(import_data))]
    import_db(import_data)
    back_up_data(preds)
    print('done. terminating')