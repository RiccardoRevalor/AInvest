from sec_agent import SECAgent
from analyst_agent import AnalystAgent
from news_insighter import NewsInsighter
import markdown as md
output_dir = "./output"
template_file = "./html_report/report_template.html"

def main():
    ticker = "STAG"
    sec_agent = SECAgent(ticker=ticker, localmodel=True)
    analyst_agent = AnalystAgent(ticker=ticker, localmodel=True)
    news_insighter = NewsInsighter(ticker=ticker, localmodel=True)

    result = analyst_agent.generateResponse_News1()
    result2 = analyst_agent.classifyNews1()
    result3 = analyst_agent.classifyNews2()
    result4 = analyst_agent.generateResponseTopAnalysts()
    articles = analyst_agent.evaluateArticle()
    ap_result = analyst_agent.generateResponse_AP_News()
    #print("ARTICLE MIX:\n\n", result)
    #print("NEWS_SOURCE_1:\n\n", result2)
    #print("NEWS_SOURCE_2\n\n", result3)
    #print("TOP_ANALYSTS\n\n", result4)
    #rint("ARTICLES\n\n", articles)

    sec_result = None
    try:
        sec_result = sec_agent.generateResponse()
        print("SEC_RESULT\n\n", sec_result)
    except Exception as e:
        print("Exception raised1:", e)
        sec_result = None
    
    #concatenate the news from the two sources to create insights for the news insighter
    news = result + "\n" + result2 + "\n" + result3
    
    bearCase = news_insighter.generateBearCase(news)
    print("BEAR CASE\n\n", bearCase)

    bullCase = news_insighter.generateBullCase(news)
    print("BULL CASE\n\n", bullCase)


    try:
        sentiment1, compound1 = analyst_agent.getSentiment_method1_News1()
        print("\n\n", compound1)
    except Exception as e:
        print("Exception raised2:", e)
        sentiment1 = None
        compound1 = None


    #build new report from template file
    with open(template_file, 'r') as file:
        template = file.read()
        template = template.replace("{article_mix}", md.markdown(result))
        template = template.replace("{news_1}", md.markdown(result2))
        template = template.replace("{news_2}", md.markdown(result3))
        template = template.replace("{analysts_1}", md.markdown(result4))
        template = template.replace("{articles}", md.markdown(articles))
        if sec_result is not None:
            template = template.replace("{sec_1}", md.markdown(sec_result))
        else: template = template.replace("{sec_1}", "Unable to fetch 10-K Module for the stock.")
        template = template.replace("{ticker}", ticker)
        template = template.replace("{ap_result1}", md.markdown(ap_result))
        #save the report in output dir
        with open(f"{output_dir}/{ticker}_report.html", 'w') as file:
            file.write(template)

    #result2 = sec_agent.generateResponse_chunks()
    #print(result2)


def test_func():
    """
    This function is used to test the functionality of the agents
    """
    ticker = "AAPL"
    analyst_agent = AnalystAgent(ticker=ticker, localmodel=True)
    result = analyst_agent.generateResponse_AP_News()
    print(result)



if __name__ == "__main__":
    main()
    #test_func()