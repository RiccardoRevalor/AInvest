import os
from bs4 import BeautifulSoup
import re 
import pandas as pd

class FilingsReader:
    def __init__(self):
        pass

    def parse_sec_filing(self, content):
        """
        Parse SEC filing txt content and extract relevant sections.
        Args:
            content (str): The txt content of the SEC filing.
        Returns:
            dict: A dictionary containing parsed sections of the SEC filing.
                  Keys are section names, and values are the corresponding content.
        """
        #the 10-K filings info are in the <DOCUMENT> tag
        startPattern = re.compile(r'<DOCUMENT>')
        endPattern = re.compile(r'</DOCUMENT>')

        #Each section within the document tags is clearly marked by a <TYPE> tag followed by the name of the section.
        typePattern = re.compile(r'<TYPE>[^\n]+')


        """
        3 lists are used:
        1) endIndices: contains the end index of each <DOCUMENT> tag
        2) startIndices: contains the start index of each <DOCUMENT> tag
        3) typeIndices: contains the index of each <TYPE> tag
        """

        endIndices = [m.end() for m in endPattern.finditer(content)]
        startIndices = [m.start() for m in startPattern.finditer(content)]
        #the third one is useful for finding section names because in the document tags there is a <TYPE> tag followed by the name of the section
        #ex: <TYPE>EX-32.01
        #the line is <TYPE> + section name + \n
        typeIndices = [m[len("<TYPE>"):] for m in typePattern.findall(content)]

        #initialize the dictionary to store the sections
        dict = {}

        #iterate over the document tags
        for type, start, end in zip(typeIndices, startIndices, endIndices):
            #if type != '10-K': continue
            #extract the type name (ex 10-K, EX-32.01)
            type = type.strip()
            #extract the content of the type section
            typeContent = content[start:end]
            #store the content in the dictionary
            dict[type] = typeContent


        return dict
    
    def extract_10K_items(self, dict, content):
        """
        Extract the 10-K items from the parsed SEC filing.
        Args:
            dict (dict): A dictionary containing parsed sections of the SEC filing.
        Returns:
            dict: A dictionary containing the 10-K items.
        """

        #initialize the dictionary to store the 10-K items
        items = {}
        content10k = dict['10-K']
        
        """
        the following items from the 10-K report will be extracted:
        1A - Risk Factors
        6 - Selected Financial Data
        7 - Management's Discussion and Analysis of Financial Condition and Results of Operations
        7A - Quantitative and Qualitative Disclosures About Market Risk
        8 - Financial Statements and Supplementary Data
        """

        #regex to match the tags
        #the items 1B and 9 are used to find the end of the previous item but are not stored
        itemsRegex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|5|6|7A|7|8|9)\.{0,1})|(ITEM\s(1A|1B|5|6|7A|7|8|9))')

        # Use finditer to math the regex
        matches = itemsRegex.finditer(dict['10-K'])

        # Write a for loop to print the matches
        #for match in matches:
        #    print(match)

        #ech item is mathed twice, once with the >Item tag and once with the ITEM tag
        #this is because at the start of the filig there is the index
        items_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches], columns=['item', 'start', 'end'])
        items_df['item'] = items_df.item.str.lower().str.strip()   

        # Get rid of unnesesary chars from the dataframe
        items_df.replace('&#160;',' ',regex=True,inplace=True)
        items_df.replace('&nbsp;',' ',regex=True,inplace=True)
        items_df.replace(' ','',regex=True,inplace=True)
        items_df.replace('\.','',regex=True,inplace=True)
        items_df.replace('>','',regex=True,inplace=True)

        #sort the df by the start index in ascending order and then remove the duplicates of the index (so the FIRST occurence of the item is removed)
        items_df = items_df.sort_values('start',ascending=True).drop_duplicates(subset=['item'], keep='last')

        #set the 'item' column as the index
        items_df.set_index('item', inplace=True)

        #Now, the dataframe contains the starting and end index of each match for Items 1A, 6, 7, 7A, 8.
        #The next step is to extract the content of each item.
        #The content of each item is the text between the start index of the current item and the start index of the next item.
        #So, search in the dict with the content the text between the start index of the current item and the start index of the next item.
        items_raw = {}
        items_raw['item_1a'] = content10k[items_df['start'].loc['item1a']:items_df['start'].loc['item1b']]
        items_raw['item_5'] = content10k[items_df['start'].loc['item5']:items_df['start'].loc['item6']]
        items_raw['item_6'] = content10k[items_df['start'].loc['item6']:items_df['start'].loc['item7']]
        items_raw['item_7'] = content10k[items_df['start'].loc['item7']:items_df['start'].loc['item7a']]
        items_raw['item_7a'] = content10k[items_df['start'].loc['item7a']:items_df['start'].loc['item8']]
        items_raw['item_8'] = content10k[items_df['start'].loc['item8']:items_df['start'].loc['item9']]

        #Now, use BeautifulSoup to extract the text from the HTML/XBLR content
        item1a_lxml = BeautifulSoup(items_raw['item_1a'], 'lxml')
        item5_lxml = BeautifulSoup(items_raw['item_5'], 'lxml')
        item6_lxml = BeautifulSoup(items_raw['item_6'], 'lxml')
        item7_lxml = BeautifulSoup(items_raw['item_7'], 'lxml')
        item7a_lxml = BeautifulSoup(items_raw['item_7a'], 'lxml')
        item8_lxml = BeautifulSoup(items_raw['item_8'], 'lxml')

        #save item8_lxml to a file
        with open("./item8.txt", "w", encoding='utf-8') as f:
            f.write(item8_lxml.prettify())
            f.close()

        #The goal now is to remove all the HTML tags and keep only the text
        #The get_text() method of BeautifulSoup returns the text of the tag

        items['item_1a'] = item1a_lxml.get_text("\n\n")
        items['item_5'] = item5_lxml.get_text("\n\n")
        items['item_6'] = item6_lxml.get_text("\n\n")
        items['item_7'] = item7_lxml.get_text("\n\n")
        items['item_7a'] = item7a_lxml.get_text("\n\n")
        items['item_8'] = item8_lxml.get_text("\n\n")

        return items
    

        