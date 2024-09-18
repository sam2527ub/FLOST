# %%
import re
import nltk
from nltk import WordNetLemmatizer as wnl
nltk.download("wordnet")
nltk.download("omw-1.4")
import csv

# %% [markdown]
# 

# %%
class flost():
    __metaclass__ = re,wnl
    def __init__(self,db):
        self.db = db
        self.wnl = wnl()

        # print(self.db.readlines())

    def querytype(self,qtype):
        qtype=qtype.lower()
        if(qtype in ['f','found']): 
            return 1  #------------------------>found query
        return 0 #----------------------------->lost query

    def index_words(self,qt):
        index = {}
        flag = self.querytype(qt)
        if(flag):
            self.db.execute('select MainTag,Foundid from FOUND')
        else:
            self.db.execute('select MainTag,Lostid from LOST')
        # print(self.db)
        for item in self.db:
            # print(index)
            desc = item[0]
            # print(line)
            words = re.findall(r'\w+',desc) # change to fetchall for sql db
            for word in words:
                word = word.lower()
                if word in index:
                    index[word].append(item[1])
                else:
                    index[word]=[item[1]]
        # print(index)
        return index
    
    def remove_stop_words(self,index):
        stop_words = {'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at'}
        for stop_word in stop_words:
            if stop_word in index:
                del index[stop_word]
        return index
    
    def stemmer(self,index):
        stm_idx={}
        for word,count in index.items():
            stm_word=self.wnl.lemmatize(word)
            if stm_word in stm_idx:
                stm_idx[stm_word]+=count
            else:
                stm_idx[stm_word]=count
        return stm_idx
    
    def stemQueries(self,query):
        stm_query = []
        for word in query:
            stm_word = self.wnl.lemmatize(word)
            stm_query.append(word)

        return stm_query
            
    
    def search(self,query,index):
        queryWords= re.findall(r'\w+',query.lower())
        stemmedQueries = self.stemQueries(queryWords)
        results = {}
        for word in stemmedQueries:
            if word in index:
                results[word] = index[word]
        return results

    def getItems(self,query,qt):
        F_index = self.index_words(qt)
        F_index = self.remove_stop_words(F_index)
        F_index = self.stemmer(F_index)
        results = self.search(query,F_index)
        return results
    
    def listing(self,query,qt): # dictionary inverter function
        listing = {}
        matches = self.getItems(query,qt)
        for item,pids in matches.items():
            for pid in pids:
                if pid not in listing:
                    listing[pid] = []
                listing[pid].append(item)
        
        listing = {k:v for k,v in sorted(listing.items(),key = lambda item: len(item[1]),reverse=True)}
        
        return listing
        

# %%
import mysql.connector

query = "laptop asus rog inegrated"
qt='found'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="LAF"
)

mycursor = mydb.cursor()

fl = flost(mycursor)
matches = fl.getItems(query,qt)
print(matches)
listing  = fl.listing(query,qt)
print(listing)

# %%



