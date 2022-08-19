"""#Data filtering



*   remove empty channel
*   drop duplicate
*   map content creator to their political affiliation




"""

import csv
import json
import pandas as pd
import os
from google.colab import drive
drive.mount('/content/drive')

title_wing=[]
#extract each channel name with their corresponding political affiliation    
with open('/content/drive/My Drive/content/channel_review.csv', 'r') as csvfile:
  lines = csv.reader(csvfile)
  for line in lines:
    title = line[0]
    wing = line[3]
    title_wing.append([title, wing])

#make all file names inside Video directory into a list of string
file_NAME = []
for filename in os.listdir("/content/drive/My Drive/content/Videos"):           
  file_NAME.append(filename)

def pull_data (data_list,json):
  for i in json:                                    
    #extract content creater
    title =json[i]['content creator']               

    for j in title_wing:

      #if matched content creater has found
      if title == j[0]:                             
       
       #add component "wing" to each element
        json[i]['wing'] = j[1]                      
     
        data_list.append(json[i])

result=[]
#iterate through each file inside Video directory
for name in file_NAME:                           
  json_file = open('/content/drive/My Drive/content/Videos/'+name)
  json_data = json.load(json_file)
  #write each unique content creator and its into into a list
  pull_data(result,json_data)                       
result

csv_header = ['title', 'content creator', 'wing', 'description', 'date', 'views', 'comments', 'likes', 'dislikes', 'video_length', 'url', 'id']
with open('/content/drive/My Drive/content/result.csv', 'w') as csvfile:                     
    writer = csv.DictWriter(csvfile, fieldnames = csv_header)
    writer.writeheader()
    writer.writerows(result)

results =pd.read_csv('/content/drive/My Drive/content/result.csv')
#remove duplicated content creator
rmdup_results = results.drop_duplicates(subset = "content creator",keep='first')       
rmdup_results
#remove content creator that has no political affiliation
rmdup_results=rmdup_results.dropna(subset=["wing"])

final_result =rmdup_results.reset_index(drop=True)                       
final_result= final_result.to_dict('index')                                                       
final_result=list(final_result.values())

final_result

drive.mount('/content/drive')
path = '/content/drive/My Drive/content/output.csv'
csv_header = ['title', 'content creator', 'wing', 'description', 'date', 'views', 'comments', 'likes', 'dislikes', 'video_length', 'url', 'id']
with open(path, 'w', encoding = 'utf-8-sig') as f:                                   
  writer = csv.DictWriter(f, fieldnames = csv_header)
  writer.writeheader()
  writer.writerows(final_result)

