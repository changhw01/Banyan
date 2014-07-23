from bs4 import BeautifulSoup
import json, codecs

class BaseType(object):
  def __init__(self, resource=None, label=None, comment=None, _type=None):
    self.resource = resource
    self.label = label
    self.comment = comment
    self._type = _type


class EnumType(BaseType):
  def __init__(self, resource=None, label=None, comment=None, _type=None):
    super(EnumType, self).__init__(resource=resource, label=label,
                                   comment=comment, _type=_type)


class SchemaClass(BaseType):
  def __init__(self, resource=None, label=None, comment=None, sub_class=None,
               super_class=None, properties=[], _type=None):
    super(SchemaClass, self).__init__(resource=resource, label=label,
                                      comment=comment, _type=_type)
    self.sub_class = sub_class
    self.super_class = super_class
    self.properties = properties
    self.ENUM = None


class SchemaProperty(BaseType):
  def __init__(self, resource=None, label=None, comment=None,
               property_domain=None, property_range=None, _type=None):
    super(SchemaProperty, self).__init__(resource=resource, label=label,
                                         comment=comment, _type=_type)
    self.property_domain = property_domain
    self.property_range = property_range


class SchemaOrg:
  _kRange = u'http://schema.org/rangeIncludes'
  _kDomain = u'http://schema.org/domainIncludes'
  _kSchemaOrg = u'http://schema.org/'

  def __init__(self, schema_org_rdfa=None, dir_local_schema=None):
    self.schema_class = {}
    self.schema_property = {}
    if schema_org_rdfa:
      InitFromSchemaOrg(schema_org_rdfa=schema_org_rdfa)
    if dir_local_schema:
      pass

  def ParseRDFa(self, fn_rdfa, debug=False):
    '''Convert the raw schema.org RDFa html to json objects.'''
    html = BeautifulSoup(open(fn_rdfa).read())
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
        if debug:
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

  def InitFromSchemaOrg(self, schema_org_rdfa='../schema/schema_org_rdfa.html',
                        debug=False):
    schema_raw = self.ParseRDFa(schema_org_rdfa, debug)

    #---------------------- Setup SchemaClass ----------------------#
    for entry in schema_raw['rdfs:Class']:
      entry_id = entry['resource']
      schema_class = SchemaClass(
          resource=entry_id, label={'en':entry['rdfs:label']},
          comment={'en':entry['rdfs:comment']}, _type='rdfs:Class')
      if 'rdfs:subClassOf' in entry:
        schema_class.super_class=entry['rdfs:subClassOf']
      self.schema_class[entry_id] = schema_class

    # Add sub_class
    for class_id,entry in self.schema_class.iteritems():
      if entry.super_class:
        for super_class in entry.super_class:
          if not self.schema_class[super_class].sub_class:
            self.schema_class[super_class].sub_class = []
          self.schema_class[super_class].sub_class.append(class_id)

    # Set up ENUM
    enum_properties = set()
    for entry_type,entries in schema_raw.iteritems():
      if (entry_type == 'rdfs:Class' or entry_type == 'rdf:Property' or
          entry_type not in self.schema_class):
        continue
      target_class = self.schema_class[entry_type]
      for entry in entries:
        entry_id = entry['resource']
        if not target_class.ENUM:
          target_class.ENUM = {}
        target_class.ENUM[entry_id] = EnumType(
            resource=entry_id, label={'en':entry['rdfs:label']},
            comment={'en':entry['rdfs:comment']}, _type=entry_type)

    #------- Setup SchemaProperty -------#
    for entry in schema_raw['rdf:Property']:
      entry_id = entry['resource']
      schema_property = SchemaProperty(
          resource=entry_id, label={'en':entry['rdfs:label']},
          comment={'en':entry['rdfs:comment']}, _type='rdf:Property')
      if self._kDomain in entry:
        schema_property.property_domain = entry[self._kDomain]
        for domain_id in entry[self._kDomain]:
          if not self.schema_class[domain_id].properties:
            self.schema_class[domain_id].properties = []
          self.schema_class[domain_id].properties.append(entry_id)
      if self._kRange in entry:
        schema_property.property_range = entry[self._kRange]
      self.schema_property[entry_id] = schema_property

  def GetPropertyContext(self, prop_uri, class_uri=None, debug=False):
    prop = self.schema_property[prop_uri]
    context = {'@id': prop.resource}
    if class_uri:
      context['inherit_from'] = class_uri
    if len(prop.property_range) == 1:
      prop_range = prop.property_range[0]
      range_id = prop_range.split('/')[-1]
      context['@type'] = prop_range
      if range_id == 'Text':
        context['@container'] = '@language'

    return context

  def _AddSuperClassProperty(self, super_class, context, debug=False):
    for class_uri in super_class:
      class_obj = self.schema_class[class_uri]
      for prop_uri in class_obj.properties:
        prop = self.schema_property[prop_uri]
        context[prop.label['en']] = self.GetPropertyContext(
            prop_uri, class_uri, debug)
      if class_obj.super_class:
        self._AddSuperClassProperty(class_obj.super_class, context, debug)
      if debug:
        print('Add properties from Class: %s'%class_uri)

  def CreateClassContext(self, class_uri, debug=False):
    class_obj = self.schema_class[class_uri]
    context = {
      '@type': class_obj.resource,
      'label': {
        '@id': 'rdfs:label',
        '@container': '@language'
      }
    }
    if class_obj.super_class:
      self._AddSuperClassProperty(class_obj.super_class, context, debug)
    for prop_uri in class_obj.properties:
      prop = self.schema_property[prop_uri]
      context[prop.label['en']] = self.GetPropertyContext(prop_uri)

    return context

  def OutputClassContextInJson(self, class_uri, fn_out=None):
    if 'http://schema.org/' not in class_uri:
      class_uri = 'http://schema.org/' + class_uri
    context = self.CreateClassContext(class_uri, debug=False)

    if fn_out is None:
      fn_out = class_uri.split('/')[-1] + '.json'
    fout = codecs.open(fn_out, encoding='utf-8', mode='w')
    fout.write(json.dumps(context, sort_keys=True, indent=2,
               separators=(',', ': '), ensure_ascii=False))
    fout.close()
