from selenium import webdriver
from utils import twocaptcha_utils
from webdriver_manager.chrome import ChromeDriverManager
import time

url="https://www.walmart.com/blocked?url=L2lwL1BsYXktRG9oLVBhcnR5LUJhZy1JbmNsdWRlcy0xNS1Db2xvcmZ1bC1DYW5zLW9mLVBsYXktRG9oLTEtT3VuY2UtQ2Fucy8xOTcwODgxNTA=&uuid=8ef89ed0-66c9-11eb-a01c-2d15fd7c1efb&vid=&g=a"
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors') #removes SSL errors from terminal
options.add_experimental_option("excludeSwitches", ["enable-logging"]) #removes device adapter errors from terminal
browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
browser.get(url)
time.sleep(3)

sitekey = browser.find_element_by_xpath('//div[@class="g-recaptcha"]').get_attribute("data-sitekey")
print("site key {}".format(sitekey))
captcha_result  = twocaptcha_utils.solve_captcha(str(browser.current_url), str(sitekey))
print("captcha result {}".format(captcha_result['code']))
if captcha_result['code'] is not None:
	browser.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
	browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]', captcha_result['code'])
	browser.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')
