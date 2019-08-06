from anytree import Node, RenderTree
from anytree.exporter import DotExporter

a=[0]*100
k=0
a[k]=Node("www.nissan.co.uk")
nodeDict={
	"www.nissan.co.uk":0
	}
k=k+1
for x in covered_URLS:
	impURL=x.split('//')[1]
	levels=impURL.split('/')
	#print(levels)
	if len(levels)>70:
		continue
	for i in range(1,len(levels)):
		#print(levels[i])
		if nodeDict.get(levels[i],-1)==-1:
			#print(nodeDict[levels[i-1]])
			a[k]=Node(levels[i],parent=a[nodeDict[levels[i-1]]])
			
			nodeDict[levels[i]]=k
			k=k+1
			#print(nodeDict)
		else:
			continue

for pre, fill, node in RenderTree(a[0]):
    print("%s%s" % (pre, node.name))

# graphviz needs to be installed for the next line!
DotExporter(a[0]).to_dotfile('udo.dot')

from graphviz import Source
Source.from_file('udo.dot')

from graphviz import render
render('dot', 'png', 'udo.dot') 


DotExporter(a[0]).to_picture("udo.png")