import urllib
import urllib2
import urlparse
import codecs
import re
import time
import sys

from Queue import Queue, Empty as QueueEmpty
from bs4 import BeautifulSoup

def establish_connection(url):
	""" 
	 This function tries to establish connection to a specified URL.
	 
	 Args:
        param1 (str): The URL string to which connection has to be established.

    Returns:
        bool: The return value. True for success, False otherwise. 
	"""
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	values = {'name':'Harsha', 'location':'Boston', 'language':'Python'}
	headers = {'User-Agent': user_agent}
	data = urllib.urlencode(values)
	url_connect = ""
	#time.sleep(1)
	request = urllib2.Request(url,headers=headers)
	try:
	   response = urllib2.urlopen(request)
	   url_connect = response.read()
	except Exception as e:
		print e.reason	
		pass

	return url_connect

def crawl_web(url_connect, keyphrase):
	"""
	 This function tries to get the list of outlink URL's from a specified URL if a specified 
	 keyphrase is present in the given webpage and an empty list if the keyphrase is missing.
	 
	 If keyphrase is not mentioned returns list of all the outlinks.
	 
	 Args:
        param1 (str): Entire webpage content as string.
		param2 (str): The keyphrase to be searched.
		
    Returns:
        list: The list of outlink URL's from the given webpage.
	"""
	if not url_connect:
		print 'The URL is empty'
		return list()
	
	soup = BeautifulSoup(url_connect)
	
	if keyphrase != None: 
		if re.search(keyphrase, str(soup), re.IGNORECASE) != None:
			return get_crawled_pages(soup)
		else:
			return list()
	else:
		return get_crawled_pages(soup)
	
def get_crawled_pages(soup):
	"""
	 This function tries to get the list of outlink URL's from a given webpage content.
	 
	 Args:
        param1 (BeautifulSoup): Entire webpage content as a BeautifulSoup object.
		
    Returns:
        list: The list of outlink URL's from the given webpage.
	"""

	list_url = []
	for url in soup.find_all('a', href = True):
		url_search =  url.get('href')
		url_crawled = url_search.encode('utf-8')
		
		if not url_crawled:
			continue

		if url_crawled.startswith('/wiki'):
			if (url_crawled.find(':') == -1) and (url_crawled != "/wiki/Main_Page"):
				url_crawled = urlparse.urljoin("http://en.wikipedia.org",url_crawled)
				url_crawled, fragment = urlparse.urldefrag(url_crawled)
				list_url.append(url_crawled)	

		else:
			if url_crawled.startswith('http://en.wikipedia.org'):
				if url_crawled != "http://en.wikipedia.org/wiki/Main_Page":
					url_search = url_crawled.lstrip("http://en")
					if url_search.find(':') == -1:
						url_crawled, fragment = urlparse.urldefrag(url_crawled)
						list_url.append(url_crawled)

	return list_url

def main(argv):
	num_args = len(sys.argv)
	input_url = sys.argv[1]
	list_urls_crawled = []
	url_queue = []
	
	if num_args == 2:
		keyphrase = None
	else:
		keyphrase = sys.argv[2]
		keyphrase = keyphrase.encode('utf-8')
		
	url_queue.append(input_url)
	depth = 1

	while depth <= 4:
		print depth
		iter_list = []
		
		for url in url_queue:
			if len(list_urls_crawled) >= 1000:
				break
			if list_urls_crawled.count(url) >= 1:
				continue
			else:
				web_page = establish_connection(url)
				if not web_page:
					print url + "Webpage not found"
					continue
					
				list_temp_url = crawl_web(web_page, keyphrase)
				if len(list_temp_url) > 0:
					list_urls_crawled.append(url)
					#print url + " : " + str(len(list_urls_crawled))
				iter_list.extend(list_temp_url)
				
		if len(list_urls_crawled) >= 1000:
			break

		url_queue = list(iter_list)
		depth = depth + 1
		
	f = codecs.open("./Links_Crawled.txt","w","utf-8")
	for url in list_urls_crawled:
		f.write(url.decode('utf-8'))
		f.write("\n")
	f.close()

if __name__ == "__main__":
   main(sys.argv)