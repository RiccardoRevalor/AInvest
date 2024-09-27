import requests

ap_key = "3PSIFTJTLFUHVTCT" #"demo"


def getNewsSentiment(ticker):
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ap_key}'
    r = requests.get(url)

    #for each article in the feed, delete url, authors e time_published
    r = r.json()
    items = r['feed']
    for i in items:
        if 'url' in i.keys(): del i['url']
        if 'authors' in i.keys(): del i['authors']
        if 'time_published' in i.keys(): del i['time_published']
        if 'banner_image' in i.keys(): del i['banner_image']
        if 'source' in i.keys(): del i['source']
        if 'banner_image' in i.keys(): del i['banner_image']
        if 'category_within_source' in i.keys(): del i['category_within_source']
        if 'source_domain' in i.keys(): del i['source_domain']
        #if other tickers appears in ticker_sentiment, delete them
        if 'ticker_sentiment' in i.keys():
            i['ticker_sentiment'] = [j for j in i['ticker_sentiment'] if j['ticker'].upper() == ticker.upper()]

    instr = r['sentiment_score_definition'] + r['relevance_score_definition']
    return items, instr

if __name__ == '__main__':
    print(getNewsSentiment('AAPL'))
