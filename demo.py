from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from bs4 import BeautifulSoup

def getTitle(url):
    try:
        html=urlopen(url)
    except (HTTPError,URLError) as e:
        return None
    try:
        bsObj=BeautifulSoup(html.read())
        title=bsObj.body.h1.get
    except AttributeError as e:
        return None
    return title

def getTable(url):
    try:
        html=urlopen(url)
    except(HTTPError,URLError) as e:
        return None
    try:
        bsobj=BeautifulSoup(html.read())
        # print(bsobj)
        for child in bsobj.find('table',{'id':'giftList'}).tr.next_siblings:
            print(child)
    except AttributeError as e:
        return None
if __name__ == '__main__':

    getTable('http://www.pythonscraping.com/pages/page3.html')

    # title=getTitle("http://www.pythonscraping.com/pages/page1.html")
    # if title == None:
    #     print("title could not be found")
    # else:
    #     print(title)
# try:
#
#     html=urlopen("https://itra.run/community/xiangbo.meng/2187079//")
# except HTTPError as e:
#     print(e)
# else:
#     bsObj=BeautifulSoup(html.read())
#     print(bsObj.text)