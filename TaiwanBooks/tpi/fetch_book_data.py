from bs4 import BeautifulSoup
import urllib2
import time
import random
import json, codecs

url_book = 'http://book.tpi.org.tw/bookinfo.php?cID='
books = []
i_file = 101
# To 33601
for i_page in xrange(30001, 36001):
  url = url_book + str(i_page)
  try:
    response = urllib2.urlopen(url)
    html_body = BeautifulSoup(response.read()).body
  except:
    print('Stop at %d' % i_page)
    break

  # There should be two tables.
  tables = html_body.find_all('table')
  if len(tables) < 2:
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

  books.append(book)
  print('Fetch book %d %s' % (i_page, book['name']))

  if i_page % 5 == 0:
    time.sleep(random.randint(1, 3))
  if i_page % 300 == 0:
    fout = codecs.open('books/book_%d.json' % i_file,
                       encoding='utf-8', mode='a')
    for book in books:
      fout.write(json.dumps(book, ensure_ascii=False) + '\n')
    fout.close()
    books = []
    i_file += 1

if books:
  fout = codecs.open('books/book_%d.json' % i_file, encoding='utf-8', mode='a')
  for book in books:
    fout.write(json.dumps(book, ensure_ascii=False) + '\n')
  fout.close()
