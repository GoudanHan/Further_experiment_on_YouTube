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

"""#Youtube Channel description Collection

collect description of target channel using YouTube API

STEP 1:

pip install --upgrade google-api-python-client

pip install --upgrade google-auth-oauthlib google-auth-httplib2

STEP 2:
Set up your project and credentials

Create or select a project in the API Console. Complete the following tasks in the API Console for your project:

    In the library panel, search for the YouTube Data API v3. Click into the listing for that API and make sure the API is enabled for your project.

    In the credentials panel, create two credentials:

        Create an API key You will use the API key to make API requests that do not require user authorization. For example, you do not need user authorization to retrieve information about a public YouTube channel.

        Create an OAuth 2.0 client ID Set the application type to Other. You need to use OAuth 2.0 credentials for requests that require user authorization. For example, you need user authorization to retrieve information about the currently authenticated user's YouTube channel.

        Download the JSON file that contains your OAuth 2.0 credentials. The file has a name like client_secret_CLIENTID.json, where CLIENTID is the client ID for your project.

STEP 3:
extract all the video Ids
"""

import re
with open('/content/drive/My Drive/content/output.csv', 'r') as csvfile:
  lines = csv.reader(csvfile)
  next(lines)
  videoID=[]
  num=[]
  #extract videoId for each channel
  for line in lines:
    if ("Error" not in line[6]):
      num.append(line[6])
      id = re.split(r'=', line[10])
      videoID.append(id[1])

import googleapiclient.discovery

def collect_comment(vidId):
  # API information
  api_service_name = "youtube"
  api_version = "v3"
  # API key
  DEVELOPER_KEY = "DEVELOPERKEY"
  # API client
  youtube = googleapiclient.discovery.build(
      api_service_name, api_version, developerKey = DEVELOPER_KEY)

  request = youtube.commentThreads().list(
      part="id,snippet,replies",
      maxResults=2,
      order="relevance",
      videoId=vidId
      )
  response = request.execute()
  return response

from urllib.error import URLError, HTTPError
from urllib.request import urlopen
commentList = []
for ID in videoID:
  try:
    cmt = collect_comment(ID)
  except Exception:
    pass
  else:
    commentList.append(cmt)

commentList

commentList[0]['items'][1]['snippet']['topLevelComment']['snippet']['textOriginal']
