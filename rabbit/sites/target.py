from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from chromedriver_py import binary_path as driver_path
from utils.rabbit_util import RabbitUtil
from utils.selenium_utils import change_driver
import time, os
from model.task_model import TaskModel
from PyQt5.QtSql import QSqlDatabase
from PyQt5 import QtCore
from configparser import ConfigParser
import logging
from utils.rabbit_util import RabbitUtil

logger = logging.getLogger(__name__)

class Target:
	def __init__(self, status_signal, image_signal, task_model):
		
		self.task_id = task_model.get_task_id()
		self.status_signal = status_signal
		self.image_signal = image_signal
		self.product = task_model.get_product()
		
		self.monitor_delay = float(task_model.get_monitor_delay())
		self.error_delay = float(task_model.get_error_delay())
		self.monitor_proxies = task_model.get_monitor_proxy()
		self.account = task_model.get_account()
		self.max_quantity = task_model.get_max_quantity()

		# create database connection
		self.db_conn = QSqlDatabase.addDatabase("QSQLITE", "target_db_conn_" + str(task_model.get_task_id()))
		self.db_conn.setDatabaseName(os.path.join('data', 'rabbit_db.sqlite'))
		if not self.db_conn.open():
			logger.error("Target | Task id {}- Open conection false!".format(self.task_id))

		# create config parser
		self.config = ConfigParser()
		self.config.read(os.path.join('data', 'config.ini'))
		self.dont_buy = True
		if self.config.getint('general', 'dev_mode') == 0:
			self.dont_buy = False

		self.product_image = None
		self.TIMEOUT_SHORT = 15
		self.TIMEOUT_LONG = 30
		self.did_submit = False
		self.failed = False
		self.retry_attempts = 10

		self.img_found = False

		starting_msg = "Starting Target"
		self.status_signal.emit(RabbitUtil.create_msg(starting_msg, "normal", self.task_id))
		# self.xpath_sequence = [
		# 	{'type': 'method', 'path': '//button[@data-test="orderPickupButton"] | //button[@data-test="shipItButton"]', 'method': self.find_and_click_atc, 'message': 'Added to cart', 'message_type': 'normal', 'optional': False}
		# 	, {'type': 'button', 'path': '//button[@data-test="espModalContent-declineCoverageButton"]', 'message': 'Declining Coverage', 'message_type': 'normal', 'optional': True}
		# 	, {'type': 'button', 'path': '//button[@data-test="addToCartModalViewCartCheckout"]', 'message': 'Viewing Cart before Checkout', 'message_type': 'normal', 'optional': False}
		# 	, {'type': 'button', 'path': '//button[@data-test="checkout-button"]', 'message': 'Checking out', 'message_type': 'normal', 'optional': False}
		# 	, {'type': 'method', 'path': '//button[@data-test="placeOrderButton"]', 'method': self.submit_order, 'message': 'Submitting order', 'message_type': 'normal', 'optional': False}
		# ]
		# self.possible_interruptions = [
		# 	{'type': 'method', 'path': '//input[@id="password"]', 'method': self.fill_and_authenticate, 'message': 'Authenticating', 'message_type': 'normal'}
		# 	, {'type': 'input', 'path': '//input[@id="creditCardInput-cardNumber"]', 'args': {'value': self.profile['card_number'], 'confirm_button': '//button[@data-test="verify-card-button"]'}, 'message': 'Entering CC #', 'message_type': 'normal'}
		# 	, {'type': 'input', 'path': '//input[@id="creditCardInput-cvv"]', 'args': {'value': self.profile['card_cvv']}, 'message': 'Entering CC #', 'message_type': 'normal'}
		# ]
		
		# self.monitor()
		for account_name in self.account.split(','):
			account_item = RabbitUtil.get_account(account_name, self.db_conn)
			if account_item is None:
				continue
			self.browser = self.init_driver(account_item)
			self.status_signal.emit(RabbitUtil.create_msg("Logging In..", "normal", self.task_id))
			self.login(account_item)
		
		# self.product_loop()
		# RabbitUtil.send_webhook("OP", "Target", self.profile["profile_name"], self.task_id, self.product_image)

	def init_driver(self, account):
		shopping_proxy = RabbitUtil.get_proxy_raw(account.get_proxy(), self.db_conn)
		if shopping_proxy is not None and shopping_proxy != "":
			print("Gamestop | TASK {} - Shopping proxy : {}".format(self.task_id, str(shopping_proxy)))
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

	def login(self, account):
		self.browser.get("https://www.target.com")
		self.browser.find_element_by_id("account").click()
		wait(self.browser, self.TIMEOUT_LONG).until(EC.element_to_be_clickable((By.ID, "accountNav-signIn"))).click()
		wait(self.browser, self.TIMEOUT_LONG).until(EC.presence_of_element_located((By.ID, "username")))
		self.fill_and_authenticate(account)

		# Gives it time for the login to complete
		time.sleep(5)

	def fill_and_authenticate(self, account):
		if self.browser.find_elements_by_id('username'):
			self.fill_field_and_proceed('//input[@id="username"]', {'value': account.get_user_name()})
		self.fill_field_and_proceed('//input[@id="password"]', {'value': account.get_password(), 'confirm_button': '//button[@id="login"]'})

	def product_loop(self):
		while not self.did_submit and not self.failed:
			self.monitor()
			self.atc_and_checkout()

	def check_stock(self, new_tab=False):
		stock = False
		if new_tab:
			windows_before = self.browser.window_handles
			self.browser.execute_script(f'window.open("{self.product}")')
			wait(self.browser, 10).until(EC.number_of_windows_to_be(2))
			new_window = [x for x in self.browser.window_handles if x not in windows_before][0]
			self.browser.switch_to_window(new_window)
		if len(self.browser.find_elements_by_xpath('//button[@data-test="orderPickupButton"]')) > 0 or len(self.browser.find_elements_by_xpath('//button[@data-test="shipItButton"]')) > 0:
			stock = True
		if new_tab:
			self.browser.close()
			wait(self.browser, 10).until(EC.number_of_windows_to_be(1))
			old_window = self.browser.window_handles[0]
			self.browser.switch_to_window(old_window)
			return False
		return stock

	def monitor(self):
		self.in_stock = False
		self.browser.get(self.product)
		wait(self.browser, self.TIMEOUT_LONG).until(lambda _: self.browser.current_url == self.product)

		while not self.img_found:
			try:
				if not self.img_found:
					product_img = self.browser.find_elements_by_class_name('slideDeckPicture')[0].find_element_by_tag_name(
						"img")
					self.image_signal.emit(product_img.get_attribute("src"))
					self.product_image = product_img.get_attribute("src")
					self.img_found = True
			except Exception as e:
				continue

		while not self.in_stock:
			self.in_stock = self.check_stock()
			if self.in_stock:
				continue
			else:
				self.status_signal.emit(RabbitUtil.create_msg("Waiting on Restock", "normal", self.task_id))
				time.sleep(5)
				self.browser.refresh()

	def atc_and_checkout(self):
		while not self.did_submit:
			for xpath_step in self.xpath_sequence:
				for attempt in range(self.retry_attempts + 1):
					try:
						wait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath_step['path'])))
						self.process_step(xpath_step)
						break
					except:
						if xpath_step['optional']:
							break
						elif attempt == self.retry_attempts:
							if not self.check_stock(new_tab=True):
								self.status_signal.emit(RabbitUtil.create_msg('Product is out of stock. Resuming monitoring.', 'error', self.task_id))
								return
							else:
								self.status_signal.emit(RabbitUtil.create_msg('Encountered unknown page while product in stock. Quitting.', 'error', self.task_id))
								self.failed = True
								return
						self.process_interruptions(attempt=attempt)

	def submit_order(self):
		self.did_submit = False
		url = self.browser.current_url
		while not self.did_submit:
			try:
				self.process_interruptions(silent=True)
				self.browser.find_element_by_xpath('//button[@data-test="placeOrderButton"]').click()
				time.sleep(5)
				if 'https://www.target.com/co-thankyou' in self.browser.current_url:
					self.status_signal.emit(RabbitUtil.create_msg("Order Placed", "success", self.task_id))
						
					send_webhook.send_webhook("OP", "Target", self.profile["profile_name"], self.task_id, self.product_image)
					self.did_submit = True
			except:
				self.status_signal.emit(RabbitUtil.create_msg('Retrying submit order until success', 'normal', self.task_id))

	def find_and_click(self, xpath):
		self.browser.find_element_by_xpath(xpath).click()
		
	def find_and_click_atc(self):
		if self.browser.current_url == self.product and self.check_stock():
			if self.browser.find_elements_by_xpath('//button[@data-test="orderPickupButton"]'):
				button = self.browser.find_element_by_xpath('//button[@data-test="orderPickupButton"]')
			elif self.browser.find_elements_by_xpath('//button[@data-test="shipItButton"]'):
				button = self.browser.find_element_by_xpath('//button[@data-test="shipItButton"]')
			else:
				button = None
		if button:
			self.browser.execute_script("return arguments[0].scrollIntoView(true);", button)
			self.atc_clicked = True
			button.click()
	
	def fill_field_and_proceed(self, xpath, args):
		input_field = self.browser.find_element_by_xpath(xpath)
		if len(input_field.get_attribute('value')) == 0:
			input_field.send_keys(args['value'])
		if 'confirm_button' in args:
			if self.browser.find_elements_by_xpath(args['confirm_button']):
				self.find_and_click(args['confirm_button'])

	def process_step(self, xpath_step, wait_after=False, silent=False):
		if self.browser.find_elements_by_xpath(xpath_step['path']):
			if not silent:
				self.status_signal.emit(RabbitUtil.create_msg(xpath_step['message'], xpath_step['message_type'], self.task_id))
			if xpath_step['type'] == 'button':
				self.find_and_click(xpath_step['path'])
			elif xpath_step['type'] == 'method':
				xpath_step['method']()
			elif xpath_step['type'] == 'input':
				self.fill_field_and_proceed(xpath_step['path'], xpath_step['args'])
			if wait_after:
				time.sleep(self.TIMEOUT_SHORT)
		
	def process_interruptions(self, attempt=0, silent=False):
		if not silent:
			self.status_signal.emit(RabbitUtil.create_msg(f'Interrupted, attempting to resolve ({attempt+1}/{self.retry_attempts})', 'error', self.task_id))
		for xpath_step in self.xpath_sequence:
			if xpath_step['optional']:
				self.process_step(xpath_step, wait_after=True, silent=True)
		for xpath_step in self.possible_interruptions:
			self.process_step(xpath_step, wait_after=True, silent=True)
