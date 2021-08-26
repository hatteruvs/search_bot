import telebot
from lxml import html
from selenium import webdriver
from time import sleep

token = '1989653860:AAE9Akpw47arzPYeauOwWaTZlup2IrgnvYE'
bot = telebot.TeleBot(token)

""""Устанавливаем опцию headless, чтобы браузер запускался быстрее и без графического интерфейса"""
options = webdriver.FirefoxOptions()
options.headless = True

driver = webdriver.Firefox(options=options) #открываем браузер
"""Перед началой работы устанавливаем в открытом браузере опцию, которая отключает безопасный поиск"""
driver.get('https://duckduckgo.com/?q=cat')
safe_search = driver.find_element_by_link_text('Безопасный поиск: умеренный')
safe_search.click()
safe_search_off = driver.find_element_by_link_text('Выкл')
safe_search_off.click()


@bot.inline_handler(func=lambda query: len(query.query)>0)
def repeat_inline(query):
    try:
        offset = int(query.offset) if query.offset else 0 #считываем offset с запроса
        url = 'https://duckduckgo.com/?q=' + query.query + '&iax=images&ia=images'  #формируем url для поиска картинок
        if offset == 0:
            driver.get(url) #делаем запрос по url, но только единожды, пока offset еще меньше нуля
        driver.execute_script('window.scrollTo(0, ' + str(1000 + offset // 50 * 1500) + ')')    #при увеличении offset, прокручиваем страницу вниз
        sleep(1)    #сон 1 секунда, чтобы картинки успели прогрузиться
        htmlSource = driver.page_source #считываем код страницы
        images = html.fromstring(htmlSource).xpath('//img/@src')    #ищем в коде ссылки на изображения
        answers = []
        length = 50 if len(images) > 50 else len(images)    #если картинок больше 50, то будем выдавать их порциями
        """Формируем изображения для отправки в inline режиме"""
        for i in range(length):
            answer = telebot.types.InlineQueryResultPhoto(id=i+1+offset, thumb_url='https:'+images[i+offset],
                                                          photo_url='https:'+images[i+offset],
                                                          photo_width=512, photo_height=512)
            answers.append(answer)
        next_offset = str(offset + 50)  # увеличиваем offset при прокрутке пользователя
        """Отправляем сформированный ответ на запрос пользователя"""
        bot.answer_inline_query(query.id, answers, cache_time=10, next_offset=next_offset if next_offset else "")
    except Exception as e:
        print(e)

bot.polling()   #запуск бота