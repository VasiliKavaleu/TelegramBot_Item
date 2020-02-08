from bs4 import BeautifulSoup
import requests 
import csv
import logging
import collections

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
	'ParseResult', 
	(
		'brand_name',
		'goods_name',
		'url'
	)
)

HEADERS = (
	'Бренд',
	'Товар',
	'Ссылка',
)

class Client:

	def __init__(self):
		self.session = requests.Session() # creating params of requests
		self.headers = { 
		'accept':'*/*','user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
		self.result = []

	def load_page(self): # loading page in according to url
		url ='https://www.wildberries.by/catalog/obuv/muzhskaya/kedy-i-krossovki'
		res = self.session.get(url  = url)
		res.raise_for_status()
		return res.content

	def parser_page(self, text: str): # parser of main page
		soup = BeautifulSoup(text, 'lxml')
		container = soup.select('div.dtList.i-dtList.j-card-item')
		#logger.info(container)
		print(container)
		for block in container:
			self.parcer_block(block=block)

	def parcer_block(self, block): # parser info from each part of block (from main container)
			#logger.info(block)
			#logger.info('='*100)

			url_block = block.select_one('a.ref_goods_n_p') # cheking if info is
			if not url_block:
				logger.error('no url_block')

			url = url_block.get('href')
			if not url:
				logger.error('no href')
				return

			name_block = block.select_one('div.dtlist-inner-brand-name')
			if not name_block:
				logger.error(f'no name_block on {url}')
				return

			brand_name = name_block.select_one('strong.brand-name')
			if not name_block:
				logger.error(f'no name_block on {url}')
				return


			brand_name = brand_name.text # convert info 
			brand_name = brand_name.replace('/','').strip()

			goods_name = name_block.select_one('span.goods-name')
			if not name_block:
				logger.error(f'goods_name on {url}')
				return

			goods_name = goods_name.text
			goods_name = goods_name.replace('/','').strip()

			

			self.result.append(ParseResult( # add information (list) for further actions
				url = url,
				brand_name = brand_name,
				goods_name = goods_name,
			))
			logger.debug('%s, %s, %s', url, brand_name, goods_name) # cheking current state
			logger.debug('='*100)

	def save_results(self): # saving results in csv 
		path = '/home/vasiliy/Project/wildbik.csv' # path to csv
		with open(path,'w') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
			writer.writerow(HEADERS) # write info with headers of table
			for item in self.result:
				writer.writerow(item)

	def run(self): # run script
		text = self.load_page()
		self.parser_page(text=text)
		self.save_results()


if __name__ == '__main__':
	parser = Client()
	parser.run()