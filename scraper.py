import requests 
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import json
import shelve as sh
from text_summary import summarize_text

class Scraper:
    def __init__(self, ticker):
        self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
        }
        self.ticker = ticker.upper()
        self.yahoo_analysis_url =f'https://finance.yahoo.com/quote/MSFT/analysis?p={self.ticker}'
        self.news_url1 = f'https://stockmarketcap.com/company/{self.ticker}#news'
        self.news_url2 = f'https://finviz.com/quote.ashx?t={self.ticker}'
        self.news_url3 = f'https://finance.yahoo.com/quote/{self.ticker}/news/'
    
    def use_playwright(self, url):
        """
        function to use playwright to scrape the data from the website
        """

        #use playwrioht to scrape the news, as the website uses javascript to load the news
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            content = page.content()
            browser.close()


        return content
    
    async def use_playwright2(self, url):
        """
        function to use playwright to scrape the data from the website
        Advanced for cookie button click
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Imposta headless=False per vedere il browser
            page = await browser.new_page()
        
            # Vai alla pagina desiderata
            await page.goto(url)  # Cambia con il link corretto
        
            # Cerca e accetta il consenso ai cookie, se presente
            try:
                await page.click("button[name='agree']")
            except:
                print("Nessun consenso richiesto o non trovato.")
        
            # Aspetta che la pagina sia completamente caricata
            await page.wait_for_selector("h1")  # Esempio: aspetta che l'header della pagina sia visibile
            
            # Scarica l'HTML della pagina
            html_content = await page.content()
        
            await browser.close()

            return html_content


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
        news = ""

        data = []

        req = requests.get(self.news_url2, headers=self.headers)
        if req.status_code == 200:
            news = req.content
        else:
            return "No news found"
        
        html = bs(news, 'html5lib')
        news_table = html.find('table', id='news-table')
        if not news_table:
            news_table = html.find('table', class_='fullview-news-outer news-table')
        if not news_table:
            return "No news found"
        
        for i, table_row in enumerate(news_table.find_all('tr')):
            # Read the text of the element 'a' into 'link_text'
            data.append(table_row.a.text)

        return data
        

    def get_news1(self):
        """
        function to scrape news from the first source
        Returns:
        news: dict, the news data
        """

        news = ""
        #use playwrioht to scrape the news, as the website uses javascript to load the news
        news = self.use_playwright(self.news_url1)

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
    
    def get_news2(self):
        """
        function to scrape news from Yahoo Finance news section
        Returns:
        news: dict, the news data
        """

        to_delete = "Tip: Try a valid symbol or a specific company name for relevant results"

        data = []

        #use playwrioht to scrape the news, as the website uses javascript to load the news
        news = asyncio.run(self.use_playwright2(self.news_url3))

        if not news:
            return "No news found 1"
        
        html = bs(news, 'html5lib')

        #save the html in output.txt
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(str(html))

        news_table = html.find('div', class_='news-stream')
        if not news_table:
            news_table = html.find('div', class_='news-stream  yf-17l7f4i')
        if not news_table:  
            news_table = html.find(attrs={"data-testid": "news-stream"})
        
        if not news_table:
            return "No news found 2"

        #find all the <li> elements in the news_table
        news_list = news_table.find_all('section', class_='container')
        
        #inside every <li> element, the title of the news is in the <h3> tag, the text in the <p> tag
        inside = ""
        i = 0
        limit = 2
        for news in news_list:
            content_class = news.find('div', class_='content')
            link = content_class.find('a')['href']
            title = news.find('h3').get_text(strip=True)
            text = news.find('p').get_text(strip=True)

            if i < limit:
                try:
                    inside = asyncio.run(self.use_playwright2(link))
                    soup = bs(inside, 'html5lib')
                    #take alle the <p> elements in the article
                    paragraphs = soup.find_all('p')
                    text = ""
                    for p in paragraphs:
                        text += p.get_text(strip=True) + " "
                    
                    #summarize the text
                    summary = summarize_text(text)
                except:
                    summary = text
                finally:
                    if summary is None or len(summary) < 10:
                        summary = text
                    data.append({title: summary.replace(to_delete, "")})
                    i += 1
            data.append({title: text})
            #data.append({title: text})


        return data

if __name__ == "__main__":
    scraper = Scraper("CPR.MI")
    print(scraper.get_news2())