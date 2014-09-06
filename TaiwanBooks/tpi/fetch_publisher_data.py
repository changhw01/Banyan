from bs4 import BeautifulSoup
import urllib2
import time
import random
import json, codecs

url_root = 'http://book.tpi.org.tw/'
url_publisher = 'http://book.tpi.org.tw/search_publishing.php?action=list&page='

publishers = []
for i_page in xrange(1, 135):
  url = url_publisher + str(i_page)
  response = urllib2.urlopen(url)
  html = response.read()
  raw = BeautifulSoup(html)

  count = 0
  for tr in raw.body.find_all('tr', class_='table_trA'):
    publisher = {}
    tds = tr.find_all('td')
    try:
      h = tds[0].find('a')
      publisher['tpi-uri'] = h['href']
      publisher['name'] = h.text
    except:
      print tr

    try:
      publisher['phone'] = tds[1].text
    except:
      print tr

    try:
      publisher['publisher-url'] = tds[2].text
    except:
      print tr

    try:
      publisher['e-mail'] = tds[3].text
    except:
      print tr
    publishers.append(publisher)
    count += 1
  print 'extract %d books from page %d' % (count, i_page)
  time.sleep(random.randint(1, 4))

fout = codecs.open('publishers_list.json', encoding='utf-8', mode='w')
for publisher in publishers:
  fout.write(json.dumps(publisher, ensure_ascii=False) + '\n')
fout.close()
