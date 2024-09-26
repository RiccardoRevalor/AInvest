from sec_agent import SECAgent
from analyst_agent import AnalystAgent
output_dir = "./output"
template_file = "./html_report/report_template.html"

def main():
    ticker = "AWK"
    sec_agent = SECAgent(ticker=ticker, localmodel=True)
    analyst_agent = AnalystAgent(ticker=ticker, localmodel=True)

    result = analyst_agent.generateResponse_News1()
    result2 = analyst_agent.classifyNews1()
    result3 = analyst_agent.classifyNews2()
    result4 = analyst_agent.generateResponseTopAnalysts()
    articles = analyst_agent.evaluateArticle()
    print("ARTICLE MIX:\n\n", result)
    print("NEWS_SOURCE_1:\n\n", result2)
    print("NEWS_SOURCE_2\n\n", result3)
    print("TOP_ANALYSTS\n\n", result4)
    print("ARTICLES\n\n", articles)

    sec_result = sec_agent.generateResponse()
    print("SEC_RESULT\n\n", sec_result)
    

    sentiment1, compound1 = analyst_agent.getSentiment_method1_News1()
    print("\n\n", compound1)


    #build new report from template file
    with open(template_file, 'r') as file:
        template = file.read()
        template = template.replace("{article_mix}", result)
        template = template.replace("{news_1}", result2)
        template = template.replace("{news_2}", result3)
        template = template.replace("{analysts_1}", result4)
        template = template.replace("{articles}", articles)
        template = template.replace("{sec_1}", sec_result)
        template = template.replace("{ticker}", ticker)
        #save the report in output dir
        with open(f"{output_dir}/{ticker}_report.html", 'w') as file:
            file.write(template)

    #result2 = sec_agent.generateResponse_chunks()
    #print(result2)






if __name__ == "__main__":
    main()