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
    try:
        print "downloading page", str(page_num), '...',
        imgData = urllib2.urlopen(src).read()
        fileName = "page" + str(page_num) + ".jpg" # keep a running count of what page we're on 
        output = open(fileName, 'wb')
        output.write(imgData)
        output.close()
        print "done"
    except:
        raise
'''
Get the page number from the file name for sorting purposes. 
'''
def pageNum(a):
    return int(a.rsplit("page")[1].rsplit(".jpg")[0])
'''
Convert the images to a pdf.
'''
def convertPDF(chapter_num, series_name):
    try:
        n = 1
        for dirpath, dirnames, filenames in os.walk("ROOT_PATH"):
            PdfOutputFileName = "chapter" + str(chapter_num) + ".pdf"
            c = canvas.Canvas(PdfOutputFileName)
            if n == 1: 
                filenames = sorted([name for name in filenames if name.endswith(".jpg")], key = pageNum)
                for filename in filenames: 
                    print "evaluating file name " + filename
                    LowerCaseFileName = filename.lower()
                    if LowerCaseFileName.endswith(".jpg"):
                        filepath = os.path.join(dirpath, filename)
                        print "found page " + filename
                        im = ImageReader(filepath)
                        imagesize = im.getSize()
                        c.setPageSize(imagesize)
                        c.drawImage(filepath, 0, 0)
                        c.showPage()
                        c.save()
                        try:
                            os.remove(filepath)
                        except WindowsError as e:
                            print e
            n = n + 1
            print "PDF created " + PdfOutputFileName
    except:
        raise

def getFiles(url, chapter_num):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    imageSRC = soup.find('img', {'id': "image"}).get('src')
    baseurl = url.rsplit("/", 1)[0] + "/"
    counter = 1
    nextPage = ""
    while True:
        getImage(imageSRC, chapter_num, "Koe no Katachi", counter)
        imgLink = soup.find('a', {'onclick': "return enlarge()"})
        if not imgLink: break
        nextPage = imgLink.get('href')
        page = urllib2.urlopen(baseurl + nextPage)
        soup = BeautifulSoup(page)
        soup.prettify()
        imgLink = soup.find('img', {'id': "image"})
        if not imgLink: break
        imageSRC = imgLink.get('src')
        counter += 1
    # try to convert all images to pdf
    convertPDF(chapter_num, "Koe no Katachi")
    



def openURL(url):
    print("yooooo")
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
            print chapterURL
            query = 'c' + zero_pad_num
            if query in chapterURL:
                print("found query at " + chapterURL)
                getFiles(chapterURL, chapter_num) # rememeber to add name of title
                break
                
if __name__ == '__main__':
    prompt()
   
