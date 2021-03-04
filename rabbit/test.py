import os, sys, requests
from utils.rabbit_util import RabbitUtil


if __name__ == "__main__":
	RabbitUtil.send_webhook("OP", "GameStop", "phongtran0715", "100", "")