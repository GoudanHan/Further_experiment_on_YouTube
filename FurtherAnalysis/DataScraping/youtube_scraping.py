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