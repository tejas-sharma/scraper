from bs4 import BeautifulSoup
import os
import argparse
import requests
import urllib
from ftplib import FTP

class Url:
    def __init__(self, url):
        self._url = url
        parsedUrl = urllib.parse.urlparse(url)
        self._baseUrl = '{}://{}'.format(parsedUrl.scheme, parsedUrl.hostname)
        
def getAnchors(url):
    request = requests.get(url)
    if (request.status_code < 400):
        contents = request.text
        soup = BeautifulSoup(contents, 'html.parser')
        return [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]

def downloadFile(url, filePath):
    if os.path.exists(filePath):
        return
    parsedUrl = urllib.parse.urlparse(url)
    contents = ''
    if parsedUrl.scheme == 'ftp':
        googleCache = 'http://webcache.googleusercontent.com/search?q=cache:{}'.format(url)
        request = requests.get(googleCache)
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'html.parser')
            if soup.pre is not None:
                contents = soup.pre.string
    else:
        request = requests.get(url)
        if (request.status_code < 400):
            contents = request.text
        else:
            print("Encountered an error when attempting to download data from {}: {}".format(url,request.status_code))

    if contents is not '':
        with open(filePath, 'w') as f:
            f.write(request.text)


def scrape(url, level, exts):
    anchors = getAnchors(url._url)
    for anchor in anchors:
        isFile = any(ext in anchor for ext in exts)
        if isFile:
            fileName = anchor.split('/')[-1]
            if fileName is not None and fileName is not '':
                if anchor.startswith('/'):
                    downloadFile('{}{}'.format(url._baseUrl, anchor), fileName)
                else:
                    downloadFile(anchor, fileName)
        else:
            if level == 0 and anchor.startswith('/'):
                scrape(Url(url._baseUrl + '/' + anchor), level+1, exts)

parser = argparse.ArgumentParser(description='Utility for scraping things')
#rootGroup = parser.add_mutually_exclusive_group()

#scraperGroup = rootGroup.add_argument_group('scrape')
parser.add_argument('url', help='Path to file')

#downlGroup = rootGroup.add_argument_group('downl')
#downlGroup.add_argument('--url', help='URL to site')
#downlGroup.add_argument('--fileName', help='File to download to')
args = parser.parse_args()
if (args.url):
    scrape(Url(args.url), 0, ['.txt'])
#elif (args.url and args.fileName):
#    downloadFile(Url(args.url, args.fileName))