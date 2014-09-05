import time, random
import json, codecs
import urllib
import socket
socket.setdefaulttimeout(30)

fns_repo = ['books_1to55/book_1to55.json',
            'books_61to112/book_61to112.json']

checked = set()
fin_log = open('book_covers/log_fetch_cover.txt')
for line in fin_log:
  checked.add(int(line.split('\t')[0]))
fin_log.close()

fout_error = open('book_covers/error_fetch_cover.txt', 'a')
fout_log = open('book_covers/log_fetch_cover.txt', 'a')
count = 0
for fn in fns_repo:
  fin = codecs.open(fn, 'r', 'utf-8')
  for line in fin:
    book = json.loads(line)
    log_str = str(book['tpi-index']) + '\t' + book['ISBN'] + '\n'
    url_img = book['img_src']
    if book['tpi-index'] in checked:
      print('Skip url: %s' % url_img)
      continue
    print('Try url: %s' % url_img)
    try:
      urllib.urlretrieve(url_img, 'book_covers/' + book['ISBN'] + '.jpg')
      print('Get cover image for book: %s' % log_str)
      fout_log.write(log_str)
      count += 1
      if count % 3 == 0:
        time.sleep(random.randint(1, 3))
    except:
      count += 1
      if count % 3 == 0:
        time.sleep(random.randint(1, 3))
      fout_error.write(log_str)
  fin.close()
fout_log.close()
fout_error.close()
