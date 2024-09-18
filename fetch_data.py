import os
from datetime import timedelta, datetime
from sec_edgar_downloader import Downloader as SECDownloader
import shelve as sh
import shutil
from html_reader import HtmlReader
from filings_reader import FilingsReader
from scraper import Scraper


class DataFetcher:
    def __init__(self, ticker = 'MSFT'):
        self.ticker = ticker
        self.secDir = "./secfilings"
        self.cache = "./cache"
        if not os.path.exists(self.secDir):
            os.makedirs(self.secDir)
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        #cache file
        self.cacheFile = os.path.join(self.cache, "cache.db")
        self.cacheExpiration = timedelta(days=1)
    

    def readContent(self, content, ticker, type, fileExtension):
        reader = FilingsReader()
        dictFilings = reader.parse_sec_filing(content)
        
        return reader.extract_10K_items(dictFilings, content)

    def downloadSecFiling(self, ticker, type, fileExtension = ".txt"):
        """
        Download the SEC filing (whose type, e.g. 10-K, is specified) for the given ticker
        !!!It only works with US companies!!!
        Args:
        ticker: str, the ticker of the company
        type: str, the type of the SEC filing to download
        fileExtension: str, the extension of the file to download (default is .txt), because the content is available either in .txt or .html
        Returns:
        res: dict, the response of the download
        """

        #at first, search it in the cache
        cacheKey = f"{ticker}_{type}"
        with sh.open(self.cacheFile) as db:
            if cacheKey in db:
                res = db[cacheKey]
                if res['timestamp'] + self.cacheExpiration > datetime.now():
                    #return HtmlReader().parse_sec_filing(res['content'])
                    return self.readContent(res['content'], ticker, type, fileExtension)
                
        #if not found in the cache, download it
        downloader = SECDownloader("Rpix17", "rpix17@info.com")

        #the filing will be automatically donwloaded to the path: '\sec-edgar-filings\{ticker}\{type}\{somecode}
        downloader.get(type, ticker, limit=1, download_details=True)

        # Get current directory full path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the filing
        default_pathName = "sec-edgar-filings"
        filing_path = os.path.join(current_dir, default_pathName, ticker, type)

        #example of filing path: R:\AInvest\sec-edgar-filings\MSFT\10-K

        #search for the newest folder in the filing path
        folders = [os.path.join(filing_path, d) for d in os.listdir(filing_path)]
        if not folders:
            return "No filing of type {} found for company {}".format(type, ticker)
        newest_folder = max(folders, key=os.path.getmtime)
        newest_folder_path = os.path.join(filing_path, newest_folder)

        newest_folder_files = os.listdir(newest_folder)

        #the filing is in the .html file, check for it
        html_files = [f for f in newest_folder_files if f.endswith(fileExtension)]
        if not html_files:
            return "No .htm file found in the folder {}".format(newest_folder)
        
        #example of filing: R:\AInvest\sec-edgar-filings\MSFT\10-K\0000950170-24-087843\primary-document.html
        filing = os.path.join(newest_folder_path, html_files[0]) 

        #extract the content of html file
        with open(filing, 'r', encoding='utf-8' ) as f:
            content = f.read()
            f.close()

        if content is None:
            return "No content found in the filing {}".format(filing)
        if content == "":
            return "Empty content found in the filing {}".format(filing)
        
        #remove the directory tree strating from the sec-edgar-filings
        #shutil.rmtree(os.path.join(current_dir, default_pathName), ignore_errors=True)

        #store the content in the cache
        res = {'content': content, 'timestamp': datetime.now()}
        with sh.open(self.cacheFile) as db:
            db[cacheKey] = res

        return self.readContent(content, ticker, type, fileExtension)
    
    
    def get_yahoo_analysis(self, ticker):
        """
        Function that get the Yahoo analysis for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: dict, the response of the download
        """
        cacheKey = f"{ticker}_yahoo_analysis"
        with sh.open(self.cacheFile) as db:
            if cacheKey in db:
                res = db[cacheKey]
                if res['timestamp'] + self.cacheExpiration > datetime.now():
                    return res['content']


        dict = Scraper(ticker).get_yahoo_analysis()

        #store the content in the cache
        res = {'content': dict, 'timestamp': datetime.now()}
        with sh.open(self.cacheFile) as db:
            db[cacheKey] = res

        return dict


        

    def get_estimates(self, ticker):
        """
        Function that get the Yahoo estimates for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: dict, the response of the download
        """
        dict = self.get_yahoo_analysis(ticker)

        #get the keys: Earnings Estimate, Revenue Estimate, Growth Estimates
        #get just the sub-dictionary with the estimates
        return {k: dict[k] for k in dict.keys() & {'Earnings Estimate', 'Revenue Estimate', 'Growth Estimates', 'EPS Revisions'}}
    
    def get_top_analysts(self, ticker):
        """
        Function that get the Yahoo top analysts for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: dict, the response of the download
        """
        dict = self.get_yahoo_analysis(ticker)

        #get the key: Top Analysts
        return dict['Top Analysts']

                    
                


    def get10k_1A(self, ticker):
        """
        Get the Item 1A of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_1a']
    
    def get10k_5(self, ticker):
        """
        Get the Item 5 of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_5']

    def get10k_6(self, ticker):
        """
        Get the Item 6 of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_6']

    def get10k_7(self, ticker):
        """
        Get the Item 7 of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_7']
    
    def get10k_7A(self, ticker):
        """
        Get the Item 7A of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_7a']
    
    def get10k_8(self, ticker):
        """
        Get the Item 8 of the 10-K filing for the given ticker
        Args:
        ticker: str, the ticker of the company
        Returns:
        res: str, the response of the download
        """
        items = self.downloadSecFiling(ticker, "10-K")
        return items['item_8']


        
    

if __name__ == "__main__":
    fetcher = DataFetcher()
    print("Fetching data...")
    #res = fetcher.downloadSecFiling("GOOG", "10-K")
    res = fetcher.get_estimates("MSFT")
    #print(res)
    with open("output.txt", "w", encoding='utf-8') as f:
        f.write(str(res))
        f.close()

    #FilingsReader().extract_10K_items(res, content)
