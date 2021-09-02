# binary = FirefoxBinary('Applications/Tor Browser.app/Contents/MacOS')
import requests
from bs4 import BeautifulSoup as soup
from itertools import cycle
from glob import glob

def socks4_list():
    proxy_urls = 'https://www.socks-proxy.net/'
    response = requests.get(proxy_urls)
    bsobj = soup(response.content)

    proxies= set()
    #this will create a list of socks4 proxies
    for ip in bsobj.findAll('table')[0].findAll('tbody')[0].findAll('tr'):
        cols = ip.findChildren(recursive = False)
        cols = [element.text.strip() for element in cols]
        proxy = ':'.join([cols[0],cols[1]])
        proxy = 'socks4://'+proxy
        proxies.add(proxy)

    proxy_pool = cycle(proxies)
    url = 'https://httpbin.org/ip'
    working_proxies= []
    while len(working_proxies)<1:
        for i in range(1,10):
            #Get a proxy from the pool
            proxy = next(proxy_pool)
            print("Request #%d"%i)
            try:
                response = requests.get(url,proxies={"http": proxy, "https": proxy})
                working_proxies += [proxy]
                print(response.json())
            except:
                print("Skipping. Connnection error")
        if len(working_proxies)>0:
            print("We got proxies to work with. Let's go!")
        else:
            print("We couldn't find proxies to work with. Let's try again")

    return working_proxies

def url_response(url_list):
    socks4 = socks4_list()
    session = requests.session()
    iteration_number= 0
    while True:
        try:
            session.proxies = {
                'http': socks4[iteration_number],
                'https': socks4[iteration_number]
            }
            available_urls = []
            unavailable_urls = []
            for url in url_list:
                r = requests.get(url)
                if r.status_code == 200:
                    available_urls += [url]
                else:
                    unavailable_urls += [url]
            break
        except:
            iteration_number += 1
            if iteration_number > len(socks4):
                socks4 = socks4_list()
            print('We got a proxy error while validating. Lets try another')

    return available_urls, unavailable_urls


csv_files = glob('./scraping/*.csv')
urls = []
for csv in csv_files:
    temp = pd.read_csv(csv)
    temp = list(temp)
    for i in temp:
        if (i[:8] == 'https://') | (i[:7] == 'http://'):
            urls += [i]
        else:
            pass


available, unavailable = url_response(urls)





