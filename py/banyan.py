import util

class BaseType(object):
  def __init__(self, resource=None, label=None, comment=None):
    self.resource = resource
    self.label = label
    self.comment = comment


class EnumType(BaseType):
  def __init__(self, resource=None, label=None, comment=None):
    super(EnumType, self).__init__(resource, label, comment)


class SchemaClass(BaseType):
  def __init__(self, resource=None, label=None, comment=None, subClass=None,
               superClass=None, properties=None):
    super(SchemaClass, self).__init__(resource=resource, label=label,
                                      comment=comment)
    self.subClass = subClass
    self.superClass = superClass
    self.properties = properties
    self.ENUM = None


class SchemaProperty(BaseType):
  def __init__(self, resource=None, label=None, comment=None,
               property_domain=None, property_range=None):
    super(SchemaProperty, self).__init__(resource=resource, label=label,
                                         comment=comment)
    self.property_domain = property_domain
    self.property_range = property_range


class Banyan:
  _kRange = 'http://schema.org/rangeIncludes'
  _kDomain = 'http://schema.org/domainIncludes'

  def __init__(self, schema_org_rdfa=None, dir_local_schema=None):
    self.schema_class = {}
    self.schema_property = {}
    if schema_org_rdfa:
      InitFromSchemaOrg(schema_org_rdfa=schema_org_rdfa)
    if dir_local_schema:
      pass

  def InitFromSchemaOrg(self, schema_org_rdfa='../schema/schema_org_rdfa.html'):
    schema_raw = util.GetSchemaFromRDFa(schema_org_rdfa)
    #---------------------- Setup SchemaClass ----------------------#
    for entry in schema_raw['rdfs:Class']:
      entry_id = entry['resource']
      schema_class = SchemaClass(
          resource=entry_id, label={'en':entry['rdfs:label']},
          comment={'en':entry['rdfs:comment']})
      if 'rdfs:subClassOf' in entry:
        schema_class.superClass=entry['rdfs:subClassOf']
      self.schema_class[entry_id] = schema_class

    # Add subClass
    for class_id,entry in self.schema_class.iteritems():
      if entry.superClass:
        for super_class in entry.superClass:
          if not self.schema_class[super_class].subClass:
            self.schema_class[super_class].subClass = []
          self.schema_class[super_class].subClass.append(class_id)

    # Set up ENUM
    # We do this before SchemaProperty so that we can add enum.
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
            comment={'en':entry['rdfs:comment']})

    #------- Setup SchemaProperty -------#
    for entry in schema_raw['rdf:Property']:
      entry_id = entry['resource']
      schema_property = SchemaProperty(
          resource=entry_id, label={'en':entry['rdfs:label']},
          comment={'en':entry['rdfs:comment']})
      if self._kDomain in entry:
        schema_property.property_domain = entry[self._kDomain]
        for domain_id in entry[self._kDomain]:
          if not self.schema_class[domain_id].properties:
            self.schema_class[domain_id].properties = []
          self.schema_class[domain_id].properties.append(entry_id)
      if self._kRange in entry:
        schema_property.property_range = entry[self._kRange]
      self.schema_property[entry_id] = schema_property
