from bs4 import BeautifulSoup
import json, codecs

def GetSchemaFromRDFa(fn_html='../schema/schema_org_rdfa.html'):
  '''Convert the raw schema.org RDFa html to json objects.'''
  html = BeautifulSoup(open(fn_html).read())
  html = html.body

  div_class = html.find_all('div')
  schema = {}
  for div in div_class:
    if div['typeof'] not in schema:
      schema[div['typeof']] = []

    # Basic info
    div_dict = {}
    try:
      div_dict['rdfs:label'] = div.find(property='rdfs:label').text
      div_dict['resource'] = div['resource']
    except:
      print(div)
      continue

    div_dict['@type'] = div['typeof']
    if div.find(property='rdfs:comment'):
      div_dict['rdfs:comment'] = div.find(property='rdfs:comment').text
    # For class
    if div['typeof'] == 'rdfs:Class':
      for a in div.find_all(property='rdfs:subClassOf'):
        div_dict.setdefault('rdfs:subClassOf', []).append(a['href'])

    # For properties
    if div['typeof'] == 'rdf:Property':
      for a in div.find_all(property='http://schema.org/domainIncludes'):
        div_dict.setdefault('http://schema.org/domainIncludes', []).append(
            a['href'])
      for a in div.find_all(property='http://schema.org/rangeIncludes'):
        div_dict.setdefault('http://schema.org/rangeIncludes', []).append(
            a['href'])

    # Append
    schema[div['typeof']].append(div_dict)

    # schema.org has some format problem, the following codes try to correct
    # them.
    map_category_type = 'MapCategoryType'
    map_category_uri = 'http://schema.org/' + map_category_type
    if map_category_type in schema:
      for entity in schema[map_category_type]:
        entity['typeof'] = map_category_uri
      schema[map_category_uri] = schema[map_category_type]
      del schema[map_category_type]

  return schema
