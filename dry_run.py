import banyan, json
from imp import reload
reload(banyan)

B = banyan.Banyan()
B.LoadContextFromFile('Book')
B.LoadContextFromFile('Person')
B.LoadContextFromFile('Organization')

# Load Books data.
fin = open('TaiwanBooks/natlib-2014-5.json')
for line in fin.readlines():
  book = json.loads(line)
  B.AddDataInstance('Book', book)
fin.close()
