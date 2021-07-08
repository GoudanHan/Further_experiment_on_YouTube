import anytree.search
import treelib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
import Video
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
#from treelib import Node, Tree
from anytree import Node, AnyNode, NodeMixin,RenderTree, AbstractStyle, ContStyle
from YTQueue import YTQueue, Node
from collections import deque
import asyncio

class YouTubeScraper:
    def __init__(self, path_driver, category, seed_url, max_wait, history=False):
        self.path = path_driver
        self.driver = self.create_chrome_driver()
        self.driverconst = self.driver.title
        self.category = category
        self.seed_url = seed_url
        self.history = history
        self.max_wait = max_wait

    def create_chrome_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--mute-audio")

        return webdriver.Chrome(executable_path=self.path, options=options)

    def update_tabs(self):
        pass

    def control(self):
        pass


###### Video Processing #################
    def video_processing(self, url) -> object:

        self.driver.get(url)
        time.sleep(1)
        try:
            self.driver.find_elements_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span')[0].click()
        except:
            try:
                self.driver.find_elements_by_xpath('/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[2]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a/tp-yt-paper-button/yt-formatted-string')[0].click()
            except:
                pass
            pass
        #skip ad
        time.sleep(2)
        ad = self.check_ad()
        while(self.check_ad() == True):
            self.skip_ad()
            time.sleep(2)

        if (ad == False):
            self.start_video()

        # extract the video length with the JavaScript code
        # use JavaScript since the element isn't always visible
        length = self.driver.execute_script("return document.getElementById('movie_player').getDuration()")

        #watch the video for a little, simulate a person
        self.wait_seconds(length)

        #collect the features
        video = self.collect_data(url=url, length=length, ads=ad)

        #get the recommended videos
        recommended = self.get_video_recommendations()

        self.driver.close()
        return video, recommended

    def start_video(self):
        time.sleep(2)

        #click on the button to start if
        try:
            element = self.driver.find_element_by_xpath("//button[@class='ytp-large-play-button ytp-button']")
            element.click()
        except ElementNotInteractableException:
            pass

    # checks if there's an ad playing or not
    def check_ad(self) -> bool:
        ads = self.driver.find_elements_by_css_selector('button[id^=visit-advertiser] > span.ytp-ad-button-text')
        if (len(ads) == 0):
            return False
        else:
            return True

    def skip_ad(self):
        time.sleep(5)
        #wait for the end of the advertisement
        try:
            #first make sure it can be skipped by finding the ad text button
            element = self.driver.find_elements_by_xpath('//*[contains(@id, "ad-text:")]')
            for i in element:
                if(i.text == 'Skip Ads' or i.text == 'Skip Ad'):
                    self.driver.find_elements_by_xpath('//*[@class="ytp-ad-skip-button ytp-button"]')[0].click()
                    break

        except TimeoutException:
            pass

    # wait minutes to simulate watching a video, length is the video's length
    def wait_seconds(self, length):
        if (length < self.max_wait):
            #WebDriverWait(driver=self.driver, timeout=length)
            time.sleep(length)
        else:
            #WebDriverWait(driver=self.driver, timeout=self.max_wait)
            time.sleep(self.max_wait)

    def collect_data(self, url, length, ads):
        time.sleep(1)
        self.driver.execute_script('window.scrollTo(0, 540)')
        time.sleep(2)

        #prepare beautiful soup for webpage extraction
        session = HTMLSession()
        response = session.get(url)
        # execute Javascript
        response.html.render(timeout=30)
        # create beautiful soup object to parse HTML
        soup = bs(response.html.html, "html.parser")

        #need to process all of these in video object
        title = self.get_title()
        creator = self.get_creator(soup=soup)
        description = self.get_description(soup=soup)
        dates = self.get_date(soup=soup)
        views = self.get_views(soup=soup)

        number_comments = self.get_by_xpath('//*[@id="count"]/yt-formatted-string/span[1]')
        if(number_comments != 'Error found'):
            number_comments = number_comments.text

        url = url
        id = self.video_url_to_id(url)

        likes, dislikes = self.get_likes_dislikes(soup=soup)

        tags = self.get_tags(soup=soup)

        length = length
        ads = ads

        vid = Video.video(title=title, content_creator=creator,
                          description=description, date=dates,
                          views=views, comments=number_comments,
                          likes=likes, dislikes=dislikes,
                          transcript='the transcript', tags=tags,
                          video_length=length, url=url,
                          ad=ads, id=id)

        response.close()
        session.close()
        #find a way to cycle through comments

        return vid

    def video_url_to_id(self, url):
        s = url.split('=')
        return s[1]

    def get_tags(self, soup):
        # open("index.html", "w").write(response.html.html)
        # initialize the result
        tags = ', '.join([ meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"}) ])
        return tags

    def get_likes_dislikes(self, soup):
        result = [i.get_attribute("aria-label") for i in self.driver.find_elements_by_xpath('//yt-formatted-string[@id="text"]') if i.get_attribute("aria-label") != None]

        likes = [i for i in result if ('like' in i) and ('dislike' not in i)]
        dislikes = [i for i in result if ' dislike' in i]

        return likes[0] if (len(likes) != 0) else 'Unavailable', dislikes[0] if (len(dislikes) != 0) else ' Unavailable'

    def get_title(self):
        return self.driver.find_elements_by_xpath('//*[@id="container"]/h1/yt-formatted-string')[0].text

    def get_creator(self, soup):
        return self.driver.find_elements_by_xpath('//*[@id="text"]/a')[1].text

    def get_views(self, soup):
        return self.driver.find_elements_by_xpath('//*[@id="count"]/ytd-video-view-count-renderer/span[1]')[0].text

    def get_description(self, soup):
        return self.driver.find_elements_by_xpath('//*[@id="description"]/yt-formatted-string/span[1]')[0].text

    def get_date(self, soup):
        return self.driver.find_elements_by_xpath('//*[@id="info-strings"]/yt-formatted-string')[0].text

    def get_duration(self, soup):
        soup.find("span", {"class": "ytp-time-duration"}).text

    def get_video_recommendations(self):
        recommended_videos = []

        #here the 1 is an index that you can use to cycle through recommended videos
        i = 1
        while(i <= 7):
            path = '//*[@id="items"]/ytd-compact-video-renderer[{0}]//*[@id="thumbnail"]'.format(i)
            recommended = self.driver.find_element_by_xpath(path).get_attribute('href')
            recommended_videos.append(recommended)
            i += 1

        return recommended_videos

    def get_by_xpath(self, xpath):
        try:
            return self.driver.find_element_by_xpath(xpath=xpath)
        except:
            return 'Error found'
def test_deque():
    #problem to solve: parent is not upating
    url = "https://www.youtube.com/watch?v=sf-qyxEIuHI"
    de = deque([url])
    root = AnyNode(id=url, parent=None, url=None, video=None)

    for i in range(0, 500):
        x = de.popleft()
        scraper = YouTubeScraper(path_driver="C:\Program Files (x86)\chromedriver.exe",
                                 category='Alt-right',
                                 seed_url=url,
                                 max_wait=1)
        video, recommendations = scraper.video_processing(x)
        node = None
        if (root.url == None):
            root.url = x
            root.video = video
            node = root
        else:
            nodes = anytree.search.findall(root, filter_= lambda node: node.url == video.url)

            #should be unique
            for i in nodes:
                i.video = video
                node = i

        for i in recommendations:
            de.append(i)
            new_node = AnyNode(id=i, parent=node, url=i, video=None)
    print(RenderTree(root, style=ContStyle()))

def main():
    test_deque()

    print('done')
if __name__ == '__main__':
    main()


# moving forward: clicking on videos and tab management!
# put all the feature extracting in some form of try catch thing to avoid the huge number of errors that can pop up
# updating the code so to incorporate asynchronous features