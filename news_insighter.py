import llm
from fetch_data import DataFetcher

class NewsInsighter:
    def __init__(self, ticker, localmodel=False):
        self.ticker = ticker
        self.stockPrice = DataFetcher(ticker).getStockPrice(ticker)   
        self.model = "llama3-8b-8192"
        self.localmodel = localmodel
    

    def generateBearCase(self, news):
        prompt = f"""
        Current price of {self.ticker} is {self.stockPrice}.
        
        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a **bear case** for {self.ticker}.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here are the insights:
        ```
        {news}
        ```

        Output Format:
        Your output must be a json with two fields.
        - price_target
        - thesis

        Your price target should be based on your thesis, so write that first. Thesis should be 50-100 words at max. Your language should be plain, but your answer must be super technical with respect to numbers,
        fundamentals, technicals, strengths, risks, etc. Your answer must only talk about a bear thesis, do not talk about strengths, or caution. We have other analysts for that. Do not mention that price target in your thesis. An example of a bull thesis is

        ```
        Driving subscription streaming adoption proves to be more challenging, with Spotify losing global market share: Total Premium subscribers reach ~290M by 2026E. Smaller scale limits leverage from the advertising business, but non-core service offerings and monetization of non-music content listening help increase gross margins...
        ```

        example:
        {{"thesis": "...", "price_target": "120"}}

        Do not start with ```json, start with the first bracket.
        """

        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        return result
    

    def generateBullCase(self, news):
        prompt = f"""
        Current price of {self.ticker} is {self.stockPrice}.

        You are an expert financial analyst at a big hedge fund. You are provided a plethora of information and insights about {self.ticker}.
        You are tasked with writing a **bull case** for {self.ticker}.

        You are not an intern, so make sure the case you write is super technical, super helpful, and super accurate. You have read every finance blog out there,
        so use that knowledge. Think of yourself as the head of quantitative divison in a big prop trading firm.

        Here are the insights:
        ```
        {news}
        ```
        
        Output Format:
        Your output must be a json with two fields.
        - price_target
        - thesis

        Your price target should be based on your thesis, so write that first. Thesis should be 50-100 words at max. Your language should be plain, but your answer must be super technical with respect to numbers,
        fundamentals, technicals, strengths, risks, etc. Your answer must only talk about a bull thesis, do not talk about risks, or caution. We have other analysts for that. Do not mention that price target in your thesis. An example of a bull thesis is

        ```Subscription streaming adoption increases more rapidly than in base case and Spotify maintains global share: Total Premium subscribers reach ~315M by 2026E. Greater scale, price increases, and market-leading position give the company operating leverage. This contributes to greater gross margin growth than```

        example:
        {{"thesis": "...", "price_target": "500"}}

        Do not start with ```json, start with the first bracket.
        """

        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        return result