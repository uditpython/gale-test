import threading
import urllib2
import time


start = time.time()
urls = ["http://www.google.com", "http://www.google.com", "http://www.google.com", "http://www.google.com", "http://www.google.com"]
print(urls)
def fetch_url(url):
    urlHandler = urllib2.urlopen(url)
    html = urlHandler.read()
    print "'%s\' fetched in %ss" % (url, (time.time() - start))

threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print "Elapsed Time: %s" % (time.time() - start)
