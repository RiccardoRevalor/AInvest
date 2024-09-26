from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
import nltk
nltk.download('punkt_tab')
from sumy.summarizers.lex_rank import LexRankSummarizer

MAX_CHARS = 800

def summarize_text(text, language='english'):
    """
    Function to summarize text using LexRank algorithm
    """
    parser = PlaintextParser.from_string(text, Tokenizer(language))

    summarizer = LexRankSummarizer()

    l = len(text)
    if l < 1000:
        sentences_count = 3
    elif l < 2000:
        sentences_count = 5
    elif l < 3000:
        sentences_count = 8
    else:
        sentences_count = 10

    summary = summarizer(parser.document, sentences_count)

    summary_text = ' '.join(str(sentence) for sentence in summary)

    return summary_text

    if len(summary_text) > MAX_CHARS:
        summary_text = summary_text[:MAX_CHARS].rsplit(' ', 1)[0] + '.' 




if __name__ == '__main__':
    ex = '''
    From sifting through investor presentations and corporate filings to listening to earnings calls and watching interviews, getting a firm gauge on an investment often requires a lot of work.

One thing that I like to do is analyze 13F filings. These are forms filed by investment firms managing over $100 million in stocks. One of the more high-profile hedge funds is Ken Griffin's Citadel. Last quarter, Citadel reduced its stake in Nvidia (NASDAQ: NVDA) by 79% -- dumping 9,282,018 shares. In addition, the firm increased its position by 1,140% in Palantir Technologies (NYSE: PLTR), scooping up 5,222,682 shares.

Let's dig into what may have compelled Griffin and his portfolio managers to sell Nvidia and buy Palantir. Moreover, I'll explore what catalysts could help fuel even more growth for Palantir -- and why now could be a great time to follow Griffin's lead.

Why sell Nvidia right now?
On the surface, selling Nvidia stock might look like a questionable move. After all, isn't artificial intelligence (AI) the next big thing?

Well, even if AI ends up being the generational opportunity it's being touted to be, that doesn't mean a whole lot at face value. There are many components to the foundations of AI, and Nvidia's expertise in the development of advanced chipsets called graphics processing units (GPU) is just one of many building blocks supporting artificial intelligence.

The biggest bear narrative surrounding Nvidia stems from rising competition. At present, products developed by Advanced Micro Devices and Intel are the most obvious alternatives to Nvidia. However, I see a bigger risk in the competitive landscape.

Namely, Nvidia's big tech cohorts including Tesla, Meta Platforms, Microsoft, and Amazon are all investing heavily into their own hardware development. Considering that many of these companies are Nvidia's own customers, I'm wary that the company's current growth trajectory is sustainable in the long run.

When more GPUs come to market, there is a good chance this technology will be viewed as somewhat commoditized. Such a dynamic will likely lead to lower prices for Nvidia, which will subsequently bring decelerating revenue, margins, and profits.

All told, I don't really blame Griffin for selling such a large portion of his Nvidia position. Despite the company's success so far, its future prospects look potentially questionable.
'''

    summary = summarize_text(ex)
    print(summary)
    print(len(ex))
    print(len(summary))