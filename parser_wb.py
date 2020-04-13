from bs4 import BeautifulSoup
import requests 
import csv
import logging
import collections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
	'ParseResult', 
	(
		'brand_name',
		'goods_name',
		'url'
	)
)

HEADERS = ( # headers of table
	'Бренд',
	'Товар',
	'Ссылка',
)

class Client:
	def __init__(self, page):
		self.page = page
		self.session = requests.Session() # creating params of requests
		self.headers = { 
		'accept':'*/*','user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
		self.result = []

	def load_page(self): # loading page in according to url
		url ='https://www.wildberries.by/catalog/obuv/muzhskaya/kedy-i-krossovki?page={}'.format(self.page)
		res = self.session.get(url  = url)
		res.raise_for_status()
		return res.content

	def parser_page(self, text: str): # parser of main page
		soup = BeautifulSoup(text, 'lxml')
		container = soup.select('div.dtList.i-dtList.j-card-item')
		#logger.debug(container)

		if len(container) == 0: # verification last page through exceptions
			return  1/0

		for block in container:
			self.parcer_block(block=block)

	def parcer_block(self, block): # parser info from each part of block (from main container)
			url_block = block.select_one('a.ref_goods_n_p') #
			url = url_block.get('href')

			name_block = block.select_one('div.dtlist-inner-brand-name')
			brand_name = name_block.select_one('strong.brand-name')	 # choosing appropriate part of block
			brand_name = brand_name.text                             # getting info
			brand_name = brand_name.replace('/','').strip()          # convert info

			goods_name = name_block.select_one('span.goods-name')
			goods_name = goods_name.text
			goods_name = goods_name.replace('/','').strip()

			self.result.append(ParseResult( # add information  for further actions
				url = url,
				brand_name = brand_name,
				goods_name = goods_name,
			))
			logger.debug('%s, %s, %s', url, brand_name, goods_name) # cheking current state
			logger.debug('='*100)

	def save_results(self): # saving results in csv 
		path = '/home/vasiliy/Project/wildbik.csv' # path to csv
		with open(path,'a') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
			if self.page == 1 : # write headers only once
				writer.writerow(HEADERS) # write  headers into table
				for item in self.result: # continue parser page
					writer.writerow(item)
			else:
				for item in self.result:
					writer.writerow(item)
		logger.info('{} page(s) passed!'.format(self.page))

	def run(self): # run script
		text = self.load_page()
		self.parser_page(text=text)
		self.save_results()

if __name__ == '__main__':
	page = 1
	while True:
		try :
			parser = Client(page)
			parser.run()
			page +=1
		except ZeroDivisionError :
			logger.info('Process has hinished!')
			break
