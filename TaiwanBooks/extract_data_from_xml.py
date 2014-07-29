import xml.etree.ElementTree as etree
import json, codecs

fn_xml = 'natlib-2014-May.xml'
tree = etree.parse(fn_xml)
Books = tree.getroot()

def extractYearDate(str_date):
  sp = [int(i) for i in str_date.split('/')]
  sp[0] = sp[0] + 1911
  return '%d/%d'%(sp[0], sp[1])

def parseISBN(str_isbn):
  sp = str_isbn[:-1].split(u'(')
  if len(sp) != 2:
    print('Incorrect ISBN format: ', str_isbn)
    return
  return [sp[0].strip()] + [s.strip() for s in sp[1].split(u',')]

fields = {'bookTitle': u'書名',
          'author': u'作者',
          'publisher': u'出版單位',
          'bookEdition': u'版次',
          'datePublished': u'出版年月',
          'libClassNum': u'類號',
          'isbn': u'ISBN'}

dataset = {'Books': [], 'BooksBrief': []}
for Book in Books:
  book = {}
  for k, v in fields.items():
    elm = Book.find(v)
    if elm is not None:
      if k == 'datePublished':
        value = extractYearDate(elm.text)
        book[k] = value
      elif k == 'isbn':
        res = parseISBN(elm.text)
        book['isbn'] = res[0]
        for value in res[1:]:
          if not value:
            continue
          if value[-1] == u'面':
            book['numberOfPages'] = value
          elif value[0] == u'N':
            book['listPrice'] = value
          elif value[-1] == u'分':
            book['bookSize'] = value
          else:
            book['bookBinding'] = value
      else:
        book[k] = elm.text
  dataset['Books'].append(book)

fields_brief = ['bookTitle', 'author', 'publisher', 'datePublished']
for book in dataset['Books']:
  book_brief = {}
  for field in fields_brief:
    if field in book:
      book_brief[field] = book[field]
  if book_brief:
    dataset['BooksBrief'].append(book_brief)

fout = codecs.open('natlib-brief-2014-5.json', encoding='utf-8', mode='w')
for book in dataset['BooksBrief']:
  fout.write(json.dumps(book, ensure_ascii=False) + '\n')
fout.close()

fout = codecs.open('natlib-2014-5.json', encoding='utf-8', mode='w')
for book in dataset['Books']:
  fout.write(json.dumps(book, ensure_ascii=False) + '\n')
fout.close()

