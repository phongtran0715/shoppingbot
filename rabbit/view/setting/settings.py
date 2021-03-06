import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.profile.new_profile import NewProfile
from configparser import ConfigParser
from view.ui.setting_manager import Ui_formProfileManager
from resource import source



class SettingManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(SettingManager, self).__init__()
		dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "setting_manager.ui"), self)
		self.ui = Ui_formProfileManager()
		self.ui.setupUi(self)
		self.center()

		self.config = ConfigParser()
		self.config.read(os.path.join('data', 'config.ini'))
		self.loadSettingData()
		self.setFixedSize(526, 380)

		self.ui.btnSave.clicked.connect(self.btnSave_clicked)


	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadSettingData(self):
		self.ui.txtWebhook.setText(self.config.get('notification', 'webhook'))
		self.ui.btnBrowerOpened.setChecked(self.config.getint('notification', 'browser_opened'))
		self.ui.btnOrderPlaced.setChecked(self.config.getint('notification', 'order_placed'))
		self.ui.btnPaymentFalse.setChecked(self.config.getint('notification', 'payment_failed'))

		self.ui.btnBrowserPaymentFalse.setChecked(self.config.getint('general', 'open_browser_payment_false'))
		self.ui.btnStopAll.setChecked(self.config.getint('general', 'stop_all_after_success'))
		self.ui.btnDevMode.setChecked(self.config.getint('general', 'dev_mode'))

	def btnSave_clicked(self):
		parser = ConfigParser()
		
		parser.add_section('notification')
		parser.set('notification', 'webhook', self.ui.txtWebhook.text())

		if self.ui.btnBrowerOpened.isChecked():
			parser.set('notification', 'browser_opened', '1')
		else:
			parser.set('notification', 'browser_opened', '0')

		if self.ui.btnOrderPlaced.isChecked():
			parser.set('notification', 'order_placed', '1')
		else:
			parser.set('notification', 'order_placed', '0')

		if self.ui.btnPaymentFalse.isChecked():
			parser.set('notification', 'payment_failed', '1')
		else:
			parser.set('notification', 'payment_failed', '0')


		parser.add_section('general')
		if self.ui.btnBrowserPaymentFalse.isChecked():
			parser.set('general', 'open_browser_payment_false', '1')
		else:
			parser.set('general', 'open_browser_payment_false', '0')

		if self.ui.btnStopAll.isChecked():
			parser.set('general', 'stop_all_after_success', '1')
		else:
			parser.set('general', 'stop_all_after_success', '0')

		if self.ui.btnDevMode.isChecked():
			parser.set('general', 'dev_mode', '1')
		else:
			parser.set('general', 'dev_mode', '0')

		with open(os.path.join('data', 'config.ini'), 'w') as configfile:
			parser.write(configfile)

		QMessageBox.about(self, "Rabbit", 'Save setting successful')


	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")