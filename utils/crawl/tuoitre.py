import os
import pandas as pd
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By

class FileHandler():
    @staticmethod
    def is_file_empty(file_name: str) -> bool:
        """Return True if file is empty

        Args: 
            - file_name: file's name that is needed to be check
        """
        try:
            return os.stat(file_name).st_size == 0
        except(FileNotFoundError):
            return True


    @staticmethod
    def write_to_csv(rows: list, file_name: str) -> None:
        header = ['Title', 'Content', 'Date', 'Url', 'Summary']
        data = pd.DataFrame(rows, index=None, columns=header)

        if FileHandler.is_file_empty(file_name):
            # remove unname cols
            data.drop(data.filter(regex="Unname"), axis=1, inplace=True)
            # drop duplicate rows
            data.drop_duplicates(inplace=True)
            data.to_csv(file_name, index=False)
        else:
            existed_data = pd.read_csv(file_name)
            # outer join
            merged_data = pd.merge(data, existed_data, how='outer').sort_values(by='Date', axis=0, ascending=False)
            # remove unname cols
            merged_data.drop(merged_data.filter(regex="Unname"), axis=1, inplace=True)
            # drop duplicate rows
            merged_data.drop_duplicates(inplace=True)
            merged_data.to_csv(file_name, index=False)
            
class BrowserOption(Enum):
    """Option for webbrowser
    """
    EDGE = 1
    CHROME = 2
    FIREFOX = 3
    SAFARI = 4

class TuoiTre_Crawler:
    @staticmethod
    def get_driver(browser_option: BrowserOption = BrowserOption.EDGE):
        """Return driver depended on BrowserOption Enuml
        
        Args:
            - browser_option: the option of browser's driver
        """
        if browser_option == BrowserOption.EDGE:
            options = webdriver.EdgeOptions()
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            return webdriver.ChromiumEdge(options=options)
        elif browser_option == BrowserOption.FIREFOX:
            return webdriver.Firefox()
        elif browser_option == BrowserOption.SAFARI:
            return webdriver.Safari()       
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            return webdriver.Chrome(options=options)  
        
    def __init__(self, browser_option: BrowserOption, folder_to_save: str, category_url: dict) -> None:
        """Create a new instance of crawler
        
        Args:
            - browser_option: the option of browser's driver
            - folder_to_save: folder to save data crawled
            - category_url: a dictionary which key=filename, value=category url
        """
        self.driver = TuoiTre_Crawler.get_driver(browser_option)
        # self.url_file = url_file
        self.folder_to_save = folder_to_save
        self.category_url = category_url

    def crawl(self, url: str):
        """Crawl data from single url
        
        Args:
            - url: a news url
        """
        self.driver.get(url)

        title_selector = "#main-detail > .article-title"
        contents_selector = "div.detail-content.afcbc-body > :not(.VCSortableInPreviewMode, #InreadPc)"
        date_selector = "#main-detail > div.detail-top > div.detail-time"
        summary_selector = "#main-detail > .detail-sapo"
        
        title = self.driver.find_element(By.CSS_SELECTOR, title_selector)
        contents = self.driver.find_elements(By.CSS_SELECTOR, contents_selector)
        date = self.driver.find_element(By.CSS_SELECTOR, date_selector)
        summary = self.driver.find_element(By.CSS_SELECTOR, summary_selector)

        title = title.text.split('\n')[0]
        joined_content = " ".join(x.text for x in contents)
        return (title, joined_content, date.text, summary.text)

    def news_from_category(self, filename: str, url: str):
        """Get news URL from category page
        
        Args:
            - filename: file to save data
            - url: a category page url
        """
        self.driver.get(url)

        focus_main_selector = "div.list__focus-main a.box-category-link-title"
        focus_main = self.driver.find_elements(By.CSS_SELECTOR, focus_main_selector)
        news_urls = [url.get_property('href') for url in focus_main]

        # listing_main_selector = "div.list__listing-main a.box-category-link-title"
        # listing_main = self.driver.find_elements(By.CSS_SELECTOR, listing_main_selector)
        # news_urls.extend([url.get_property('href') for url in listing_main])
        
        rows = []
        for news_url in news_urls:
            try:
                (title, joined_content, date, summary) = self.crawl(news_url)
                rows.append([title, joined_content, date, news_url, summary])
            except:
                continue
        
        FileHandler.write_to_csv(rows, os.path.join(self.folder_to_save, filename))
        print("Crawled", len(rows), "from", url)
        return len(rows)

    def start_crawl(self):
        count = 0
        for file, url in self.category_url.items():
            count += self.news_from_category(file, url)

        print("Done! Crawled", count)
        self.driver.quit()

    def data_summary(self, verbose=False):
        header = ['Title', 'Content', 'Date', 'Url', 'Summary']
        total = pd.DataFrame(columns=header)
        for file, url in self.category_url.items():
            data = pd.read_csv(os.path.join(self.folder_to_save, file))
            total = pd.merge(data, total, how='outer')
            print('Data:', file)
            print(data.info(verbose=verbose))
            print('=====================================')
        print('Total:')
        print(total.info(verbose=verbose))
        
def tuoitre_crawl():
    category_url = {
        "tuoitre_kinhdoanh.csv": "https://tuoitre.vn/kinh-doanh.htm",
        "tuoitre_congnghe.csv": "https://tuoitre.vn/cong-nghe.htm",
        "tuoitre_dulich.csv": "https://tuoitre.vn/du-lich.htm",
        "tuoitre_vanhoa.csv": "https://tuoitre.vn/van-hoa.htm",
        "tuoitre_giaitri.csv": "https://tuoitre.vn/giai-tri.htm",
        "tuoitre_thethao.csv": "https://tuoitre.vn/the-thao.htm",
        "tuoitre_giaoduc.csv": "https://tuoitre.vn/giao-duc.htm"
    }

    crawler = TuoiTre_Crawler(BrowserOption.CHROME, folder_to_save='./data/tuoitre', category_url=category_url)
    crawler.start_crawl()
    
def tuoitre_merge():
    category_name = {
        "tuoitre_kinhdoanh.csv": "Kinh doanh",
        "tuoitre_congnghe.csv": "Công nghệ",
        "tuoitre_dulich.csv": "Du lịch",
        "tuoitre_vanhoa.csv": "Văn hóa",
        "tuoitre_giaitri.csv": "Giải trí",
        "tuoitre_thethao.csv": "Thể thao",
        "tuoitre_giaoduc.csv": "Giáo dục"
    }
    dfs = []
    for file, name in category_name.items():
        df = pd.read_csv('data/tuoitre/' + file)
        df = df.assign(Categorical=name)
        dfs.append(df)
        
    merge_data = pd.concat(dfs, axis=0)
    merge_data.dropna(inplace=True)
    merge_data.drop_duplicates()
    merge_data.to_csv('data/tuoitre/tuoitre_news.csv', index=False)
    
    return merge_data