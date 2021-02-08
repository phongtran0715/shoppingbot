from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from chromedriver_py import binary_path as driver_path
from utils import random_delay, send_webhook, create_msg, get_proxy, get_proxy_raw
from utils.selenium_utils import change_driver
import urllib, requests, time, lxml.html, json, sys, settings

class GameStop:
	def __init__(self, task_id, status_signal, image_signal, product, profile, monitor_proxies, shopping_proxies, monitor_delay, error_delay, max_price, max_quantity):
		self.task_id, self.status_signal, self.image_signal, self.product, self.profile, self.monitor_delay, self.error_delay, self.max_price, self.max_quantity = task_id, status_signal, image_signal, product, profile, float(
			monitor_delay), float(error_delay), max_price, max_quantity
		self.monitor_proxies = monitor_proxies
		self.shopping_proxies = shopping_proxies

		starting_msg = "Starting GameStop"
		self.product_image = None

		self.SHORT_TIMEOUT = 5
		self.LONG_TIMEOUT = 20
		self.MONITOR_DELAY = 15

		if settings.dont_buy:
			starting_msg = "Starting GameStop in dev mode; will not actually checkout."

		self.status_signal.emit(create_msg(starting_msg, "normal"))
		self.monitoring_browser = self.init_monitoring_driver()
		self.monitor()
		self.browser = self.init_shopping_driver()
		if settings.gamestop_user != None and settings.gamestop_user != "" and settings.gamestop_pass != None and settings.gamestop_pass != "":
			self.is_login = True
		else:
			self.is_login = False
		self.login()
		self.add_to_cart()
		self.submit_shipping()
		self.submit_billing()
		self.submit_order()

	def init_shopping_driver(self):
		# chrome_options = webdriver.ChromeOptions()
		# chrome_options.add_experimental_option('useAutomationExtension', False)
		# chrome_options.add_argument("window-size=1200x600")
		# # shopping_proxy = get_proxy_raw(self.shopping_proxies)
		# # if shopping_proxy is not None and shopping_proxy != "":
		# #     chrome_options.add_argument('--proxy-server={}'.format(shopping_proxy))
		# browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

		# browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		#     "source": """
		#           Object.defineProperty(navigator, 'webdriver', {
		#            get: () => undefined
		#           })
		#         """
		# })

		# firefox
		shopping_proxy = get_proxy_raw(self.shopping_proxies)
		if shopping_proxy is not None and shopping_proxy != "":
			print("Shopping proxy : " + str(shopping_proxy))
			proxy = Proxy({
				'proxyType': ProxyType.MANUAL,
				'httpProxy': shopping_proxy,
				'ftpProxy': shopping_proxy,
				'sslProxy': shopping_proxy,
				'noProxy': '' # set this value as desired
			})
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), proxy=proxy)
		else:
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		return browser

	def init_monitoring_driver(self):
		# firefox
		monitoring_proxy = get_proxy_raw(self.monitor_proxies)
		if monitoring_proxy is not None and monitoring_proxy != "":
			print("Shopping proxy : " + str(monitoring_proxy))
			proxy = Proxy({
				'proxyType': ProxyType.MANUAL,
				'httpProxy': monitoring_proxy,
				'ftpProxy': monitoring_proxy,
				'sslProxy': monitoring_proxy,
				'noProxy': '' # set this value as desired
			})
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), proxy=proxy)
		else:
			browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		return browser


	def login(self):
		if self.is_login == False:
			return
		self.status_signal.emit(create_msg("Logging In..", "normal"))

		self.browser.get("https://www.gamestop.com")

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.LINK_TEXT, "MY ACCOUNT")))
		self.browser.find_element_by_link_text('MY ACCOUNT').click()

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "signIn"))).click()

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "login-form-email")))

		email = self.browser.find_element_by_id("login-form-email")
		email.send_keys(settings.gamestop_user)

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "login-form-password")))

		password = self.browser.find_element_by_id("login-form-password")
		password.send_keys(settings.gamestop_pass)

		time.sleep(2) # slight delay for in-between filling out login info and clicking Sign In

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signinCheck"]/button')))
		sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signinCheck"]/button')
		sign_in_btn.click()
		time.sleep(2)

	# def monitor(self):
	# 	headers = {
	# 		"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	# 		"accept-encoding": "gzip, deflate, br",
	# 		"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
	# 		"cache-control": "max-age=0",
	# 		"upgrade-insecure-requests": "1",
	# 		"user-agent": settings.userAgent
	# 	}
	# 	self.session = requests.Session()
	# 	monitor_proxy = get_proxy(self.monitor_proxies)
	# 	if monitor_proxy is not None and monitor_proxy != "":
	# 		self.session.proxies.update(monitor_proxy)
	# 		print("Monitoring by proxy : {}".format(monitor_proxy))
	# 	while True:
	# 		self.status_signal.emit(create_msg("Checking Product ..", "normal"))
	# 		try:
	# 			r = self.session.get(self.product, headers=headers)
	# 			if r.status_code == 200:
	# 				doc = lxml.html.fromstring(r.text)
	# 				if self.is_xpath_exist(doc, '//button[@data-buttontext="Add to Cart"][@disabled="disabled"]'):
	# 					item = doc.xpath("//button[@class='add-to-cart btn btn-primary ']")
	# 					print(item.text_content())
	# 					self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
	# 					time.sleep(self.MONITOR_DELAY)
	# 				else:
	# 					if self.is_xpath_exist(doc, '//button[@data-buttontext="Add to Cart"]'):
	# 						add_to_cart_btn = doc.xpath('//button[@data-buttontext="Add to Cart"]')[0]
	# 						if add_to_cart_btn is None:
	# 							self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
	# 							time.sleep(self.MONITOR_DELAY)
	# 						else:
	# 							return
	# 			else:
	# 				self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
	# 				time.sleep(self.MONITOR_DELAY)
	# 		except Exception as e :
	# 			self.status_signal.emit({"msg": "Error Loading Product Page (line {} {} {})".format(
	# 				sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
	# 			print("Not found add to cart button\n");
	# 			time.sleep(self.MONITOR_DELAY)
	def monitor(self):
		self.status_signal.emit(create_msg("Monitoring Product ..", "normal"))
		self.monitoring_browser.get(self.product)
		wait(self.monitoring_browser, self.LONG_TIMEOUT).until(lambda _: self.monitoring_browser.current_url == self.product)
		while True:
			try:
				wait(self.monitoring_browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-buttontext="Add to Cart"]')))
				add_to_cart_btn = self.monitoring_browser.find_element_by_xpath('//button[@data-buttontext="Add to Cart"]')
				if add_to_cart_btn is not None:
					self.monitoring_browser.close()
					return
				else:
					self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
					time.sleep(self.MONITOR_DELAY)
			except Exception as e:
				# self.status_signal.emit({"msg": "Error Adding to card (line {} {} {})".format(
				# 	sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				print("Not found avialable add to cart button")
				self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
				time.sleep(self.MONITOR_DELAY)


	def add_to_cart(self):
		self.status_signal.emit(create_msg("Adding To Cart..", "normal"))
		self.browser.get(self.product)
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == self.product)
		try:
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-buttontext="Add to Cart"]')))
			add_to_cart_btn = self.browser.find_element_by_xpath('//button[@data-buttontext="Add to Cart"]')
			add_to_cart_btn.click()
			time.sleep(self.SHORT_TIMEOUT)
			self.status_signal.emit(create_msg("Added to cart", "normal"))
		except Exception as e:
			self.status_signal.emit({"msg": "Error Adding to card (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})


	def submit_shipping(self):
		if self.is_login == True:
			return
		self.status_signal.emit(create_msg("Summit shipping", "normal"))
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=shipping#shipping")
		self.browser.implicitly_wait(15)

		self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shipping-email")))
		email = self.browser.EC("shipping-email")
		email.send_keys(self.profile["shipping_email"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingFirstName")))
		firstName = self.browser.find_element_by_id("shippingFirstName")
		firstName.send_keys(self.profile["shipping_fname"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingLastName")))
		lastName = self.browser.find_element_by_id("shippingLastName")
		lastName.send_keys(self.profile["shipping_lname"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingAddressOne")))
		address1 = self.browser.find_element_by_id("shippingAddressOne")
		address1.send_keys(self.profile["shipping_a1"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingState")))
		state = Select(driver.find_element_by_id('shippingState'))
		state.select_by_visible_text('Georgia')

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingAddressCity")))
		city = self.browser.find_element_by_id("shippingAddressCity")
		city.send_keys(self.profile["shipping_city"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingZipCode")))
		zipcode = self.browser.find_element_by_id("shippingZipCode")
		zipcode.send_keys(self.profile["shipping_zipcode"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "shippingPhoneNumber")))
		phone = self.browser.find_element_by_id("shippingPhoneNumber")
		phone.send_keys(self.profile["shipping_phone"])

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "shippingPhoneNumber")))
		self.browser.find_element_by_class_name("btn.btn-primary.btn-block.submit-shipping").click()
		self.status_signal.emit(create_msg("Summit shipping done", "normal"))

	def submit_billing(self):
		self.browser.get("https://www.gamestop.com/checkout/?stage=payment#payment")
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=payment#payment")

		self.status_signal.emit(create_msg("Entering billing info", "normal"))
		if self.is_login:
			# just fill cvv
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "saved-payment-security-code")))
			securityCode = self.browser.find_element_by_id("saved-payment-security-code")
			securityCode.send_keys(self.profile["card_cvv"])
		else:
			# fill billing info
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "email")))
			email = self.browser.find_element_by_id("email")
			email.send_keys(self.profile["shipping_email"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingFirstName")))
			firstName = self.browser.find_element_by_id("billingFirstName")
			firstName.send_keys(self.profile["shipping_fname"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingLastName")))
			lastName = self.browser.find_element_by_id("billingLastName")
			lastName.send_keys(self.profile["shipping_lname"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingAddressOne")))
			address1 = self.browser.find_element_by_id("billingAddressOne")
			address1.send_keys(self.profile["shipping_a1"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingState")))
			state = Select(self.browser.find_element_by_id('billingState'))
			state.select_by_visible_text('Georgia')

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingAddressCity")))
			city = self.browser.find_element_by_id("billingAddressCity")
			city.send_keys(self.profile["shipping_city"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "billingZipCode")))
			zipcode = self.browser.find_element_by_id("billingZipCode")
			zipcode.send_keys(self.profile["shipping_zipcode"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "phoneNumber")))
			phone = self.browser.find_element_by_id("phoneNumber")
			phone.send_keys(self.profile["shipping_phone"])

			# Add card information
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "cardNumber")))
			card_number = self.browser.find_element_by_id("cardNumber")
			card_number.send_keys(self.profile["card_number"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "expirationMonth")))
			expirationMonth = Select(self.browser.find_element_by_id('expirationMonth'))
			expirationMonth.select_by_visible_text(self.profile["card_month"])

			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "expirationYear")))
			expirationYear = Select(self.browser.find_element_by_id('expirationYear'))
			expirationYear.select_by_visible_text(self.profile["card_year"])
			wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "saved-payment-security-code")))
			securityCode = self.browser.find_element_by_id("saved-payment-security-code")
			securityCode.send_keys(self.profile["card_cvv"])

		# send summit button
		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btn-primary.btn-block.submit-payment")))
		order_review_btn = self.browser.find_element_by_class_name("btn.btn-primary.btn-block.submit-payment")
		order_review_btn.click()


	def submit_order(self):
		wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == "https://www.gamestop.com/checkout/?stage=placeOrder#placeOrder")

		self.status_signal.emit(create_msg("Submitting Order..", "normal"))

		wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.btn-block.place-order')))

		if not settings.dont_buy:
			order_review_btn = self.browser.find_element_by_class_name("btn.btn-primary.btn-block.place-order")
			order_review_btn.click()
			self.status_signal.emit(create_msg("Order Placed", "success"))
			send_webhook("OP", "GameStop", self.profile["profile_name"], self.task_id, self.product_image)
		else:
			self.status_signal.emit(create_msg("Mock Order Placed", "success"))
			send_webhook("OP", "GameStop", self.profile["profile_name"], self.task_id, self.product_image)

	def is_xpath_exist(self, doc, xpath_str):
		result = False
		try:
			item = doc.xpath(xpath_str)[0]
			if item is not None:
				print("Found button {}".format(item))
				result = True
		except:
			result = False
		return result

