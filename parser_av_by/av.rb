require 'curb'
require 'nokogiri'
require 'ruby-progressbar'
require 'csv'

url = 'https://cars.av.by/volkswagen/page/5'
name_of_file = 'auto'


CSV.open("#{name_of_file}.csv","w") do |wr|           # init csv with headers
	wr << ["Model", "Year", "Price", "Link"]
end



def load(url)										# func of loading 
	http = Curl.get(url) do |http|                    
		http.headers['User-Agent']="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"
	end
	html = Nokogiri::HTML.parse(http.body_str)
	return html
end



def save_csv(data, name_of_file)					# func of saving to csv
	CSV.open("#{name_of_file}.csv","a") do |ap|           
		ap << data
	end
end


def parcer_page(url, name_of_file)				# parsers func

	html = load(url)
	
	model = html.xpath("//div[@class='listing-item-main']/div[@class='listing-item-title']//a/@href").each do |href|
		html = load(href)
		data = []
		model = html.xpath("//div[@class='card-header']/h1").text.split(',')[0].strip()
		year = html.xpath("//div[@class='card-header']/h1").text.split(',')[1].strip()
		price = html.xpath("//div[@class='card-price-main']/span[@class='card-price-main-secondary']").text().strip()
		data << model
		data << year
		data << price
		data << href

		save_csv(data, name_of_file)

	end
	
end

parcer_page(url, name_of_file)