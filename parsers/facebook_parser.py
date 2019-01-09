# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from apscheduler.schedulers.blocking import BlockingScheduler
# import time
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
#
# GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
# CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
#
# cloudinary.config(
#   cloud_name = "newskit",
#   api_key = "159113262954346",
#   api_secret = "Xx-kuwJZzHAjOjKmV3nSuBjwXQg"
# )
#
# sched2 = BlockingScheduler()
#
# class FacebookCrawler:
#     LOGIN_URL = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'
#
#     def __init__(self, login, password):
#         chrome_options = webdriver.ChromeOptions()
#         prefs = {"profile.default_content_setting_values.notifications": 2}
#         chrome_options.add_experimental_option("prefs", prefs)
#
#         chrome_options.binary_location = GOOGLE_CHROME_BIN
#         chrome_options.add_argument('--disable-gpu')
#         chrome_options.add_argument('--no-sandbox')
#         driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
#
#         self.driver = webdriver.Chrome(chrome_options=chrome_options)
#         self.wait = WebDriverWait(self.driver, 10)
#
#         self.login(login, password)
#
#     def login(self, login, password):
#         self.driver.get(self.LOGIN_URL)
#
#         # wait for the login page to load
#         self.wait.until(EC.visibility_of_element_located((By.ID, "email")))
#
#         self.driver.find_element_by_id('email').send_keys(login)
#         self.driver.find_element_by_id('pass').send_keys(password)
#         self.driver.find_element_by_id('loginbutton').click()
#
#         # wait for the main page to load
#         self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#bluebarRoot")))
#         link = 'lviv1256'
#         self.driver.get('https://www.facebook.com/'+link+'/')
#
#     def _get_post_containers(self):
#         return self.driver.find_elements_by_css_selector("div._4-u2._4-u8")
#
#     def _get_seperate_posts(self):
#         return self.driver.find_elements_by_css_selector("span.fsm.fwn.fcg a._5pcq")
#
#     def get_posts(self):
#         # navigate to "friends" page
#         #self.driver.find_element_by_css_selector("a#findFriendsNav").click()
#
#         # continuous scroll until no more new friends loaded
#         self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#u_0_z")))
#         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         num_of_loaded_posts = len(self._get_post_containers())
#         #print(num_of_loaded_posts)
#         # i=0
#         # while True:
#         #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         #     try:
#         #         #print('here')
#         #         self.wait.until(lambda driver: len(self._get_post_containers()) > num_of_loaded_posts)
#         #         num_of_loaded_posts = len(self._get_post_containers())
#         #         print(num_of_loaded_posts)
#         #         if i>2:
#         #             break
#         #         i+=1
#         #     except TimeoutException:
#         #         #print('TimeoutException')
#         #         break  # no more friends loaded
#         #     #print('here')
#         #
#         # print(len(self._get_seperate_posts()))
#         # self.driver.save_screenshot('filename.png')
#         return self._get_seperate_posts()
#
#     def get_screenshot(self, link, i):
#         print(i)
#         if i >=3:
#             return
#         self.driver.get(link)
#         try:
#             self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img._4on7._3mk2.img")))
#         except:
#             time.sleep(2)
#             self.driver.save_screenshot('filename'+str(i)+'.png')
#             return
#         self.driver.execute_script("var position = window.pageYOffset; var getElemDistance = function ( elem ) { var location = 0; if (elem.offsetParent) {do {location += elem.offsetTop; elem = elem.offsetParent;} while (elem);}return location >= 0 ? location : 0;};var elem = document.querySelector('#content_container');var location = getElemDistance( elem );window.scrollTo(0, location-82);")
#         #time.sleep(1)
#         self.driver.save_screenshot('filename'+str(i)+'.png')
#         #cloudinary.uploader.upload('filename'+str(i)+'.png')
#         cloudinary.uploader.upload('filename'+str(i)+'.png', public_id = 'filename'+str(i)+'.png', use_filename = 1, unique_filename = 0)
#
# @sched2.scheduled_job('interval', minutes=2)
# def parse():
#     crawler = FacebookCrawler(login='newskitbot@gmail.com', password='NewsKit2019')
#     posts = crawler.get_posts()
#     links = []
#     for post in posts:
#         link = post.get_attribute("href")
#         links.append(link)
#     i=-1
#     for link in links:
#         i+=1
#         print(link)
#         try:
#             crawler.get_screenshot(link, i)
#         except:
#             continue
#
#     print('Finished!')
#
# if __name__ == '__main__':
#     parse()
#     sched2.start()
