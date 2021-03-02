import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.profile.new_profile import NewProfile
from configparser import ConfigParser



class SettingManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(SettingManager, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "setting_manager.ui"), self)
		self.center()

		self.config = ConfigParser()
		self.config.read(os.path.join('data', 'config.ini'))
		self.loadSettingData()

		self.btnSave.clicked.connect(self.btnSave_clicked)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadSettingData(self):
		self.txtWebhook.setText(self.config.get('notification', 'webhook'))
		self.btnBrowerOpened.setChecked(self.config.getint('notification', 'browser_opened'))
		self.btnOrderPlaced.setChecked(self.config.getint('notification', 'order_placed'))
		self.btnPaymentFalse.setChecked(self.config.getint('notification', 'payment_failed'))

		self.btnBrowserPaymentFalse.setChecked(self.config.getint('general', 'open_browser_payment_false'))
		self.btnStopAll.setChecked(self.config.getint('general', 'stop_all_after_success'))
		self.btnDevMode.setChecked(self.config.getint('general', 'dev_mode'))

	def btnSave_clicked(self):
		parser = ConfigParser()
		
		parser.add_section('notification')
		parser.set('notification', 'webhook', self.txtWebhook.text())

		if self.btnBrowerOpened.isChecked():
			parser.set('notification', 'browser_opened', '1')
		else:
			parser.set('notification', 'browser_opened', '0')

		if self.btnOrderPlaced.isChecked():
			parser.set('notification', 'order_placed', '1')
		else:
			parser.set('notification', 'order_placed', '0')

		if self.btnPaymentFalse.isChecked():
			parser.set('notification', 'payment_failed', '1')
		else:
			parser.set('notification', 'payment_failed', '0')


		parser.add_section('general')
		if self.btnBrowserPaymentFalse.isChecked():
			parser.set('general', 'open_browser_payment_false', '1')
		else:
			parser.set('general', 'open_browser_payment_false', '0')

		if self.btnStopAll.isChecked():
			parser.set('general', 'stop_all_after_success', '1')
		else:
			parser.set('general', 'stop_all_after_success', '0')

		if self.btnDevMode.isChecked():
			parser.set('general', 'dev_mode', '1')
		else:
			parser.set('general', 'dev_mode', '0')

		with open(os.path.join('data', 'config.ini'), 'w') as configfile:
			parser.write(configfile)

		QMessageBox.about(self, "Rabbit", 'Save setting successful')


	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")