"""Banyan API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.

Check the api here: http://localhost:8080/_ah/api/explorer
"""
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

import json, codecs, collections

package = 'Banyan'


class Book(messages.Message):
  author = messages.StringField(1)
  bookEdition = messages.StringField(2)
  bookSize = messages.StringField(3)
  bookTitle = messages.StringField(4)
  datePublished = messages.StringField(5)
  isbn = messages.StringField(6)
  listPrice = messages.StringField(7)
  numberOfPages = messages.IntegerField(8)
  publisher = messages.StringField(9)

class BookCollection(messages.Message):
  """Collection of Books."""
  books = messages.MessageField(Book, 1, repeated=True)

def LoadBooks():
  # Load Books data.
  fin = codecs.open('natlib-2014-5.json', encoding='utf-8')
  books = []
  for line in fin.readlines():
    books.append(json.loads(line))
  fin.close()
  return books

def IndexByISBN(books_list):
  books_isbn = {}
  for book in books_list:
    if 'isbn' in book:
      books_isbn[book['isbn']] = book
  return books_isbn

def IndexByDate(books_list):
  books_date = collections.defaultdict(list)
  for book in books_list:
    if 'datePublished' in book:
      books_date[book['datePublished']].append(book)
  return books_date

def SortedByDate(book_dict):
  S =  sorted([(k, book_dict[k]) for k in book_dict], reverse=True)
  S = [tp[1] for tp in S]
  return [item for sublist in S for item in sublist]

class DateRequestMessageClass(messages.Message):
  date_after = messages.StringField(1)
  date_before = messages.StringField(2)

BOOKS_LIST = LoadBooks()
BOOKS_ISBN = IndexByISBN(BOOKS_LIST)
BOOKS_DATE = IndexByDate(BOOKS_LIST)
BOOKS_SORTED_BY_DATE = SortedByDate(BOOKS_DATE)

def BookJsonToMessage(book_json):
  book_msg = Book()
  for k in book_msg.all_fields():
    name = k.name
    if name in book_json:
      if name == 'numberOfPages':
        setattr(book_msg, name, int(book_json[name][:-1]))
      else:
        setattr(book_msg, name, book_json[name])
  return book_msg


@endpoints.api(name='banyan', version='v1')
class BanyanApi(remote.Service):
  """Banyan API v1."""
  QUERY_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    query_type = messages.StringField(1),
    n_newest = messages.IntegerField(2, variant=messages.Variant.INT32),
    isbn = messages.StringField(3),
    year = messages.StringField(4),
    year_month = messages.StringField(5),
    before_month = messages.StringField(6),
    after_month = messages.StringField(7))

  @endpoints.method(QUERY_RESOURCE, BookCollection,
                    path='book/{query_type}', http_method='GET',
                    name='banyan.getBook')
  def banyan_getbook_by_id(self, request):
    try:
      if request.query_type == 'isbn':
        result = [BOOKS_ISBN[request.isbn]]
      elif request.query_type == 'newest':
        result = BOOKS_SORTED_BY_DATE[:request.n_newest]
      elif request.query_type == 'date':
        if request.year:
          result = []
          for k in BOOKS_DATE:
            if k[:4] == request.year:
              result += BOOKS_DATE[k]
        elif request.year_month:
          result = []
          for k in BOOKS_DATE:
            if k == request.year_month:
              result += BOOKS_DATE[k]
        elif request.before_month:
          result = [b for b in BOOKS_SORTED_BY_DATE
                    if b['datePublished'] < request.before_month]
        elif request.after_month:
          result = [b for b in BOOKS_SORTED_BY_DATE
                    if b['datePublished'] > request.after_month]

      return BookCollection(books=[BookJsonToMessage(b) for b in result])

    except (IndexError, TypeError):
      raise endpoints.NotFoundException('Books not found.')


APPLICATION = endpoints.api_server([BanyanApi])
