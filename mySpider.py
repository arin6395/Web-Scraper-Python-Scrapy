import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import re
import json
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import os
#os.environ["PATH"] += os.pathsep + 'D:/Program Files (x86)/Graphviz-2.38/bin/'
import pandas as pd

covered_URLS=set()
open('datatea.txt', 'w').close()

inputs=pd.read_csv('input.csv')
print(inputs.head(5))
inputs.columns = [c.replace(' ', '_') for c in inputs.columns]

baseURL=inputs.Starting_URL[0]
regex=baseURL+".+"
domain=inputs.Domain[0]
DTM_Css_Handle=inputs.DTM_CSS_handle[0]

if baseURL=="list":
    pages=inputs.Starting_URL.tolist()
pages.remove('list')
print(pages)


class mySpider(scrapy.Spider):
    name = "mySpider"
    start_urls = [baseURL]
    covered_URLS.add(baseURL)
    allowed_domains=[domain]
    rules = [
        Rule(LinkExtractor(allow=[regex]), callback='parse', follow=True),
    ] 

    def parse(self, response):

        URL_SELECTOR = '::attr(href)'
        DTM_SELETOR = DTM_Css_Handle


        if response.css(DTM_SELETOR).extract_first():
        	URL=response.url
        	DTMheader=response.css(DTM_SELETOR).extract_first()
        else:
        	URL=response.request.url
        	DTMheader="none found"

        yield{
            'URL': URL,
            'DTMheader': DTMheader
        }
       

        for next_page in response.css('a ::attr(href)').extract():
            next_page=next_page.split("?")[0]
            if next_page and next_page.find(domain)>-1 and not(next_page in covered_URLS):
                covered_URLS.add(next_page)
                next_page = response.urljoin(next_page)
                yield scrapy.Request(url=next_page, callback=self.parse)

class listSpider(scrapy.Spider):
    name = "listSpider"
    
    start_urls=pages
    allowed_domains=[domain]
    rules = [
        Rule(LinkExtractor(allow=[regex]), callback='parse', follow=True),
    ] 

    def parse(self, response):
            DTM_SELETOR = DTM_Css_Handle
            if response.css(DTM_SELETOR).extract_first():
                URL=response.url
                DTMheader=response.css(DTM_SELETOR).extract_first()
            else:
                URL=response.request.url
                DTMheader="none found"

            yield{
                'URL': URL,
                'DTMheader': DTMheader
            }
            


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'datatea.txt'
})

if baseURL!="list":
    process.crawl(mySpider)
else:
    process.crawl(listSpider)

process.start() # the script will block here until the crawling is finished

data=[]
with open('datatea.txt') as json_file:  
    data = json.load(json_file)

pages_without_script=[]
pages_crawled=[]
DTM_scripts=[]

for x in data:
	if(x['DTMheader']=="none found"):
		pages_without_script.append(x['URL'])
	pages_crawled.append(x['URL'])
	DTM_scripts.append(x['DTMheader'])	

print(pages_without_script)
df_noscript=pd.DataFrame(pages_without_script)
df_noscript.to_csv('URLs without DTM Script.csv')
pages_crawled_scripts={
	'URL':pages_crawled,
	'DTM Script': DTM_scripts
}
df_crawled=pd.DataFrame(pages_crawled_scripts,columns= ['URL', 'DTM Script'])
df_crawled.to_csv('All URLs and Scripts.csv')

'''
a=[0]*100
k=0
a[k]=Node(domain)
nodeDict={
	domain:0
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


DotExporter(a[0]).to_picture("Sitemap.png")

'''