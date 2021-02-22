from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from chromedriver_py import binary_path as driver_path
from utils import (random_delay, send_webhook,
	create_msg, get_profile, get_proxy,
	get_proxy_raw, get_account,
	get_profile_by_account,
	get_proxy_by_account)
from utils.selenium_utils import change_driver
import urllib, requests, time, lxml.html, json, sys, settings

class GameStop:
	def __init__(self, task_id, status_signal, image_signal, product, monitor_proxies,
		monitor_delay, error_delay, max_price, max_quantity, account):
		self.task_id = task_id
		self.status_signal = status_signal
		self.image_signal = image_signal
		self.product = product
		self.monitor_delay = float(monitor_delay)
		self.error_delay = float(error_delay)
		self.max_price = max_price
		self.max_quantity = max_quantity
		self.monitor_proxies = monitor_proxies
		self.account = account
		self.is_login = True

		starting_msg = "Starting GameStop"
		self.product_image = None

		self.SHORT_TIMEOUT = 5
		self.LONG_TIMEOUT = 20
		self.MONITOR_DELAY = 15

		if settings.dont_buy:
			starting_msg = "Starting GameStop in dev mode; will not actually checkout."

		self.status_signal.emit(create_msg(starting_msg, "normal"))
		self.monitor()
		for account_name in self.account.split(','):
			account_item = get_account(account_name)
			if account_item is None:
				continue
			self.browser = self.init_shopping_driver(account_item)
			self.login(account_item)
			# Add to cart maximum 3 items
			if self.max_quantity is None or self.max_quantity == "" or int(self.max_quantity) > 3:
				self.max_quantity = 3

			for i in range(0, int(self.max_quantity)):
				self.add_to_cart()
			# self.submit_shipping(account_item)
			self.submit_billing(account_item)
			self.submit_order(account_item)

	def init_shopping_driver(self, account):
		# firefox
		shopping_proxy = get_proxy_raw(account['proxy'])
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


	def login(self, account_item):
		self.status_signal.emit(create_msg("Logging In..", "normal"))

		self.browser.get("https://www.gamestop.com")

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.LINK_TEXT, "MY ACCOUNT")))
		self.browser.find_element_by_link_text('MY ACCOUNT').click()

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "signIn"))).click()

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "login-form-email")))

		email = self.browser.find_element_by_id("login-form-email")
		email.send_keys(account_item['user_name'])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "login-form-password")))

		password = self.browser.find_element_by_id("login-form-password")
		password.send_keys(account_item['password'])

		time.sleep(2) # slight delay for in-between filling out login info and clicking Sign In

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signinCheck"]/button')))
		sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signinCheck"]/button')
		sign_in_btn.click()
		time.sleep(5)

	def monitor(self):
		headers = {
			"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"cache-control": "max-age=0",
			"upgrade-insecure-requests": "1",
			"user-agent": settings.userAgent
		}
		self.session = requests.Session()
		monitor_proxy = get_proxy(self.monitor_proxies)
		if monitor_proxy is not None and monitor_proxy != "":
			self.session.proxies.update(monitor_proxy)
			print("Gamestop | TASK {} - Monitoring by proxy{}".format(self.task_id, monitor_proxy))
		else:
			print("Gamestop | TASK {} - Monitoring without proxy".format(self.task_id))
		while True:
			self.status_signal.emit(create_msg("Checking Product ..", "normal"))
			try:
				r = self.session.get(self.product, headers=headers)
				if r.status_code == 200:
					doc = lxml.html.fromstring(r.text)
					if self.is_product_disable(doc, '//button[@data-buttontext="Add to Cart"][@disabled="disabled"]'):
						print("Gamestop | TASK {} - Product is not available".format(self.task_id))
						item = doc.xpath("//button[@class='add-to-cart btn btn-primary ']")
						self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
						time.sleep(self.MONITOR_DELAY)
					else:
						if self.is_xpath_exist(doc, '//button[@data-buttontext="Add to Cart"]'):
							add_to_cart_btn = doc.xpath('//button[@data-buttontext="Add to Cart"]')[0]
							if add_to_cart_btn is None:
								print("Gamestop | TASK {} - Add to cart button not found".format(self.task_id))
								self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
								time.sleep(self.MONITOR_DELAY)
							else:
								print("Gamestop | TASK {} - Found product".format(self.task_id))
								# TODO: checking for “Free store pick up” or “Ship to Home”
								return
				else:
					print("Gamestop | TASK {} - Connection error - status code = {} - msg = {}".format(self.task_id, r.status_code, r.text))
					self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
					time.sleep(self.MONITOR_DELAY)
			except Exception as e :
				self.status_signal.emit({"msg": "Error Loading Product Page (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				print("Not found add to cart button\n");
				time.sleep(self.MONITOR_DELAY)

	def add_to_cart(self):
		result = False
		self.status_signal.emit(create_msg("Adding To Cart..", "normal"))
		self.browser.get(self.product)
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == self.product)
		try:
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-buttontext="Add to Cart"]')))
			add_to_cart_btn = self.browser.find_element_by_xpath('//button[@data-buttontext="Add to Cart"]')
			add_to_cart_btn.click()
			time.sleep(self.SHORT_TIMEOUT)
			result = True
			self.status_signal.emit(create_msg("Added to cart", "normal"))
		except Exception as e:
			self.status_signal.emit({"msg": "Error Adding to card (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})


	def submit_shipping(self, account):
		# don't nees to enter shipping info
		pass
		profile = get_profile(account['profile'])
		self.status_signal.emit(create_msg("Summit shipping", "normal"))
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=shipping#shipping")
		self.browser.implicitly_wait(15)

		self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shipping-email")))
		email = self.browser.EC("shipping-email")
		email.send_keys(profile["shipping_email"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingFirstName")))
		firstName = self.browser.find_element_by_id("shippingFirstName")
		firstName.send_keys(profile["shipping_fname"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingLastName")))
		lastName = self.browser.find_element_by_id("shippingLastName")
		lastName.send_keys(profile["shipping_lname"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingAddressOne")))
		address1 = self.browser.find_element_by_id("shippingAddressOne")
		address1.send_keys(profile["shipping_a1"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingState")))
		state = Select(driver.find_element_by_id('shippingState'))
		state.select_by_visible_text('Georgia')

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingAddressCity")))
		city = self.browser.find_element_by_id("shippingAddressCity")
		city.send_keys(profile["shipping_city"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingZipCode")))
		zipcode = self.browser.find_element_by_id("shippingZipCode")
		zipcode.send_keys(profile["shipping_zipcode"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingPhoneNumber")))
		phone = self.browser.find_element_by_id("shippingPhoneNumber")
		phone.send_keys(profile["shipping_phone"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "shippingPhoneNumber")))
		self.browser.find_element_by_class_name("btn.btn-primary.btn-block.submit-shipping").click()
		self.status_signal.emit(create_msg("Summit shipping done", "normal"))

	def submit_billing(self, account):
		self.browser.get("https://www.gamestop.com/checkout/?stage=payment#payment")
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=payment#payment")

		profile = get_profile(account['profile'])
		self.status_signal.emit(create_msg("Entering billing info", "normal"))
		if self.is_login:
			# just fill cvv
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "saved-payment-security-code")))
			securityCode = self.browser.find_element_by_id("saved-payment-security-code")
			securityCode.send_keys(profile["card_cvv"])
		else:
			# fill billing info
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "email")))
			email = self.browser.find_element_by_id("email")
			email.send_keys(profile["shipping_email"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingFirstName")))
			firstName = self.browser.find_element_by_id("billingFirstName")
			firstName.send_keys(profile["shipping_fname"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingLastName")))
			lastName = self.browser.find_element_by_id("billingLastName")
			lastName.send_keys(profile["shipping_lname"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingAddressOne")))
			address1 = self.browser.find_element_by_id("billingAddressOne")
			address1.send_keys(profile["shipping_a1"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingState")))
			state = Select(self.browser.find_element_by_id('billingState'))
			state.select_by_visible_text('Georgia')

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingAddressCity")))
			city = self.browser.find_element_by_id("billingAddressCity")
			city.send_keys(profile["shipping_city"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingZipCode")))
			zipcode = self.browser.find_element_by_id("billingZipCode")
			zipcode.send_keys(profile["shipping_zipcode"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "phoneNumber")))
			phone = self.browser.find_element_by_id("phoneNumber")
			phone.send_keys(profile["shipping_phone"])

			# Add card information
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "cardNumber")))
			card_number = self.browser.find_element_by_id("cardNumber")
			card_number.send_keys(profile["card_number"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "expirationMonth")))
			expirationMonth = Select(self.browser.find_element_by_id('expirationMonth'))
			expirationMonth.select_by_visible_text(profile["card_month"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "expirationYear")))
			expirationYear = Select(self.browser.find_element_by_id('expirationYear'))
			expirationYear.select_by_visible_text(profile["card_year"])
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "saved-payment-security-code")))
			securityCode = self.browser.find_element_by_id("saved-payment-security-code")
			securityCode.send_keys(profile["card_cvv"])

		# send summit button
		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btn-primary.btn-block.submit-payment")))
		order_review_btn = self.browser.find_element_by_class_name("btn.btn-primary.btn-block.submit-payment")
		order_review_btn.click()


	def submit_order(self, account):
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=placeOrder#placeOrder")

		self.status_signal.emit(create_msg("Submitting Order..", "normal"))

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.btn-block.place-order')))

		if settings.dont_buy is True:
			self.status_signal.emit(create_msg("Mock Order Placed", "success"))
			send_webhook("OP", "GameStop", account["name"], self.task_id, self.product_image)
		else:
			order_review_btn = self.browser.find_element_by_class_name("btn.btn-primary.btn-block.place-order")
			order_review_btn.click()
			self.status_signal.emit(create_msg("Order Placed", "success"))
			send_webhook("OP", "GameStop", account['name'], self.task_id, self.product_image)

	def is_xpath_exist(self, doc, xpath_str):
		result = False
		try:
			item = doc.xpath(xpath_str)[0]
			if item is not None:
				result = True
		except:
			result = False
		return result

	def is_product_disable(self, doc, xpath_str):
		result = False
		try:
			item = doc.xpath(xpath_str)[0]
			if item is not None:
				msg = str(lxml.html.tostring(item))
				if "Not Available" in msg:
					result = True
				else:
					result = False
		except Exception as e:
			result = False
		return result

