import json, codecs

class Banyan:
  def __init__(self, dir_context='./context'):
    # data is stored as a dict of ('schema_class_name', [obj])
    self.data = {}
    # key: 'schema_class_name', value: context obj
    self.context = {}
    self.dir_context = dir_context

  def LoadContextFromFile(self, class_name):
    if class_name in self.context:
      return
    fn_in = './context/' + class_name + '.json'
    try:
      context = json.loads(codecs.open(fn_in, encoding='utf-8').read())
    except:
      print('Failed to load: %s'%fn_in)
      return
    self.context[class_name] = context

  def AddDataInstance(self, data_class_name, properties):
    if data_class_name not in self.data:
      self.LoadContextFromFile(data_class_name)
      self.data[data_class_name] = []
    # Note the properties not declared in the context will be dropped,
    # so please make sure every properties are defined properly.
    # TODO: Add more detailed data type validation, and do extension instead
    # of overwriting.
    # TODO: Change the codes to handle the case that v is a object.
    instance = dict([(k,v) for k,v in properties.items()
                     if k in self.context[data_class_name]])
    # TODO: Check basic info, if missing some basic info, drop it.
    self.data[data_class_name].append(instance)
