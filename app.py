from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request
import re
import time

from flask import Flask, render_template, request
app = Flask(__name__)

headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

@app.route('/')
def student():
   return render_template('index.html')


@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      resultImmutable = request.form
      result = getLinks(resultImmutable['URL'], resultImmutable['time'])
      #result['URL'] = resultImmutable['URL']
      return render_template("result.html", result = result)



def getLinks(url, t):
    req = Request(url, headers = headers)
    html_page = urlopen(req)
    #html_page = requests.get(url, headers=headers)
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(html_page, "html.parser")
    #print(soup)
    urls = set()
    internal_urls = {}
    external_urls = {}

    start = time.time()

    for a_tag in soup.findAll("a"):
        try:
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)

            if time.time() - start < int(t):
                if is_valid(href):
                    req2 = Request(href, headers = headers)
                    html_page2 = urlopen(req2)
                    soup2 = BeautifulSoup(html_page2, "html.parser")
                    name = soup2.title.string.strip()
            else:
                name = parsed_href.netloc

            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                # not a valid URL
                continue
            if href in internal_urls:
                # already in the set
                continue
            if domain_name not in href:
                # external link
                if href not in external_urls:
                    external_urls[name] = href
            else:
                if href not in internal_urls:
                    internal_urls[name] = href
            urls.add(href)
        except:
            print(a_tag)
    

    # print("---------")
    # print(domain_name)
    # print("---------")
    # print(internal_urls)
    # print("---------")
    # print(external_urls)
    # print("---------")
    # print(urls)
    # print("---------")
    return {'internalURLS': internal_urls,
            'externalURLS': external_urls,
            } #'allURLS': urls



def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)



if __name__ == '__main__':
    #print(getLinks("https://haccess.isodme.com/"))
    #print(getLinks("https://hackmit.org/"))
    #print(getLinks("https://google.com/"))
    #getLinks("https://haccess.isodme.com/")
    app.run(debug = True)
