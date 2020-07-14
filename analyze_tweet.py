def analyze():
    from bs4 import BeautifulSoup
    import requests
    import time
    from random import randint
    from IPython.display import display, HTML
    #import selenium
    #from selenium import webdriver
    import re
    import pandas as pd
    from watson_developer_cloud import NaturalLanguageUnderstandingV1
    from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SemanticRolesOptions, SentimentOptions, EmotionOptions, ConceptsOptions, CategoriesOptions
    import ibm_boto3
    from botocore.client import Config
    import json
    import nltk
    import csv
    import ibm_db
    import sys
    if sys.version_info[0] < 3: 
        from StringIO import StringIO
    else:
        from io import StringIO
    from io import BytesIO
    from urllib.parse import urlencode, urlparse, parse_qs
    from lxml.html import fromstring
    from requests import get
    from fake_useragent import UserAgent

    apikey='3Ttsj8CSHHwJBaPD1Ut9C8PqXdegQhNXINYloWPQRCbM'
    url='https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/be8d1ab7-a2c9-42a9-9c8b-f59e9e5590ca'
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-03-16',
        iam_api_key=apikey,
        url=url
    )



    credentials_1 = {
    "db": "BLUDB",
    "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=xkc99512;PWD=0mzc194p@bd5t4xg;",
    "host": "dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "hostname": "dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "https_url": "https://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net",
    "jdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50000/BLUDB",
    "parameters": {},
    "password": "0mzc194p@bd5t4xg",
    "port": 50000,
    "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=xkc99512;PWD=0mzc194p@bd5t4xg;Security=SSL;",
    "ssljdbcurl": "jdbc:db2://dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;",
    "uri": "db2://xkc99512:0mzc194p%40bd5t4xg@dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net:50000/BLUDB",
    "username": "xkc99512"
    }


    data={
    "topics": [
        {
        "coronavirus": [
            "Adeadly virus that is suffering the whole world ",
            "www.who.int"
        ]
        },
        {
        "Lockdown-extension": [
            "India has declared the lockdown throughout the country for almost 3 monthes",
            "mohfw.gov.in"
        ]
        }
    ]
    }

    df_data_1=pd.DataFrame(data)

    topics_list_final=list(df_data_1['topics'])


    def scrape_news_summaries_google(s):
        ua = UserAgent()
        
        number_result=10
        google_url = "https://www.google.com/search?q=" + s + "&num=" + str(number_result)
        response = requests.get(google_url, {"User-Agent": ua.random})
        soup = BeautifulSoup(response.text, "html.parser")

        result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})

        
        news_items=[]
        for r in result_div:
            # Checks if each element is present, else, raise exception
            
            try:
                news_dict=dict()
                link = r.find('a', href = True)
                title = r.find('div', attrs={'class':'vvjwJb'}).get_text()
                description = r.find('div', attrs={'class':'s3v9rd'}).get_text()

                # Check to make sure everything is present before appending
                if link != '' and title != '' and description != '': 
                    
                    news_dict['news_link']=link['href']
                    news_dict['summary']=description
                    news_items.append(news_dict)
            # Next loop if one element is not present
            except:
                continue
        return news_items




    final_rows=[]
    val=dict()
    for c in topics_list_final:
        for key,value in c.items():
            s='"'+key+'"'+'company economic times'
            inner_dict=dict()
            temp=[]
            temp=temp+scrape_news_summaries_google(s)
            inner_dict['Description']=value[0]
            inner_dict['topic_Link']=value[1]
            inner_dict['News_Items']=temp
            val[key]=inner_dict
            final_rows.append(val)
            val=dict()





    def split_sentences(text):
        """ Split text into sentences.
        """
        sentence_delimiters = re.compile(u'[\\[\\]\n.!?]')
        sentences = sentence_delimiters.split(text)
        return sentences



    def split_into_tokens(text):
        """ Split text into tokens.
        """
        tokens = nltk.word_tokenize(text)
        return tokens



    def load_string(fileobject):
        '''Load the file contents into a Python string'''
        text = fileobject.read()
        return text.decode('utf-8')



    def POS_tagging(text):
        """ Generate Part of speech tagging of the text.
        """
        POSofText = nltk.tag.pos_tag(text)
        return POSofText




    def resolve_coreference(text, config):
        """ Resolve coreferences in the text for Nouns that are Subjects in a sentence
        """
        sentenceList = split_sentences(text)
        referenceSubject = ''
        sentenceText = ''
        configjson = json.loads(config)
        
        for sentences in sentenceList:    
            tokens = split_into_tokens(sentences)   
            postags = POS_tagging(tokens)
            sentencetags = chunk_sentence(postags)
            subjects = find_subject(sentencetags)
            for rules in configjson['configuration']['coreference']['rules']:
                if (rules['type'] == 'chunking'):
                    for tags in rules['chunk']:
                        chunktags = chunk_tagging(tags['tag'],tags['pattern'],postags)
                        if (len(chunktags)>0):
                            for words in chunktags:
                                if tags['tag'] == 'PRP':
                                    if subjects == '':
                                        sentenceText = sentenceText+sentences.replace(words,referenceSubject)+'. '
                                elif tags['tag'] == 'NAME':
                                    if words == subjects:
                                        referenceSubject = words
                                        sentenceText = sentenceText+sentences+'. '
                        
        return sentenceText




    def chunk_sentence(text):
        """ Tag the sentence using chunking.
        """
        grammar = """
        NP: {<DT|JJ|PRP|NN.*>+} # Chunk sequences of DT,JJ,NN
            #}<VB*|DT|JJ|RB|PRP><NN.*>+{  # Chink sequences of VB,DT,JJ,NN       
        PP: {<IN><NP>}               # Chunk prepositions followed by NP
        V: {<V.*>}                   # Verb      
        VP: {<VB*><NP|PP|CLAUSE>+}  # Chunk verbs and their arguments
        CLAUSE: {<NP><VP>}           # Chunk NP, VP
        """  
        parsed_cp = nltk.RegexpParser(grammar,loop=2)
        pos_cp = parsed_cp.parse(text)
        return pos_cp




    def find_subject(t):
        for s in t.subtrees(lambda t: t.label() == 'NP'):
            return find_attrs(s,'NP')
        


    def find_attrs(subtree,phrase):
        attrs = ''
        if phrase == 'NP':
            for nodes in subtree:
                if nodes[1] in ['DT','PRP$','POS','JJ','CD','ADJP','QP','NP','NNP']:
                    attrs = attrs+' '+nodes[0]
        return attrs   

    def chunk_tagging(tag,chunk,text):
        """ Tag the text using chunking.
        """
        parsed_cp = nltk.RegexpParser(chunk)
        pos_cp = parsed_cp.parse(text)
        chunk_list=[]
        for root in pos_cp:
            if isinstance(root, nltk.tree.Tree):               
                if root.label() == tag:
                    chunk_word = ''
                    for child_root in root:
                        chunk_word = chunk_word +' '+ child_root[0]
                    chunk_list.append(chunk_word)
        return chunk_list

    def analyze_using_NLU(analysistext):
        """ Extract results from Watson Natural Language Understanding for each news item
        """
        res=dict()
        response = natural_language_understanding.analyze( 
            text=analysistext,
            features=Features(
                            sentiment=SentimentOptions(),
                            entities=EntitiesOptions(), 
                            keywords=KeywordsOptions(),
                            emotion=EmotionOptions(),
                            concepts=ConceptsOptions(),
                            categories=CategoriesOptions(),
                            ))
        res['results']=response
        return res



    def hasET(topic_name):
        cnbcVal=0
        cnbcLinks=[]
        ET_link=[]
        s='"'+topic_name+'"'+' economic times'
        res= scrape_news_summaries_google(s)
        return res



    def hasTwitter(topic_name):
        cnbcVal=0
        cnbcLinks=[]
        ET_link=[]
        s='"'+topic_name+'"'+' twitter'
        res= scrape_news_summaries_google(s)
        return res




    def getTechAreaNews(article_text):
        concept=''
        relevance=''
        if len(article_text) > 15:
            NLUres=analyze_using_NLU(article_text)
            
            if len(NLUres['results']['concepts']) != 0:
                concept=NLUres['results']['concepts'][0]['text']
                relevance=NLUres['results']['concepts'][0]['relevance']
            if len(NLUres['results']['sentiment']) != 0: 
                sentiment=NLUres['results']['sentiment']['document']['label']
        return concept,relevance,sentiment



    def getTechArea(article_text):
        concept=''
        relevance=''
        sentiment=''
        if len(article_text) > 15:
            NLUres=analyze_using_NLU(article_text)
            if len(NLUres['results']['concepts']) != 0:
                concept=NLUres['results']['concepts'][0]['text']
                relevance=NLUres['results']['concepts'][0]['relevance']
        return concept,relevance





    def hasWiki(s):
        wikiVal=0
        wikiLinks=[]
        s=s.replace(' ','+')
        link='https://en.wikipedia.org/w/index.php?search='+s+'&title=Special%3ASearch&go=Go'
        r = requests.get(link)
        #print(r.status_code)
        content = r.text
        return content




    wikiList=[]
    for f in final_rows:
        for name, info in f.items():
            wiki=dict()
            wiki['topic_Name']=name
            wiki['Wiki_Concept'],wiki['Wiki_Confidence']=getTechArea(hasWiki(name))
            wikiList.append(wiki)




    keys = wikiList[0].keys()
    with open('Wiki.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(wikiList)




    ET=[]
    for f in final_rows:
        for name, info in f.items():
            temp=dict()
            news=hasET(name)
            for n in news:
                flag=0
                if 'summary' in n:
                    summary=n['summary']
                    flag=1
                link=n['news_link']
                temp=dict()

                if 'economictimes' in link and flag:
                        temp['topic_Name']=name
                        temp['News_Link']=link
                        temp['News_Concept'],temp['News_Relevance'],temp['News_Sentiment']=getTechAreaNews(summary)
                        ET.append(temp)



    keys = ET[0].keys()
    with open('ET_final.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(ET)




    Twitter=[]
    for f in final_rows:
        for name, info in f.items():
            temp=dict()
            news=hasTwitter(name)
            for n in news:
                flag=0
                if 'summary' in n:
                    summary=n['summary']
                    flag=1
                #print(summary)
                link=n['news_link']
                temp=dict()
                #print('economictimes' in link)
                if flag:
                        temp['topic_Name']=name
                        temp['Twitter_news_link']=link
                        temp['Twitter_Topic'],temp['Twitter_Relevance'],temp['Twitter_Sentiment']=getTechAreaNews(summary)
                        Twitter.append(temp)


    keys = Twitter[0].keys()
    with open('Twitter.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(Twitter)



    file = open("ET_final.csv", "r")
    ET = pd.read_csv(file, delimiter=',')
    file = open("Wiki.csv", "r")
    Wiki = pd.read_csv(file, delimiter=',')
    file = open("Twitter.csv", "r")
    Twitter = pd.read_csv(file, delimiter=',')



    compiled_rows=pd.merge(Twitter,ET, on="topic_Name")


    compiled_rows=pd.merge(compiled_rows,Wiki,on="topic_Name")


    compiled_rows['Wiki_Confidence'].fillna(0.0, inplace=True)

    compiled_rows['News_Relevance'].fillna(0.0, inplace=True)

    compiled_rows['Twitter_Relevance'].fillna(0.0, inplace=True)



    import numpy as np
    compiled_rows = compiled_rows.replace(np.nan, '', regex=True)

    sample_len=int(100/len(list(compiled_rows.topic_Name.unique())))

    compiled_rows.groupby('topic_Name').apply(lambda x: x.sample(sample_len)).reset_index(drop=True)


    dsn_database = credentials_1['db'] 
    dsn_hostname = credentials_1['host']
    dsn_port = 50000               
    dsn_uid = credentials_1['username']      
    dsn_pwd = credentials_1['password']

    dsn = (
        "DRIVER={{IBM DB2 ODBC DRIVER}};"
        "DATABASE="+str(dsn_database)+";"
        "HOSTNAME="+str(dsn_hostname)+";"
        "PORT="+str(dsn_port)+";"
        "PROTOCOL=TCPIP;"
        "UID="+str(dsn_uid)+";"
        "PWD="+str(dsn_pwd)+";").format(dsn_database, dsn_hostname, dsn_port, dsn_uid, dsn_pwd)

    conn = ibm_db.connect(dsn, "", "")

    sql = "DELETE FROM "+dsn_uid+".DATA_FOR_DASHBOARD"
    ins_sql=ibm_db.prepare(conn, sql)
    ibm_db.execute(ins_sql)

    tuple_of_tuples = tuple([tuple(x) for x in compiled_rows.values])
    i=1
    for x in compiled_rows.values:
        vals= (i,) + tuple(x)
       # print(vals)
        sql = "INSERT INTO "+dsn_uid+".DATA_FOR_DASHBOARD VALUES"+ str(vals)
        i=i+1
        ins_sql=ibm_db.prepare(conn, sql)
        ibm_db.execute(ins_sql)

    print("successful")