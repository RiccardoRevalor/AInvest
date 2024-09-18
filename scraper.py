import requests 
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
import json
import shelve as sh

class Scraper:
    def __init__(self, ticker):
        self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
        }
        self.ticker = ticker.upper()
        self.yahoo_analysis_url =f'https://finance.yahoo.com/quote/MSFT/analysis?p={self.ticker}'
        self.news_url1 = f'https://stockmarketcap.com/company/{self.ticker}#news'
    
    def get_yahoo_analysis(self):
        items = ["Earnings Estimate", "Revenue Estimate", "Earnings History", "EPS Trend", "EPS Revisions", "Growth Estimates","Top Analysts", "Upgrades & Downgrades"]
        soup = bs(requests.get(self.yahoo_analysis_url , headers=self.headers).content, "html5lib")
        i = 0
        dict = {}
        for table in soup.select("table"):
            category = items[i]
            dict[category] = []
            th_row = [th.text.strip() for th in table.find_all("th")]

            for j in range(1, len(th_row)):
                dict[category].append({th_row[j]: {}})

            #print(th_row)
            i1 = 0
            for tr in table.select("tr:has(td)"):
                td_row = [td.text.strip() for td in tr.find_all("td")]
                subtitle = td_row[0]
                for j in range(len(dict[category])):
                    k = list(dict[category][j].keys())[0]
                    dict[category][j][k][subtitle] = td_row[j+1]
                #print(td_row)
                # Combine headers and data into a dictionary for this row
                #row_data = {th_row[j]: td_row[j] for j in range(len(td_row))}
                #dict[category].append(row_data)
            
            i += 1

            #print()
        
        #return the json data
        return dict
        #return json.dumps(dict, indent=4)


    def get_finviz_news(self):
        pass

    def get_news1(self):
        """
        function to scrape news from the first source
        Returns:
        news: dict, the news data
        """

        news = ""
        #use playwrioht to scrape the news, as the website uses javascript to load the news
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.news_url1)
            page.wait_for_load_state("networkidle")
            news = page.content()
            browser.close()

        if not news:
            return "No news found"
        
        data = []

        #extract all the text from the HTML elements with the class 'text-md' and in a paragraph 'p'
        soup = bs(news, 'html5lib')
        with open('soup.html', 'w', encoding='utf-8') as f:
            f.write(str(news))
        scroll_section = soup.find('div', class_='infinite-scroll-component')
        if not scroll_section:
            scroll_section = soup.find('div', id='headlessui-tabs-panel-:ri:')
            
        #the title of the news are the keys in the dictionary, the values are the text of the news
        #the title is stored in the h3 tag, the text in the p tag
        if scroll_section:
            # Trova tutti i <h3> e <p> all'interno di scroll_section
            titles = scroll_section.find_all('h3') #titles of the news
            texts = scroll_section.find_all('p') #body of the news

            # Associa ogni titolo al testo corrispondente
            for title, text in zip(titles, texts):
                data.append({title.get_text(strip=True): text.get_text(strip=True)})
        else: 
            print("No news found")
        


        #return the data
        return data

if __name__ == "__main__":
    scraper = Scraper("MSFT")
    print(scraper.get_news1())