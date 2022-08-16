#!/usr/bin/env python
# coding: utf-8

# In[80]:


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


# In[81]:


data = pd.read_csv("description.csv")


# In[82]:


data
wing_c = data.loc[data["wing"]=="C"]
wing_c
wing_l = data.loc[data["wing"]=="L"]
wing_l
wing_r = data.loc[data["wing"]=="R"]
wing_r


# In[83]:


def clean_text(df):
    #make all description into a list

    desc=df["description"].to_list()

    #drop those that contains nan
    desc = [x for x in desc if str(x) != 'nan']

    #remove punctuations
    punc="""!()-[]{}'";:\,<>./?@#$%^&*_"""
    with open('stopList.txt') as f:
        lines = [line.rstrip() for line in f]
    # stop = ' '.join([x for x in lines])

    no_punc = [''.join(c.lower() for c in s if c not in punc) for s in desc]
    all_words=[]
    for s in no_punc:

        s= s.split()

        for w in s:

            #remove any words that contain non alphabet character
            if (w not in lines) and w.isalpha():
                all_words.append(w)
    return all_words
            #sentence = " ".join(sentence)
        #list.append(sentence)


# In[84]:


clean_c = clean_text(wing_c)
clean_l = clean_text(wing_l)
clean_r = clean_text(wing_r)


# In[85]:


from collections import Counter
import math
count_c = Counter(clean_c)
count_l = Counter(clean_l)
count_r = Counter(clean_r)


# In[86]:


# Simplefied TF-TDF
# tf-idf(w, wc_wing, keys_l, keys_c, keys_r) = tf(w, wc_wing) x idf(w, keys_l, keys_c, keys_r
# tf(w, wc_wing) = the number of times wc_wing uses the word w 
# idf(w, wc_wing) = log [(total number of wings)/(number of wc_wing that use the word w)]

keys_c = [key for key in count_c]
keys_l = [key for key in count_l]
keys_r = [key for key in count_r]

#IDF
def idf(w,keys_c,keys_l,keys_r):
    count = 0
    if w in keys_c:
        count+=1
    if w in keys_l:
        count+=1
    if w in keys_r:
        count+=1
    result = math.log(3/count)
    return result

#TF-IDF
def tfidf (w,count,keys_c,keys_l,keys_r):
    result = count[w] * idf(w,keys_c,keys_l,keys_r)
    return result


# In[87]:


result_tfidf_c={}
for w in keys_c:
    value = tfidf(w,count_c,keys_c,keys_l,keys_r)
    result_tfidf_c[w] = value
    
result_tfidf_l={}
for w in keys_c:
    value = tfidf(w,count_l,keys_c,keys_l,keys_r)
    result_tfidf_l[w] = value
    
result_tfidf_r={}
for w in keys_r:
    value = tfidf(w,count_r,keys_c,keys_l,keys_r)
    result_tfidf_r[w] = value
    


# In[88]:


top_c = sorted(result_tfidf_c, key=result_tfidf_c.get, reverse=True)[:5]
top_l = sorted(result_tfidf_l, key=result_tfidf_l.get, reverse=True)[:5]
top_r = sorted(result_tfidf_r, key=result_tfidf_r.get, reverse=True)[:5]


# In[89]:


print(top_c)
print(top_l)
print(top_r)

