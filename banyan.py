class Banyan:
  def __init__(self, dir_context):
    # data is stored as a dict of ('schema_class_name', [obj])
    self.data = {}
    # key: 'schema_class_name', value: context obj
    self.context = {}
    self.dir_context = dir_context

  def LoadContextFromFile(self, class_name):
    pass

  def AddDataInstance(self, data_class_name, **properties):
    if data_class not in self.data:
      LoadContextFromFile(data_class_name)
      self.data[data_class] = []
    # Note the properties not declared in the context will be dropped,
    # so please make sure every properties are defined properly.
    # TODO: Add more detailed data type validation, and do extension instead
    # of overwriting.
    instance = dict([(k,v) for k,v in properties.iteritems()
                     if k in self.context])
    # TODO: Check basic info, if missing some basic info, drop it.
    self.data[data_class].append(instance)
