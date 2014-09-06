#for i_page in xrange(30001, 36001):
import urllib, urllib2
import time
import random
import json, codecs
from bs4 import BeautifulSoup
import socket
socket.setdefaulttimeout(30)

url_book = 'http://book.tpi.org.tw/bookinfo.php?cID='

fout = codecs.open('books/books.json', encoding='utf-8', mode='a')
log_book_info = open('books/log_book.txt', 'a')
err_book_info = open('books/err_book.txt', 'a')
log_book_cover = open('books/log_cover.txt', 'a')
err_book_cover = open('books/err_cover.txt', 'a')

# 9/5 11:56PM 312000-311842
# 9/6 00:11AM 311841-300000
for i_page in xrange(311841, 300000, -1):
  url = url_book + str(i_page)
  try:
    response = urllib2.urlopen(url, timeout=30)
    html_body = BeautifulSoup(response.read()).body
  except:
    print('Failed to retrieve tpi: %s', i_page)
    err_book_info.write(str(i_page) + '\n')
    continue

  # There should be two tables.
  tables = html_body.find_all('table')
  if len(tables) < 2:
    print('Failed to retrieve tpi: %s', i_page)
    err_book_info.write(str(i_page) + '\n')
    continue

  book = {'tpi-index': i_page}
  tds = tables[0].find_all('td')
  try:
    book['img_src'] = tds[0].find('img')['src']
  except:
    book['img_src'] = ''
  try:
    book['name'] = tds[1].find('div').text
  except:
    book['name'] = ''
  book['ISBN'] = tds[3].text
  book['EAN'] = tds[5].text
  book['CIP'] = tds[7].text
  book['lang'] = tds[9].text
  book['author'] = tds[11].text
  book['translator'] = tds[13].text
  book['numPages'] = tds[15].text
  book['size'] = tds[17].text
  book['binding'] = tds[19].text
  book['control'] = tds[21].text
  book['publisher'] = tds[23].text
  try:
    book['publisher_url'] = tds[23].find('a')['href']
  except:
    book['publisher_url'] = ''
  book['publishDate'] = tds[25].text
  book['price'] = tds[27].text

  for a in html_body.find_all('a'):
    if a['href'].startswith('http://www.ucd.com.tw/stk/stk_detail.jsp?stk_c='):
      book['book_info_url'] = a['href']

  book['channels'] = []
  trs = tables[1].find_all('tr')
  for i in range(1, len(trs)):
    tds = trs[i].find_all('td')
    book['channels'].append({
      'company': tds[0].text,
      'phone': tds[1].text,
      'e-mail': tds[2].text,
      'company_url': tds[3].text
      })

  fout.write(json.dumps(book, ensure_ascii=False) + '\n')

  log_str = str(i_page) + '\n'
  print('Fetched book: %s' % log_str[:-1])
  log_book_info.write(log_str)

  if book['img_src']:
    try:
      urllib.urlretrieve(book['img_src'],
                         'books/covers/' + book['ISBN'] + '.jpg')
      print('Fetched cover: %s' % log_str[:-1])
      log_book_cover.write(log_str)
    except:
      err_book_cover.write(log_str)

  if i_page % 3 == 0:
    time.sleep(random.randint(1, 2))

fout.close()
log_book_info.close()
log_book_cover.close()
err_book_info.close()
err_book_cover.close()
