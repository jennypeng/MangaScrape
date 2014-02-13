import sys
import os
import urllib2
from os.path import basename
from urlparse import urlsplit
from bs4 import BeautifulSoup
import mechanize
import cookielib
# pdf handler
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

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
'''
Prompt for a series name and open the url for the series page.
'''
def prompt():
    series_name = raw_input("Series name: ").lower().strip().replace(" ", "_")
    url = "http://mangafox.me/manga/" + series_name + "/"
    openURL(url)

'''
Ask the users for a new request or to exit the program.
'''
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
'''
Download the image located at imageSRC, and save into \series_name\chapter[chapter_num]\. 
'''
def getImage(src, chapter_num, series_name, page_num):
    #while not src == "": # we w=set tge src ti e=tge enoty string when mechanize fails to find a next page in the chapter
        #counter = 1 # start off at page 1 
    try:
        imgData = urllib2.urlopen(src).read()
        fileName = "page" + str(page_num) + ".jpg" # keep a running count of what page we're on 
        output = open(fileName, 'wb')
        output.write(imgData)
        output.close()
        os.rename('/' + fileName, '/' + series_name + '/chapter' + str(chapter_num) + "/" + fileName)
        #counter += 1
        #get the next image
        #src = mechanize

        #print "image downloaded"
    except:
        raise
    '''
Convert the images to a pdf.
'''
def convertPDF(chapter_num, seriess_name):
    try:
        n = 0
        for dirpath, dirnames, filenames in os.walk('\\' + series_name + '\\chapter' + str(chapter_num) + "\\"): # the downloaded files are going to be in chapter directory 
            PdfOutputFileName = "chapter" + str(chapter_num) + ".pdf"
            c = canvas.Canvas(PdfOutputFileName)
            if n > 0:
                for filename in filenames:
                    LowerCaseFileName = filename.lower()
                    if LowerCaseFileName.endswith(".jpg"):
                        filepath = os.path.join(dirpath, filename)
                        print(filepath)
                        im = ImageReader(filepath)
                        imagesize = im.getSize()
                        c.setPageSize(imagesize)
                        c.drawImage(filepath, 0, 0)
                        c.showPage()
                        c.save()
            n = n + 1
            print "PDF created" + PdfOutputFileName
    except:
        raise

def getFiles(url, chapter_num):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    imageSRC = soup.find('img', {'id': "image"}).get('src')
    # try to download image
    counter = 1
    while not nextPage == "javascript:void(0)":
        getImage(imageSRC, chapter_num, counter)
        nextPage = soup.find('a', {'onclick': "return enlarge()"}).get('href')
        page = urllib2.urlopen(baseurl + nextPage)
        soup = BeautifulSoup(page)
        soup.prettify()
        imageSRC = soup.find('img', {'id': "image"}).get('src')
        counter += 1
    # try to convert all images to pdf
    convertPDF(chapter_num)
    



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
        chapter_num = raw_input("Chapter number: ")
        zero_pad_num = chapter_num.zfill(3)
        for chapter in soup.find_all('a', {'class': "tips"}):
            chapterURL = chapter.get('href')
            query = 'c' + chapter_num
            if query in chapterURL:
                print("found query at " + chapterURL)
                getFiles(chapterURL, chapter_num, "test1")
                break
                


    


if __name__ == '__main__':
    prompt()
   
