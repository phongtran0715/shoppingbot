from selenium import webdriver
from utils import send_webhook, random_delay, get_proxy, twocaptcha_utils
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
print("captcha result {}".format(captcha_result))
# code = "03AGdBq25pJv_uy3fDwpqH4EsCtMtYPSnhL57nQv5l-b5a8EOlK8pvCYKDlkpJA4NgHqWHxaSQ-jz9UWA-Zxp-6Yos-j0gZbuKz6lqrCzQZPijzABfw9H1OpF0Ak-J-8T2rN5Uye0A9UYuwtGdcXsI9jGqDBifnum4DaKO7osweOSE69MXIHf69NlVzAHDYT0qAUQL4KkUIvUquauBuGQO9x748XgYQTvL41fllZ8MnPcpFkSelB-pWMCliVgemQeU4dFPflKaHgMMDHjjF5CaCphcRn485whedj7M61cnji1dQrrvCDYGlq7dWYtvUhOEvSkVKDHuVFdx9YBbUy27kx8nMotGVDnNTsSFaB3hgJgvw7bnw67td-CL9TO4PYCXIdZq96CG40n9W0SdviLHQ70d7XJ55OZtPweCAFtBpoglt-lrQKyMFjwSW3e3mW0407c-4McdqN3tOtgoU6j2fenid9eIU4nVfSMAnp5_fT1Kyc42T-W8Obcowd073Hptb4bDS5ge_OG0Sz7E09ibJMy-OmtTObcDIw"
if captcha_result is not None:
	pass
	# Inject response in webpage
	# browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % captcha_result['code'])
	# 	# Wait a moment to execute the script (just in case).
	# time.sleep(1)

	# Press submit button
# 	browser.execute_script("""
#   document.getElementById("g-recaptcha-response").innerHTML = arguments[0]
# """, code)
	# # Inject response in webpage
	# driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
	# captcha_response= browser.find_element_by_xpath('//textarea[@id="g-recaptcha-response"]')
	# javaScript = "document.querySelector('#g-recaptcha-response').textContent='';"
	# browser.execute_script(javaScript)
	# 
	# browser.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
	# browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]', code)