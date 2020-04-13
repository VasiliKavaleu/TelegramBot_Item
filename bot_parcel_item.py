from selenium import webdriver
from bs4 import BeautifulSoup
import telebot
import config
import re

bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=['text'])
def answer(message):
    t = '[A-Z]{2}[0-9]{9}[A-Z]{2}'
    if len(message.text) == 13 and re.match(t, message.text):  
        parsel_from_ali = parsel(message.text)
        bot.send_message(message.from_user.id, parsel_from_ali.run())  
    else:
        bot.send_message(message.from_user.id, 'Трек-номер не верный. Попробуйте еще раз.')

class parsel:
    def __init__(self, item_num):
        self.item_num = item_num  
        self.result = ''

    def load_page(self):
        url = 'https://1track.ru/tracking/' + '{}'.format(self.item_num)  
        chromedriver = '/bin/chromedriver'  
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  
        browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
        browser.get(url)  
        requiredHtml = browser.page_source 
        return requiredHtml

    def exploring_page(self, page):  # exploring html page
        soup = BeautifulSoup(page, 'lxml')
        row_parsel = soup.select('div.show_nogroups')
        
        # searchng points of arrivel
        for point in row_parsel:  
            points_of_arrivel = point.find_all('div', attrs={'class': 'stage'})
            
            # getting info about points of arrivel
            for block in points_of_arrivel:  
                title = block.find('div', attrs={'class': 'col-12 col-md-8 statuses-block'})
                # sorting advertisement
                if title == None:  
                    pass
                else:
                    # getting str about transfer
                    info_about_po = title.h4['data-lang-ru']  
                    getting_time = block.find('div', attrs={'class': 'col-12 col-md-2 stage-timing stage-transit'})
                    time = getting_time.select_one('p.date').text
                    # conversion to a single form
                    self.result = self.result + time + ' ' + info_about_po + '\n'  
        return self.result
    
    # manage func
    def run(self):  
        page = self.load_page()
        finish = self.exploring_page(page=page)
        return finish

bot.polling(none_stop=True)
