import os, sys, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class LinksProcessing:
	def __init__(self, url, category, colour, size, profile, proxy):
		self.checkout_url = 'https://www.supremenewyork.com/checkout'
		# https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/
		self.webdriver_path="E:\\Program\\chromedriver.exe"
		# check proxy
		if proxy is not None:
			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument('--proxy-server=http://%s' % proxy)
			self.driver = webdriver.Chrome(executable_path=self.webdriver_path, chrome_options=chrome_options)
		else:
			self.driver = webdriver.Chrome(executable_path=self.webdriver_path)

		self.url = url
		self.category = category
		self.coloue = colour
		self.size = size
		self.profile = profile
		self.proxy = proxy

	def process_links(self):
		print("process link : " + str(self.url))
		# check link is active or sold-out
		page = requests.get(self.url)
		soup = BeautifulSoup(page.content, 'html.parser')
		results = soup.find(id='add-remove-buttons')
		print("result : " + str(results))
		if str(results).find('sold-out') != -1:
			print('This product is sold-out')
			self.driver.close()
			return False, 'Product is soldout'

		# add to card
		# TODO: select coloue and size
		add_cart_result = self.add_to_cart(self.url)
		# Check out
		if add_cart_result:
			checkout_result = self.checkout(self.url)
			if checkout_result == False:
				self.driver.close()
				return False, 'Checkout false!'
		else:
			self.driver.close()
			return False, 'Add to cart false!'

		self.driver.close()
		return True, 'Success'

	def add_to_cart(self):
		try:
			self.driver.get(self.url)
			add_button= self.driver.find_element_by_name('commit')
			add_button.click()
			delay = 3
			print("Add to card successful!")
			return True
		except NoSuchElementException:
			print("Can not add product to card")
			return False
		except TimeoutException as toex:
			print("Can not add product to card")
			return False
		except:
			print("Can not add product to card")
			return False

	def checkout(self):
		try:
			self.driver.find_element_by_xpath("//a[contains(@href,'https://www.supremenewyork.com/checkout')]").click()
			delay = 3 # seconds
			print("Start to checkout")
			self.driver.find_element_by_name('order[billing_name]').send_keys('Tran Ngoc Phong')
			self.driver.find_element_by_name('order[email]').send_keys('phongtran0715@gmail.com')
			self.driver.find_element_by_name('order[tel]').send_keys('0984626619')
			self.driver.find_element_by_name('order[billing_zip]').send_keys('72201')
			self.driver.find_element_by_name('order[billing_state]').send_keys('NY')
			self.driver.find_element_by_name('order[billing_city]').send_keys('NY')
			self.driver.find_element_by_name('order[billing_address]').send_keys('Address')
			self.driver.find_element_by_name('credit_card[type]').send_keys('Visa')
			self.driver.find_element_by_name('riearmxa').send_keys('123456')

			month_select = Select(self.driver.find_element_by_name('credit_card[month]'))
			month_select.select_by_index(3)

			year_select = Select(self.driver.find_element_by_name('credit_card[year]'))
			year_select.select_by_index(3)

			self.driver.find_element_by_name('credit_card[meknk]').send_keys('123')
			self.driver.find_elements_by_class_name('iCheck-helper')[1].click()
			self.driver.find_element_by_name('commit').click()

			delay = 3 # seconds
			return True
		except NoSuchElementException:
			print("Can not add product to card")
			return False
		except TimeoutException as toex:
			print("Can not add product to card")
			return False
		except:
			print("Can not add product to card")
			return False








