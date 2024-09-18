import llm
from fetch_data import DataFetcher
import json

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
            """
        
        if self.localmodel:
            result = llm.generateResponseLocally(prompt)
        else:
            result = llm.generateResponse(prompt, model=self.model)
        
        return result