from sec_agent import SECAgent
from analyst_agent import AnalystAgent

def main():
    ticker = "PLTR"
    sec_agent = SECAgent(ticker=ticker, localmodel=False)
    analyst_agent = AnalystAgent(ticker=ticker, localmodel=True)

    result = analyst_agent.generateResponse_News1()
    print(result)






if __name__ == "__main__":
    main()