# import sendgrid
# from sendgrid.helpers.mail import *
import os
try:
    import chromedriver_binary
except ImportError:
    raise
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def create_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--lang=ja')


if __name__ == '__main__':
    # message = Mail(
    #     from_email=Email('from_address@example.com'),
    #     subject='fxpytradingトレード通知',
    #     to_emails=Email('ishikawa.toru@gmail.com'),
    #     html_content=Content('text/plain', 'テスト'),
    # )

    # # SendGrid の APIキー を使うが ここでは環境変数に入れている
    # # sg = sendgrid.SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
    # sg = sendgrid.SendGridAPIClient(
    #     apikey='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')
    # response = sg.client.mail.send.post(request_body=message.get())
    # print(response.status_code)


# message = Mail(
#     from_email='from_email@example.com',
#     to_emails='ishikawa.toru@gmail.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')
# try:
#     sg = SendGridAPIClient(
#         apikey='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')
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(e.message)

    # sg = sendgrid.SendGridAPIClient(api_key='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')
    # from_email = Email("info@pyfxtrading.com")
    # to_email = To("ishikawa.toru@gmail.com")
    # subject = "trading info mail"
    # content = Content("text/plain", "this is a mail from pyfxtrading")
    # mail = Mail(from_email, to_email, subject, content)
    # response = sg.client.mail.send.post(request_body=mail.get())
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('http://www.chikuwachan.com/twicas/')

    live_list = []
    for i in range(1, 10):
        title_selector = f'#ranking > div > ul > li:nth-child({i}) > div.content > a.liveurl > div.title'
        # title = driver.find_element_by_css_selector(title_selector)
        # print(title.text)
        topic_selector = f'#ranking > div > ul > li:nth-child({i}) > div.content > a.liveurl > div.topic'
        # topic = driver.find_element_by_css_selector(topic_selector)
        # print(topic.text)
        href_selector = f'#ranking > div > ul > li:nth-child({i}) > div.content > a.liveurl'
        # href = driver.find_element_by_css_selector(href_selector).get_attribute('href')
        # print(href)

        icon_selector = f'#ranking > div > ul > li:nth-child({i}) > div.content > a.liveurl > div.image_user > img'
        # icon = driver.find_element_by_css_selector(icon_selector).get_attribute('src')
        # print(icon)

        live = {
            'title': driver.find_element_by_css_selector(title_selector).text,
            'topic': driver.find_element_by_css_selector(topic_selector).text,
            'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
            'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('src')
        }
        live_list.append(live)
    for i in live_list:
        print(i)
    # live_df = pd.DataFrame(live_list)



        # 視聴者数を取得する方法？
        # try:
        #     viewers_selector = f'#ranking > div > ul > li:nth-child({i}) > div.watch.viewers.watch10000 > div.count'
        # except NoSuchElementException:
        #     viewers_selector = f'#ranking > div > ul > li:nth-child({i}) > div.watch.viewers.watch5000 > div.count'
        # viewers = driver.find_element_by_css_selector(viewers_selector)
        # print(viewers.text)

        # 放送時間を取得する方法？？
        # time_selector = f'#ranking > div > ul > li:nth-child({i}) > div.content > div.progress.progress180 > span:nth-child(1)'
        # f'#ranking > div > ul > li:nth-child({i}) > div.content > div.progress > span.count'
        # time = driver.find_element_by_css_selector(time_selector)
        # print(time.text)

