import requests 
from bs4 import BeautifulSoup as bs
import json
import shelve as sh

class Scraper:
    def __init__(self, ticker):
        self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
        }
        self.ticker = ticker
        self.yahoo_analysis_url =f'https://finance.yahoo.com/quote/MSFT/analysis?p={ticker}'
    
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

if __name__ == "__main__":
    scraper = Scraper("MSFT")
    print(scraper.get_yahoo_analysis())