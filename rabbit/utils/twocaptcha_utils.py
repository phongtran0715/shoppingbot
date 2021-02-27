# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

config = {
			'apiKey':'9e3f6fb52aca883e4f563aaf2650cd3f',
			'defaultTimeout':120,
			'recaptchaTimeout':600,
			'pollingInterval':10,
		}
		
# api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(**config)

def solve_captcha(url, sitekey):
	result = None
	try:
		result = solver.recaptcha(
			sitekey=sitekey,
			url=url)

	except Exception as e:
		print(e)
		result = None
	return result