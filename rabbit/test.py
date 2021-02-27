import os, sys, requests
from products import Productions
from bs4 import BeautifulSoup


if __name__ == "__main__":
	url = 'https://www.supremenewyork.com/shop/shirts/mh1a0x7bk'
	url_soldout = 'https://www.supremenewyork.com/shop/shirts/x5xog8iuv'
	product = Productions()
	result = product.add_to_cart(url)
	# if result:
	# 	product.checkout()