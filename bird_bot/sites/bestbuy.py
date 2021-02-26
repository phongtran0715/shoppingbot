import json, settings, webbrowser, urllib3, requests, sys, time
from time import sleep
from urllib import parse
from chromedriver_py import binary_path  # this will get you the path variable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.json_utils import find_values
from utils.selenium_utils import enable_headless
from utils import (random_delay, send_webhook, create_msg,
	get_profile, get_proxy, get_proxy_raw, get_account,
	get_proxy_by_account,
	get_profile_by_account)

DEFAULT_HEADERS = {
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"accept-encoding": "gzip, deflate, br",
	"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
	"user-agent": settings.userAgent,
	"origin": "https://www.bestbuy.com",
}

class BestBuy:

	def __init__(self, task_id, status_signal, image_signal, product,
		monitor_proxies, monitor_delay, error_delay, account, max_quantity):
		self.task_id = task_id
		self.status_signal = status_signal
		self.image_signal = image_signal
		self.product = product
		self.monitor_delay = float(monitor_delay)
		self.error_delay = float(monitor_delay)
		self.monitor_proxies = monitor_proxies
		self.account = account
		self.max_quantity = max_quantity

		self.SHORT_TIMEOUT = 5
		self.LONG_TIMEOUT = 20
		self.MONITOR_DELAY = 15

		self.sku_id = parse.parse_qs(parse.urlparse(self.product).query)['skuId'][0]
		self.auto_buy = False
		starting_msg = "Starting GameStop"
		if settings.dont_buy:
			starting_msg = "Starting GameStop in dev mode; will not actually checkout."
		self.status_signal.emit(create_msg(starting_msg, "normal"))

		# TODO: Add Product Image To UI
		# TODO: implement monitor function
		self.status_signal.emit(create_msg("Loading https://www.bestbuy.com/", "normal"))
		
		for account_name in self.account.split(','):
			account_item = get_account(account_name)
			if account_item is None:
				continue
			self.browser = self.init_driver(account_item)
			self.login(account_item)

			# Add to cart maximum 3 items
			if self.max_quantity is None or self.max_quantity == "" or int(self.max_quantity) > 3:
				self.max_quantity = 3

			for i in range(0, int(self.max_quantity)):
				self.add_to_cart(account_item)

			self.submit_billing(account_item)
			self.submit_order(account_item)

	def init_driver(self, account):
		browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
		# shopping_proxy = get_proxy_raw(account['proxy'])
		# if shopping_proxy is not None and shopping_proxy != "":
		# 	print("Bestbuy | TASK {} - Shopping proxy : {}".format(self.task_id, str(shopping_proxy)))
		# 	firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
		# 	firefox_capabilities['marionette'] = True
		# 	firefox_capabilities['proxy'] = {
		# 		"proxyType": "MANUAL",
		# 		"httpProxy": shopping_proxy,
		# 		"ftpProxy": shopping_proxy,
		# 		"sslProxy": shopping_proxy
		# 	}
		# 	browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),capabilities=firefox_capabilities)
		# else:
		# 	browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		return browser

	def login(self, account):
		self.browser.get("https://www.bestbuy.com/identity/global/signin")
		self.browser.find_element_by_xpath('//*[@id="fld-e"]').send_keys(account['user_name'])
		self.browser.find_element_by_xpath('//*[@id="fld-p1"]').send_keys(account['password'])
		self.browser.find_element_by_xpath(
			"/html/body/div[1]/div/section/main/div[1]/div/div/div/div/form/div[4]/button"
		).click()

		wait(self.browser, self.LONG_TIMEOUT).until(lambda x: "Official Online Store" in self.browser.title)

	def add_to_cart(self, account):
		result = False
		self.status_signal.emit(create_msg("Adding To Cart..", "normal"))
		self.browser.get(self.product)
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == self.product)
		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-lg')))
		add_to_cart_btn = self.browser.find_element_by_class_name('btn-lg')
		add_to_cart_btn.click()
		time.sleep(self.SHORT_TIMEOUT)
		result = True
		self.status_signal.emit(create_msg("Added to cart", "normal"))
		# try:
		# 	wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-lg')))
		# 	add_to_cart_btn = self.browser.find_element_by_class_name('btn-lg')
		# 	add_to_cart_btn.click()
		# 	time.sleep(self.SHORT_TIMEOUT)
		# 	result = True
		# 	self.status_signal.emit(create_msg("Added to cart", "normal"))
		# except Exception as e:
		# 	self.status_signal.emit({"msg": "Error Adding to card (line {} {} {})".format(
		# 			sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})

	def submit_billing(self, account):
		pass

	def submit_order(self, account):
		pass