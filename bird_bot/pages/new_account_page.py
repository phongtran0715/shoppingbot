import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *

class NewAccount(QtWidgets.QDialog):
	def __init__(self, mode='new', account_name=None):
		super(NewAccount, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "new_account.ui"), self)
		self.center()
		self.mode = mode
		self.account_name = account_name

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadEditData(self):
		# TODO: load data from json
		pass