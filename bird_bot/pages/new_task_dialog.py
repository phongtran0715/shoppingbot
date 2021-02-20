import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from utils import return_data,write_data,get_profile,Encryption


class NewTask(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(NewTask, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "new_task_dialog.ui"), self)
		self.homepage = parent
		self.show()
		self.center()
		
		# connect action for button
		self.btnAccountAdd.clicked.connect(self.btnAccountAdd_clicked)
		self.init_data()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def init_data(self):
		proxies = return_data("./data/proxies.json")
		for proxy in proxies:
			self.cbMonitorProxy.addItem(proxy['list_name'])

		accounts = return_data("./data/accounts.json")
		for account in accounts:
			self.cbAccount.addItem(account['name'])

	def btnAccountAdd_clicked(self):
		account_name = self.cbAccount.currentText()
		if account_name is not None and account_name != "":
			current_account = self.txtAccount.text()
			if current_account is not None and current_account != "":
				self.txtAccount.setText(current_account + "," + account_name)
			else:
				self.txtAccount.setText(account_name)

	def save_task(self):
		task_id = int(self.homepage.tasks_total_count.text()) + 1
		task_data = {
			'task_id' : str(task_id),
			'site' : self.cbSite.currentText(),
			'product' : self.txtLink.text(),
			'monitor_proxy' : self.cbMonitorProxy.currentText(),
			'monitor_delay' : self.txtMonitorDelay.text(),
			'error_delay' : self.txtErrorDelay.text(),
			'max_price' : self.txtMaxPrice.text(),
			'max_quantity' : self.txtMaxQuantity.text(),
			'account' : self.txtAccount.text()
		}
		tasks = return_data("./data/tasks.json")
		tasks.append(task_data)
		write_data("./data/tasks.json",tasks)
		self.homepage.add_tab(task_data)

	def update_task(self):
		task_data = {
			'site' : self.cbSite.currentText(),
			'product' : self.txtLink.text(),
			'monitor_proxy' : self.cbMonitorProxy.currentText(),
			'monitor_delay' : self.txtMonitorDelay.text(),
			'error_delay' : self.txtErrorDelay.text(),
			'max_price' : self.txtMaxPrice.text(),
			'max_quantity' : self.txtMaxQuantity.text(),
			'account' : self.txtAccount.text()
		}
		tasks = return_data("./data/tasks.json")
		tasks.append(task_data)
		write_data("./data/tasks.json",tasks)
