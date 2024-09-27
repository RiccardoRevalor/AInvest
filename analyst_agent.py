import llm
from fetch_data import DataFetcher
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ap_api import getNewsSentiment
from random import randint

class AnalystAgent:
    def __init__(self, ticker, localmodel=False):
        self.ticker = ticker
        self.model = "llama3-8b-8192"
        self.localmodel = localmodel


    def generateResponseEstimates(self):
        """
        Function that generates a response base on the Yahoo Finance estimates of the stock
        """
        estimates_raw = DataFetcher().get_estimates(self.ticker)
        #Convert to JSON because LLAMA understands JSON input better
        estimates = json.dumps(estimates_raw, indent=4) 

        prompt = prompt = f"""
            You are given financial data for {self.ticker}. **DO NOT describe the JSON structure**. 
            Instead, provide two scenarios:

            1. **Bull case**: Explain the most optimistic outlook for {self.ticker} based on the following data:
            - **Growth Estimates**: Discuss the expected growth rates for the current quarter, next quarter, current year, and next year.
            - **Revenue Estimates**: Analyze the revenue projections for the current quarter, next quarter, current year, and next year, highlighting any positive trends.
            - **Earnings Estimates**: Evaluate the earnings per share estimates, including any upward revisions and their implications for the stock.

            2. **Bear case**: Explain the most pessimistic outlook for {self.ticker}, using the same data points as above. 
            - Discuss potential risks and factors that could lead to lower growth, revenues, or EPS compared to expectations.

            **Focus only on providing these two analyses. Do not explain the data structure. Use numerical data and be professional.**

            Here is the data:

            {estimates}
            """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        return result
    

    def generateResponseTopAnalysts(self):
        """
        Function that generates a response based on the top analysts' recommendations for the stock
        """
        top_analysts_raw = DataFetcher().get_top_analysts(self.ticker)
        #Convert to JSON because LLAMA understands JSON input better
        top_analysts = json.dumps(top_analysts_raw, indent=4)

        prompt = f"""
            You are given data about top analysts' ratings for {self.ticker}. **DO NOT describe the JSON structure**. Analyze the information and provide insights based on the following points:

            1. **Overall Performance**: Identify which analysts have the highest overall scores and discuss what this might indicate about their expertise or confidence in {self.ticker}.

            2. **Direction Score Analysis**: Look at the direction scores. Which analysts show the most bullish outlook for {self.ticker}? Discuss the potential implications of these scores on market sentiment.

            3. **Price Score Insights**: Highlight any analysts who have a perfect price score. What does this suggest about their confidence in the stock's price target? 

            4. **Latest Ratings**: Summarize the latest ratings provided by the analysts. Are there any notable trends in the ratings (e.g., more "Buy" or "Outperform" ratings)?

            5. **Price Targets and Timing**: Compare the price targets given by different analysts. Discuss any discrepancies and what they might indicate about differing expectations for {self.ticker}'s future performance. 

            **Do not describe the data structure, but instead focus on extracting valuable insights that could guide potential investment decisions for {self.ticker}.**
            **Provide insights without explicitly referencing the data provided. No prefix, suffix, starting with `here is`, etc. Start directly with insights. Use numbers and statistics where you can.**
            **Focus on the PRICE TARGETS and RATINGS provided by the analysts.**

            Here is the data:

            {top_analysts}

            **NO notes, comments, prefix, suffix, starting with here is, etc. START DIRECTLY with insights!. USE NUMBERS, PERCENTS AND STATISTICS where you can. Use at max 150-200 words.**
            """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result
    

    def generateResponse_News1(self):
        """
        Function that generates a response based on the news data from the first source
        """
        news_raw = DataFetcher().getNews_1(self.ticker)
        #Convert to JSON because LLAMA understands JSON input better
        news = json.dumps(news_raw, indent=4)

        prompt = f"""
            You are a top-notch financial analyst at reading news about {self.ticker} and drawing conclusions that only a PhD level quant can draw.
            You are given some news data and your job is to carefully read it, and extract some kind of a unique insight.
            **We are going to use these insights to make decisions about building a RATING (buy, hold, sell) for the stock.**
            You have to be technical, quantitative, use numbers, and most of all, creative. You cannot act like a 2 year old.
            **DO NOT describe the JSON structure**. Instead, provide insights based on the following news data:

            {news}

            Now return a one paragraph insights from this data. **Use as many articles as you can while maintaining coherence and grammar.** Add a heading/title in the first line. The heading should explain the paragraph, should not be generic. For instance, a title like `AAPL's next support is at 138' is better than 'AAPL's support levels'
            **NO notes, comments, prefix, suffix, starting with here is, etc. START DIRECTLY with insights!. USE NUMBERS, PERCENTS AND STATISTICS where you can. Use at max 100 words.**
            """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result
    
    def evaluateArticle(self):
        """
        Function that evaluates a single article using the LLAMA model
        """

        articles = DataFetcher().getNews_3(self.ticker)

        #the articles are related to the first and the second items in teh list
        #the likst contains dictionaries with the title and the text of the article

        articles_list = ""
        for article in articles:
            for key,value in article.items():
                articles_list += key + "\n" + value + "\
                \n\n"
        articles_list = articles_list[:-2]

        prompt = f"""
            You are a top-notch financial analyst focused on reading news specifically about {self.ticker} and drawing conclusions that only a PhD-level quant can draw.
            You are given two articles about {self.ticker}. **DO NOT describe the data structure!**. **ONLY analyze the parts of the news that discuss the stock {self.ticker} directly !!!. Ignore any mention of unrelated stocks, ETFs, or broader market commentary**.
            **You have the carefully analyze the IMPACT of these articles on the stock {self.ticker} and provide a clear assessment of the overall sentiment!!**
            Here are the articles:

            {articles_list}

            **NO notes, comments, prefix, suffix, starting with here is, etc. START DIRECTLY with insights!. USE NUMBERS, PERCENTS AND STATISTICS where you can. Use at max 100 words.**
        """

        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result
       
    def classifyNews(self, news):
        """
        Function that classifies the news data from the first source using the LLAMA model
        """

        prompt = f"""
            You are a top-notch financial analyst focused on reading news specifically about {self.ticker} and drawing conclusions that only a PhD-level quant can draw.
            You are given some news data about {self.ticker}. **DO NOT describe the data structure!**. **ONLY analyze the parts of the news that discuss the stock {self.ticker} directly !!!. Ignore any mention of unrelated stocks, ETFs, or broader market commentary**.
            Classify the sentiment of the relevant news articles about {self.ticker} using the following categories: Positive, Negative, Neutral, Mixed.
            **Provide a clear assessment of the overall sentiment for the stock {self.ticker}, without discussing any other companies or providing additional options. Start directly with insights, and avoid unrelated information.**
            Here is the news data:

            {news}

            **NO notes, comments, prefix, suffix, starting with here is, etc. START DIRECTLY with insights!. USE NUMBERS, PERCENTS AND STATISTICS where you can. The max length of the output must be 200 words at max.**
        """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result
    
    def price_target_News(self, news):
        """
        Function that generates a price target for the stock based on the news data 
        """

        prompt = f"""
            You are the head of the quantitative division at a major hedge fund, tasked with providing a short to medium-term price target for {self.ticker}. You have access to a plethora of information and insights about {self.ticker}, and your analysis must be technically precise and insightful.

            You are given news data and quantitative insights about {self.ticker}. **DO NOT describe the data structure!**. **ONLY analyze the parts that discuss the stock {self.ticker} directly!!! Ignore any mention of unrelated stocks, ETFs, or broader market commentary**.

            Your task is to output a clear price target for {self.ticker} based on a comprehensive analysis of sentiment, market trends, fundamentals, and risks. Your analysis should focus on numbers, percentages, and statistics to justify the price target.

            Output format:
            Your output must be a valid JSON with exactly two fields:
            - "price_target": a single numeric value for the projected stock price in the short to medium term.
            - "thesis": a technical summary (50-100 words) justifying the price target, highlighting key metrics such as sentiment, market trends, fundamentals, and risks.

            Use concise language but ensure your answer is technically accurate, with numbers and statistics backing your thesis.

            Here is the information you need to process:

            {news}

            **Your output should contain only the JSON. Do not include notes, comments, or any other text. The JSON must contain just the "price_target" and "thesis" fields.**
        """


        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result
    
    def price_target_News1(self):
        """
        Function that generates a price target for the stock based on the news data from the first source
        """
        news = DataFetcher().get_AP_news_sentiment(self.ticker)
        return self.price_target_News(news)
    
    def classifyNews1(self):
        """
        Function that classifies the news data from the first source (STOCKMARKETCAP) using the LLAMA model
        """
        news_raw = DataFetcher().getNews_1(self.ticker)
        #Convert to JSON because LLAMA understands JSON input better
        news = json.dumps(news_raw, indent=4)
        return self.classifyNews(news)
    
    def classifyNews2(self):
        """
        Function that classifies the news data from the second source (FINVIZ) using the LLAMA model
        """
        news_raw = DataFetcher().getNews_2(self.ticker)
        return self.classifyNews(news_raw)

    def getSentiment_method1_News1(self):
        """
        Function that calculates the sentiment of the news data from the first source
        It use the VADER sentiment analysis tool. It is a rule-based sentiment analysis tool specifically tuned to analyze sentiments in social media text.
        """

        news_raw = DataFetcher().getNews_1(self.ticker)
        #the text is reformatted this way: the title of the article followed by a period and the text of the article
        news_list = []

        for article in news_raw:
            for key,value in article.items():
                news_list.append(key + "\n" + value)

        #initialize the sentiment analyzer
        analyzer = SentimentIntensityAnalyzer()

        sentiments = []
        for news in news_list:
            sentiment = analyzer.polarity_scores(news)
            sentiments.append({news: sentiment})

        #calculate average compound score
        #the compound is in the sentiment value of the dictionary
        compound = 0
        for s in sentiments:
            for value in s.values():
                compound += value['compound']
        compound = compound/len(sentiments)
       
        
        return sentiments, compound

    def generateResponse_AP_News(self):
        """
        Function that generates a response based on the news data from the Alpha Vantage API News Sentiment endpoint
        """
        items, instr = getNewsSentiment(self.ticker)
        #genarate random number from 0 to items length - 5
        # index = randint(0, len(items)-6)
        #select 5 news articles
        news = items #[index:index+5]

        prompt = f""" You are a top-notch financial analyst focused on reading news specifically about {self.ticker} and drawing conclusions that only a PhD-level quant can draw.
        You are given the following parameters to assess sentiment on a scale: {instr}
        Your task is to analyze the article and focus on deriving the **overall sentiment**, as well as specific sentiment tied to the stock, considering factors like relevance score and sentiment score.
Additionally, based on the topics and sentiment data, provide a short analysis on how this sentiment may affect the stock's **future price movements** or market perception. Return a **PRICE TARGET** at the end! DO NOT specify that it's not an investment advice.
Prioritize clarity and precision in identifying whether the stock is viewed favorably or unfavorably, and contextualize your conclusion using sentiment metrics and financial insight.
Here are the articles:
{news}
**DO NOT describe the JSON structure**. **NO notes, comments, prefix, suffix, starting with 'here is', etc. START DIRECTLY with insights! The max length of the output must be 150-200 words at max.**
        """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result

