import sys
import os
import urllib2
from os.path import basename
from urlparse import urlsplit
from bs4 import BeautifulSoup
import mechanize
import cookielib

# Browser
br = mechanize.Browser()

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True) # compression
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# debugging messages
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
# br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
def prompt():
    series_name = raw_input("Series name: ").lower().strip().replace(" ", "_")
    url = "http://mangafox.me/manga/" + series_name + "/"
    openURL(url)
def reprompt():
    print("[y] for new series request")
    print("[q] for exit")
    quit = raw_input().lower().strip()
    if quit == 'q':
        return
    elif quit == 'y':
        prompt()
    else:
        print("Sorry, I couldn't understand you")
        reprompt()

def getFiles(url):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    imageSRC = soup.find('img', {'id': "image"}).get('src')
    # try to download image
    try:
        imgData = urllib2.urlopen(imageSRC).read()
        fileName = "page1.jpg" #change later
        output = open(fileName, 'wb')
        output.write(imgData)
        output.close()
        #os.rename('/' + fileName, '/' + fileName)
    except:
        print("why does this not work")




def openURL(url):
    r = br.open(url) # open our browser object to the comic page
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    html = r.read()
    # manga is licensed
    if "has been licensed, it is not available" in html:
        print("Sorry, the series has been licensed")
        reprompt()
    elif "searchform_name" in html:
    # deal with search
        br.select_form(nr = 1)
        br.submit()
        #print(br.response().read())
    else: # does not work for half chapters at the moment
        chapter_num = raw_input("Chapter number: ").zfill(3)
        for chapter in soup.find_all('a', {'class': "tips"}):
            chapterURL = chapter.get('href')
            query = 'c' + chapter_num
            if query in chapterURL:
                print("found query at " + chapterURL)
                getFiles(chapterURL)
                break
                


    


if __name__ == '__main__':
    prompt()
   
