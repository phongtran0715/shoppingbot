from sites.walmart_encryption import walmart_encryption as w_e
from utils import (send_webhook, random_delay,
	get_proxy, twocaptcha_utils,
	get_profile, get_account,
	get_profile_by_account,
	get_proxy_by_account)
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from PyQt5 import QtCore
import urllib, requests, time, lxml.html, json, sys, settings
import logging
logger = logging.getLogger(__name__)

class Walmart:
	def __init__(self, task_id, status_signal, image_signal, wait_poll_signal, polling_wait_condition, product,
				 monitor_proxies, monitor_delay, error_delay, max_price, max_quantity, account):
		self.task_id = task_id
		self.status_signal = status_signal
		self.image_signal = image_signal
		self.product = product
		self.monitor_proxies = monitor_proxies
		self.monitor_delay = float(monitor_delay)
		self.error_delay = float(error_delay)
		self.max_price = max_price
		self.max_quantity = max_quantity
		self.account =account
		####### Browser/Captcha Polling Variables ######
		self.captcha_mutex = QtCore.QMutex()
		self.captcha_wait_condition = polling_wait_condition
		self.wait_poll_signal = wait_poll_signal
		#################################################

		self.session = requests.Session()
		# shopping_proxy = get_proxy(self.shopping_proxies)
		# if shopping_proxy is not None and shopping_proxy != "":
		# 	self.session.proxies.update(shopping_proxy)

		if self.max_quantity is None or self.max_quantity == "":
			self.max_quantity = 1

		starting_msg = "Starting"
		self.status_signal.emit({"msg": starting_msg, "status": "normal"})
		self.product_image, offer_id = self.monitor()
		if offer_id is None:
			return
		for account_name in self.account.split(','):
			account_item = get_account(account_name)
			if account_item is None:
				continue
			logger.info("Processing for account : {}".format(account_name))
			did_add = self.atc(offer_id, account_item)
			count_add = 1
			while did_add is False and count_add <= 3:
				did_add = self.atc(offer_id, account_item)
				count_add += 1
			if did_add is False:
				return

			item_id, fulfillment_option, ship_method = self.check_cart_items(account_item)
			self.submit_shipping_method(item_id, fulfillment_option, ship_method, account_item)
			self.submit_shipping_address(account_item)
			card_data, PIE_key_id, PIE_phase = self.get_PIE(account_item)
			pi_hash = self.submit_payment(card_data, PIE_key_id, PIE_phase, account_item)
			self.submit_billing(pi_hash, account_item)
			self.submit_order(account_item)

	def monitor(self):
		headers = {
			"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"cache-control": "max-age=0",
			"upgrade-insecure-requests": "1",
			"user-agent": settings.userAgent
		}
		image_found = False
		product_image = ""
		while True:
			self.status_signal.emit({"msg": "Monitoring Product Page", "status": "normal"})
			try:
				monitor_proxy = get_proxy(self.monitor_proxies)
				if monitor_proxy is not None and monitor_proxy != "":
					self.session.proxies.update(monitor_proxy)
					logger.info("Monitoring by proxy : {}".format(monitor_proxy))

				r = self.session.get(self.product, headers=headers)
				if r.status_code == 200:
					# check for captcha page
					if self.is_captcha(r.text):
						self.status_signal.emit({"msg": "CAPTCHA - Opening Product Page", "status": "error"})
						self.handle_captcha(self.product)
						continue

					doc = lxml.html.fromstring(r.text)
					vendor = doc.xpath('//a[@class="seller-name"]/text()')[0]
					if "walmart" != vendor.lower():
						self.status_signal.emit({"msg": "Seller is not Walmart", "status": "error"})
						return "", None
					if not image_found:
						product_image = doc.xpath('//meta[@property="og:image"]/@content')[0]
						self.image_signal.emit(product_image)
						image_found = True
					price = float(doc.xpath('//span[@itemprop="price"]/@content')[0])
					if "add to cart" in r.text.lower():
						if self.max_price != "":
							if float(self.max_price) < price:
								self.status_signal.emit({"msg": "Waiting For Price Restock", "status": "normal"})
								self.session.cookies.clear()
								time.sleep(random_delay(self.monitor_delay, settings.random_delay_start,
														settings.random_delay_stop))
								continue
						offer_id = json.loads(doc.xpath('//script[@id="item"]/text()')[0])["item"]["product"]["buyBox"][
							"products"][0]["offerId"]
						return product_image, offer_id
					self.status_signal.emit({"msg": "Waiting For Restock", "status": "normal"})
					self.session.cookies.clear()
					time.sleep(random_delay(self.monitor_delay, settings.random_delay_start, settings.random_delay_stop))
				else:
					self.status_signal.emit({"msg": "Product Not Found", "status": "normal"})
					time.sleep(random_delay(self.monitor_delay, settings.random_delay_start, settings.random_delay_stop))
			except Exception as e:
				self.status_signal.emit({"msg": "Error Loading Product Page (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def atc(self, offer_id, account):
		headers = {
			"accept": "application/json",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": self.product,
			"user-agent": settings.userAgent,
			"wm_offer_id": offer_id
		}
		profile = get_profile(account['profile'])
		body = {"offerId": offer_id, "quantity": int(self.max_quantity),
				"location": {"postalCode": profile["shipping_zipcode"], "city": profile["shipping_city"],
							 "state": profile["shipping_state"], "isZipLocated": True},
				"shipMethodDefaultRule": "SHIP_RULE_1"}

		while True:
			self.status_signal.emit({"msg": "Adding To Cart", "status": "normal"})
			try:
				shopping_proxy = get_proxy(account['proxy'])
				if shopping_proxy is not None and shopping_proxy != "":
					logger.info("Walmart | Task id : {} - Shopping proxy : : {}".format(self.task_id, shopping_proxy))
					self.session.proxies.update(shopping_proxy)
				else:
					logger.info("Walmart | Task id : {} - Shopping without proxy".format(self.task_id))

				r = self.session.post("https://www.walmart.com/api/v3/cart/guest/:CID/items", json=body,
									  headers=headers)

				# check for captcha page
				if self.is_captcha(r.text):
					self.status_signal.emit({"msg": "Opening CAPTCHA", "status": "error"})
					self.handle_captcha(self.product)
					return False

				if r.status_code == 201 or r.status_code == 200 and json.loads(r.text)["checkoutable"] == True:
					self.status_signal.emit({"msg": "Added To Cart", "status": "carted"})
					return True
				else:
					logger.info("Walmart | Task id : {} - status code : {}".format(self.task_id, r.status_code))
					blocked_url = "https://www.walmart.com" + json.loads(r.text)["redirectUrl"]
					self.handle_captcha(blocked_url)
					self.status_signal.emit({"msg": "Error Adding To Cart", "status": "error"})
					time.sleep(self.error_delay)
					return False
			except Exception as e:
				self.status_signal.emit({"msg": "Error Adding To Cart (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)
				return False

	def check_cart_items(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent,
			"wm_vertical_id": "0",
			"wm_cvv_in_session": "true",
		}

		profile = get_profile(account['profile'])
		body = {"postalCode": profile["shipping_zipcode"], "city": profile["shipping_city"],
				"state": profile["shipping_state"], "isZipLocated": True, "crt:CRT": "", "customerId:CID": "",
				"customerType:type": "", "affiliateInfo:com.wm.reflector": "", "storeList": []}

		while True:
			self.status_signal.emit({"msg": "Loading Cart Items", "status": "normal"})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract?page=CHECKOUT_VIEW", json=body,
									  headers=headers)# this sometimes returns json data related to loading a captcha.js file so that could be intercepted when requests fail

				if r.status_code == 201 or r.status_code == 200:
					r = json.loads(r.text)["items"][0]
					item_id = r["id"]
					fulfillment_option = r["fulfillmentSelection"]["fulfillmentOption"]
					ship_method = r["fulfillmentSelection"]["shipMethod"]
					self.status_signal.emit({"msg": "Loaded Cart Items", "status": "normal"})
					return item_id, fulfillment_option, ship_method
				else:
					if json.loads(r.text)["message"] == "Item is no longer in stock.":
						self.status_signal.emit({"msg": "Waiting For Restock", "status": "normal"})
						time.sleep(
							random_delay(self.monitor_delay, settings.random_delay_start, settings.random_delay_stop))
					else:
						if self.is_captcha(r.text):
							self.handle_captcha("https://www.walmart.com/checkout")
						self.status_signal.emit(
							{"msg": "Error Loading Cart Items, Got Response: " + str(r.text), "status": "error"})
						time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Loading Cart Items (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def submit_shipping_method(self, item_id, fulfillment_option, ship_method, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent,
			"wm_vertical_id": "0"
		}
		body = {"groups": [{"fulfillmentOption": fulfillment_option, "itemIds": [item_id], "shipMethod": ship_method}]}
		while True:
			self.status_signal.emit({"msg": "Submitting Shipping Method", "status": "normal"})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/fulfillment", json=body,
									  headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"msg": "Submitted Shipping Method", "status": "normal"})
						return
					except:
						pass
				self.status_signal.emit({"msg": "Error Submitting Shipping Method", "status": "error"})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Submitting Shipping Method (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def submit_shipping_address(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"inkiru_precedence": "false",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent,
			"wm_vertical_id": "0"
		}
		profile = get_profile(account['profile'])
		body = {
			"addressLineOne": profile["shipping_a1"],
			"city": profile["shipping_city"],
			"firstName": profile["shipping_fname"],
			"lastName": profile["shipping_lname"],
			"phone": profile["shipping_phone"],
			"email": profile["shipping_email"],
			"marketingEmailPref": False,
			"postalCode": profile["shipping_zipcode"],
			"state": profile["shipping_state"],
			"countryCode": "USA",
			"addressType": "RESIDENTIAL",
			"changedFields": []
		}
		if profile["shipping_a2"] != "":
			body.update({"addressLineTwo": profile["shipping_a2"]})
		while True:
			self.status_signal.emit({"msg": "Submitting Shipping Address", "status": "normal"})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/shipping-address",
									  json=body, headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"msg": "Submitted Shipping Address", "status": "normal"})
						return
					except:
						pass
				self.status_signal.emit({"msg": "Error Submitting Shipping Address", "status": "error"})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Submitting Shipping Address (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def get_PIE(self, account):
		headers = {
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"Connection": "keep-alive",
			"Host": "securedataweb.walmart.com",
			"Referer": "https://www.walmart.com/",
			"User-Agent": settings.userAgent
		}
		profile = get_profile(account['profile'])
		while True:
			self.status_signal.emit({"msg": "Getting Checkout Data", "status": "normal"})
			try:
				r = self.session.get(
					"https://securedataweb.walmart.com/pie/v1/wmcom_us_vtg_pie/getkey.js?bust=" + str(int(time.time())),
					headers=headers)
				if r.status_code == 200:
					PIE_L = int(r.text.split("PIE.L = ")[1].split(";")[0])
					PIE_E = int(r.text.split("PIE.E = ")[1].split(";")[0])
					PIE_K = str(r.text.split('PIE.K = "')[1].split('";')[0])
					PIE_key_id = str(r.text.split('PIE.key_id = "')[1].split('";')[0])
					PIE_phase = int(r.text.split('PIE.phase = ')[1].split(';')[0])
					card_data = w_e.encrypt(profile["card_number"], profile["card_cvv"], PIE_L, PIE_E, PIE_K,
											PIE_key_id, PIE_phase)
					self.status_signal.emit({"msg": "Got Checkout Data", "status": "normal"})
					return card_data, PIE_key_id, PIE_phase
				self.status_signal.emit({"msg": "Error Getting Checkout Data", "status": "error"})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Getting Checkout Data (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def submit_payment(self, card_data, PIE_key_id, PIE_phase, account):
		headers = {
			"accept": "application/json",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent
		}
		# "inkiru_precedence": "false",
		profile = get_profile(account['profile'])
		body = {
			"encryptedPan": card_data[0],
			"encryptedCvv": card_data[1],
			"integrityCheck": card_data[2],
			"keyId": PIE_key_id,
			"phase": PIE_phase,
			"state": profile["billing_state"],
			"postalCode": profile["billing_zipcode"],
			"addressLineOne": profile["billing_a1"],
			"addressLineTwo": profile["billing_a2"],
			"city": profile["billing_city"],
			"firstName": profile["billing_fname"],
			"lastName": profile["billing_lname"],
			"expiryMonth": profile["card_month"],
			"expiryYear": profile["card_year"],
			"phone": profile["billing_phone"],
			"cardType": profile["card_type"].upper(),
			"isGuest": True
		}
		while True:
			self.status_signal.emit({"msg": "Submitting Payment", "status": "normal"})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout-customer/:CID/credit-card", json=body,
									  headers=headers)
				if r.status_code == 200:
					pi_hash = json.loads(r.text)["piHash"]
					self.status_signal.emit({"msg": "Submitted Payment", "status": "normal"})
					return pi_hash
				self.status_signal.emit({"msg": "Error Submitting Payment", "status": "error"})
				logger.error("Walmart | Task id : {} - Error Submitting Payment - Status code : {} - msg : {}".format(self.task_id, r.status_code, r.text))
				if self.check_browser(account):
					return
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Submitting Payment (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def submit_billing(self, pi_hash, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent,
			"wm_vertical_id": "0"
		}

		profile = get_profile(account['profile'])
		card_data, PIE_key_id, PIE_phase = self.get_PIE(account)
		body = {
			"payments": [{
				"paymentType": "CREDITCARD",
				"cardType": profile["card_type"].upper(),
				"firstName": profile["billing_fname"],
				"lastName": profile["billing_lname"],
				"addressLineOne": profile["billing_a1"],
				"addressLineTwo": profile["billing_a2"],
				"city": profile["billing_city"],
				"state": profile["billing_state"],
				"postalCode": profile["billing_zipcode"],
				"expiryMonth": profile["card_month"],
				"expiryYear": profile["card_year"],
				"email": profile["billing_email"],
				"phone": profile["billing_phone"],
				"encryptedPan": card_data[0],
				"encryptedCvv": card_data[1],
				"integrityCheck": card_data[2],
				"keyId": PIE_key_id,
				"phase": PIE_phase,
				"piHash": pi_hash
			}]
		}
		while True:
			self.status_signal.emit({"msg": "Submitting Billing", "status": "normal"})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/payment", json=body,
									  headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"msg": "Submitted Billing", "status": "normal"})
						return
					except:
						pass
				self.status_signal.emit({"msg": "Error Submitting Billing", "status": "error"})
				if self.check_browser(account):
					return
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"msg": "Error Submitting Billing (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def submit_order(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": settings.userAgent,
			"wm_vertical_id": "0"
		}
		profile = get_profile(account['profile'])
		if settings.dont_buy is True:
			# TODO: this used to open the page up with everything filled out but only works for some users
			self.status_signal.emit({"msg":"Mock Opening Checkout Page","status":"alt"})
			send_webhook("OP", "Walmart", account["name"], self.task_id, self.product_image)
			return             

		while True:
			self.status_signal.emit({"msg": "Submitting Order", "status": "alt"})
			try:
				r = self.session.put("https://www.walmart.com/api/checkout/v3/contract/:PCID/order", json={},
									 headers=headers)
				try:
					json.loads(r.text)["order"]
					self.status_signal.emit({"msg": "Order Placed", "status": "success"})
					send_webhook("OP", "Walmart", account["name"], self.task_id, self.product_image)
					return
				except:
					self.status_signal.emit({"msg": "Payment Failed", "status": "error"})

					# open the page for checkout if failed to auto submit
					self.handle_captcha("https://www.walmart.com/checkout/#/payment")
					if self.check_browser(account):
						return

					send_webhook("PF", "Walmart", account["name"], self.task_id, self.product_image)
					# delay for next time
					time.sleep(self.SHORT_TIMEOUT)
					return
			except Exception as e:
				self.status_signal.emit({"msg": "Error Submitting Order (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error"})
				time.sleep(self.error_delay)

	def check_browser(self, account):
		profile = get_profile(account['profile'])
		if settings.browser_on_failed:
			self.status_signal.emit(
				{"msg": "Browser Ready", "status": "alt", "url": "https://www.walmart.com/checkout/#/payment",
				 "cookies": [{"name": cookie.name, "value": cookie.value, "domain": cookie.domain} for cookie in
							 self.session.cookies]})
			send_webhook("B", "Walmart", account["name"], self.task_id, self.product_image)
			return True
		return False

	def handle_captcha(self, url_to_open, close_window_after=True,redirect=False):
		'''added redirect arg since captchas are lost when redirecting to the page that triggered them
		this opens up chrome browser to get prompted with captcha'''
		# options = webdriver.ChromeOptions()
		# options.add_argument('--ignore-certificate-errors') #removes SSL errors from terminal
		# options.add_experimental_option("excludeSwitches", ["enable-logging"]) #removes device adapter errors from terminal
		# browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
		logger.info("Walmart | Task id : {} - handle captcha; url: {}".format(self.task_id, url_to_open))
		browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
		browser.get(url_to_open)

		# pass current session cookies to browser before loading url
		for c in self.session.cookies:
				browser.add_cookie({
					'name': c.name,
					'value': c.value,
					'domain': c.domain,
					'path': c.path
				})

		time.sleep(3)
		if "blocked" in str(browser.current_url):            
			# solve captcha by manual
			# self.captcha_mutex.lock()
			# self.wait_poll_signal.emit()
			# try:
			#     # wait for condition to be released
			#     self.captcha_wait_condition.wait(self.captcha_mutex)
			# finally:
			#     # unlock the thread
			#     self.captcha_mutex.unlock()
			
			# solve captcha by api
			logger.info("Walmart | Task id : {} - Waiting 2captcha to solve recaptcha...".format(self.task_id))
			sitekey = browser.find_element_by_xpath('//*[@id="px-captcha"]/div').get_attribute("data-sitekey")
			captcha_result  = twocaptcha_utils.solve_captcha(str(browser.current_url), str(sitekey))

			browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]', captcha_result['code'])
			browser.execute_script("handleCaptcha('{}');".format(captcha_result['code']))

		for c in browser.get_cookies():
			if c['name'] not in [x.name for x in self.session.cookies]:
				self.session.cookies.set(c['name'], c['value'], path=c['path'], domain=c['domain'])

		if close_window_after:
			browser.quit()

	def is_captcha(self, text):
		return '<div class="re-captcha">' in text



