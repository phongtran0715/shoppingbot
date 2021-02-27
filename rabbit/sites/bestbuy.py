import json, settings, webbrowser, urllib3, requests, sys, time, lxml.html
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
import logging
logger = logging.getLogger(__name__)


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
		self.is_login = True

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
		self.monitor()
		pass
		for account_name in self.account.split(','):
			account_item = get_account(account_name)
			if account_item is None:
				continue
			self.browser = self.init_driver(account_item)
			self.login(account_item)

			# Add to cart maximum 3 items
			if self.max_quantity is None or self.max_quantity == "" or int(self.max_quantity) > 3:
				self.max_quantity = 3

			self.add_to_cart(account_item)

			self.submit_billing(account_item)

	def init_driver(self, account):
		shopping_proxy = get_proxy_raw(account['proxy'])
		if shopping_proxy is not None and shopping_proxy != "":
			print("Bestbuy | TASK {} - Shopping proxy : {}".format(self.task_id, str(shopping_proxy)))
			firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
			firefox_capabilities['marionette'] = True
			firefox_capabilities['proxy'] = {
				"proxyType": "MANUAL",
				"httpProxy": shopping_proxy,
				"ftpProxy": shopping_proxy,
				"sslProxy": shopping_proxy
			}
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),capabilities=firefox_capabilities)
		else:
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		return browser

	def init_monitor_driver(self):
		monitor_proxy = get_proxy_raw(self.monitor_proxies)
		if monitor_proxy is not None and monitor_proxy != "":
			print("Bestbuy | TASK {} - Shopping proxy : {}".format(self.task_id, str(monitor_proxy)))
			firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
			firefox_capabilities['marionette'] = True
			firefox_capabilities['proxy'] = {
				"proxyType": "MANUAL",
				"httpProxy": monitor_proxy,
				"ftpProxy": monitor_proxy,
				"sslProxy": monitor_proxy
			}
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),capabilities=firefox_capabilities)
		else:
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		return browser

	def monitor(self):
		monitor_browser = self.init_monitor_driver()

		while True:
			self.status_signal.emit(create_msg("Monitoring Product ..", "normal"))
			monitor_browser.get(self.product)
			try:
				wait(monitor_browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Add to Cart"]')))
				add_to_cart_btn = monitor_browser.find_element_by_xpath('//button[text()="Add to Cart"]')
				if add_to_cart_btn is not None:
					logger.info('BestBuy | Task id : {} - Found product'.format(self.task_id))
					monitor_browser.close()
					return
				else:
					logger.info("BestBuy | Task id : {} - Product is not available".format(self.task_id));	
					self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
					time.sleep(self.MONITOR_DELAY)
			except Exception as e :
				self.status_signal.emit({"msg": "Error Loading Product Page (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				logger.info("Not found add to cart button\n");
				time.sleep(self.MONITOR_DELAY)


	def login(self, account):
		self.status_signal.emit(create_msg("Logging...", "normal"))
		self.browser.get("https://www.bestbuy.com/identity/global/signin")
		self.browser.find_element_by_xpath('//*[@id="fld-e"]').send_keys(account['user_name'])
		self.browser.find_element_by_xpath('//*[@id="fld-p1"]').send_keys(account['password'])
		self.browser.find_element_by_xpath('//button[@data-track="Sign In"]').click()
		wait(self.browser, self.LONG_TIMEOUT).until(lambda x: "Official Online Store" in self.browser.title)


	def add_to_cart(self, account):
		result = False
		try:
			self.status_signal.emit(create_msg("Adding To Cart..", "normal"))
			self.browser.get(self.product)
			wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == self.product)
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-lg')))
			add_to_cart_btn = self.browser.find_element_by_class_name('btn-lg')
			add_to_cart_btn.click()
			time.sleep(self.SHORT_TIMEOUT)
			result = True
			self.status_signal.emit(create_msg("Added to cart", "normal"))
		except Exception as e:
			self.status_signal.emit({"msg": "Error Adding to card (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})

	def submit_billing(self, account):
		self.browser.get("https://www.bestbuy.com/checkout/r/fast-track")
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.bestbuy.com/checkout/r/fast-track")

		profile = get_profile(account['profile'])
		self.status_signal.emit(create_msg("Entering billing info", "normal"))
		if self.is_login:
			# just fill cvv
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "credit-card-cvv")))
			securityCode = self.browser.find_element_by_id("credit-card-cvv")
			securityCode.send_keys(profile["card_cvv"])
		else:
			# TODO: fill billing info
			pass

		# send summit button
		if settings.dont_buy is True:
			self.status_signal.emit(create_msg("Mock Order Placed", "success"))
			send_webhook("OP", "BestBuy", account["name"], self.task_id, self.product_image)
		else:
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="button--place-order-fast-track"]//button[@data-track="Place your Order - Contact Card"]')))
			order_review_btn = self.browser.find_element_by_xpath('//div[@class="button--place-order-fast-track"]//button[@data-track="Place your Order - Contact Card"]')
			order_review_btn.click()

	def is_xpath_exist(self, doc, xpath_str):
		result = False
		try:
			item = doc.xpath(xpath_str)[0]
			if item is not None:
				result = True
		except:
			result = False
		return result