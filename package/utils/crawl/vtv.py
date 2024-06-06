from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd

import time
import datetime

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('headless')

locales = {
    'eco': ['https://vtv.vn/kinh-te.htm', 'cache/links_eco.csv', 'data/vtv/vtv_eco_raw.csv'],
    'social': ['https://vtv.vn/xa-hoi.htm', 'cache/links_social.csv', 'data/vtv/vtv_social_raw.csv']
}


def extract_summary(text_: str):
    text = text_[:]
    text = text.split(' - ')
    text.pop(0)
    text = ' '.join(text)
    return text

def get_link_until_date(url, date: datetime.date, sleep_interval):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.find_element(by=By.CLASS_NAME, value='loadmore').click()
        time.sleep(sleep_interval)
        upto_date = driver.find_elements(by=By.CLASS_NAME, value='tlitem')[-2].find_element(by=By.CLASS_NAME, value='time').text
        [dd, mm, yyyy] = upto_date.split('/')
        dd = int(dd)
        mm = int(mm)
        yyyy = int(yyyy)
        if date > datetime.date(yyyy, mm, dd): 
            elements = driver.find_elements(by=By.CLASS_NAME, value='tlitem')
            for element in elements[::-1]:
                try:
                    e_date = element.find_element(by=By.CLASS_NAME, value='time').text
                    [day, month, year] = e_date.split('/')
                    day, month, year = int(day), int(month), int(year)
                    if datetime.date(year, month, day) < date:
                        elements.remove(element)
                    else: 
                        break
                except: elements.remove(element)
            break
    
    links = []
    dates = []
    summaries = []
    for element in elements:
        try:
            link = element.find_elements(by=By.TAG_NAME, value='a')[0].get_attribute('href')
            date = element.find_element(by=By.CLASS_NAME, value='time').text
            summary = extract_summary(element.find_element(by=By.CLASS_NAME, value='sapo').text)
            links.append(link)
            dates.append(date)
            summaries.append(summary)
        except: pass
    
    return pd.DataFrame({'link': links, 'date': dates, 'summary': summaries})

def from_links_to_raw_data(df, loading_interval=3):
    links = df['link'].values
    summaries = df['summary'].values
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'setTimeout(function(){window.stop();}, 4000);'})
    titles = []
    contents = []
    datetimes = []
    for url in links:
        driver.get(url)
        time.sleep(loading_interval)
        
        driver.execute_script("""
            var element = document.querySelector(".VCSortableInPreviewMode");
            if (element)
                element.parentNode.removeChild(element);
            """)
        
        try:
            content = driver.find_element(by=By.CLASS_NAME, value='noidung')
            datetime_text = content.find_element(by=By.CLASS_NAME, value='time').text
            dt = datetime_text.split('ngày ')[1]
            title = content.find_element(by=By.CSS_SELECTOR, value='h1.title_detail').text
            paragraphs = content.find_elements(by=By.CSS_SELECTOR, value='#entry-body p')
            try:
                text = [content.find_element(by=By.CSS_SELECTOR, value='h2.sapo').text.split(' - ')[1]]
            except: text = []
            for paragraph in paragraphs:
                text.append(paragraph.text)
            titles.append(title)
            contents.append(" ".join(text))
            datetimes.append(dt)
        except:
            contents.append(None)
            titles.append(None)
    
    return pd.DataFrame({'title': titles, 'content': contents, 'summary': summaries, 'date': datetimes, 'url': links})

def add_to_data(df: pd.DataFrame, path, reset=False):
    if reset == True: df.to_csv(path, index=False)
    else: df.to_csv(path, mode='a', header=False, index=False)
    
def vtv_crawl(categorical, date):
    [url, link_path, raw_data_path] = locales[categorical]
    current_url = pd.read_csv(link_path)
    url_df = get_link_until_date(url, date, 3)
    url_df = url_df.merge(current_url, on=['link', 'date', 'summary'], how='left', indicator=True)
    url_df = url_df[url_df['_merge'] == 'left_only'].drop('_merge', axis=1)
    if len(url_df) == 0: return
    df = from_links_to_raw_data(url_df)
    url_df.to_csv(link_path, index=False, header=False, mode='a')
    add_to_data(df, reset=False, path=raw_data_path)
    
def crawl_from_link(categorical):
    [_, link_path, raw_data_path] = locales[categorical]
    url_df = pd.read_csv(link_path)
    df = from_links_to_raw_data(url_df)
    add_to_data(df, reset=False, path=raw_data_path)

def vtv_merge():
    eco_data = pd.read_csv(locales['eco'][2])
    social_data = pd.read_csv(locales['social'][2])
    
    eco_data = eco_data.assign(categorical='economic')
    social_data = social_data.assign(categorical='social')
    
    merge_data = pd.concat([eco_data, social_data], axis=0)
    merge_data.rename(columns={
        'title': 'Title',
        'content': 'Content',
        'summary': 'Summary',
        'date': 'Date',
        'url': 'Url',
        'categorical': 'Categorical'
    }, inplace=True)
    
    merge_data.dropna(inplace=True)
    merge_data.drop_duplicates(inplace=True)
    merge_data.to_csv('data/vtv/vtv_news.csv', index=False)
    
    return merge_data