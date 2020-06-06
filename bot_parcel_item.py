from selenium import webdriver
from bs4 import BeautifulSoup
import telebot
import config  
import re
import os

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
        path = os.path.abspath('bot_parcel_item.py')
        base_dir = os.path.dirname(path)
        path_chromedriver = os.path.join(base_dir, 'chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  
        browser = webdriver.Chrome(executable_path=path_chromedriver, options=options)
        browser.get(url)  
        requiredHtml = browser.page_source 
        return requiredHtml

    def exploring_page(self, page):  
        soup = BeautifulSoup(page, 'lxml')
        row_parsel = soup.select('div.show_nogroups')
        
        for point in row_parsel:  
            points_of_arrivel = point.find_all('div', attrs={'class': 'stage'})
            
            for block in points_of_arrivel:  
                title = block.find('div', attrs={'class': 'col-12 col-md-8 statuses-block'})
                if title == None:  
                    pass
                else:
                    info_about_po = title.h4['data-lang-ru']  
                    getting_time = block.find('div', attrs={'class': 'col-12 col-md-2 stage-timing stage-transit'})
                    time = getting_time.select_one('p.date').text
                    self.result = self.result + time + ' ' + info_about_po + '\n'  
        return self.result

    def run(self):  
        page = self.load_page()
        finish = self.exploring_page(page=page)
        return finish

bot.polling(none_stop=True)
