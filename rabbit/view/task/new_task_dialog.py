import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class NewTask(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, task_id=None, parent=None):
		super(NewTask, self).__init__()
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "new_task_dialog.ui"), self)
		self.task_id = task_id
		self.parent = parent
		self.init_data()
		if modifyMode is True:
			self.load_data()
		self.show()
		self.center()

		# create signal for button
		self.btnAccountAdd.clicked.connect(self.btnAccountAddClicked)
		self.txtLink.textChanged.connect(self.txtLinkChanged)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def init_data(self):
		query = QSqlQuery("SELECT id, name FROM proxies", self.db_conn)
		while query.next():
			self.cbMonitorProxy.addItem(query.value(1))

		query = QSqlQuery("SELECT id, name FROM account", self.db_conn)
		while query.next():
			self.cbAccount.addItem(query.value(1))

	def load_data(self):
		query = QSqlQuery("""
			SELECT product, site, monitor_proxy, monitor_delay, error_delay, max_price, max_quantity, account 
			FROM task WHERE id = """ + str(self.task_id), self.db_conn)
		if query.next():
			self.txtLink.setText(query.value(0))

			index = self.cbSite.findText(query.value(1), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbSite.setCurrentIndex(index)

			index = self.cbMonitorProxy.findText(query.value(2), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbMonitorProxy.setCurrentIndex(index)

			self.txtMonitorDelay.setText(str(query.value(3)))
			self.txtErrorDelay.setText(str(query.value(4)))
			self.txtMaxPrice.setText(str(query.value(5)))
			self.txtMaxQuantity.setText(str(query.value(6)))
			self.txtAccount.setText(query.value(7))

			self.txtLinkChanged()

	def create_task(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(""" INSERT INTO task (product, site, monitor_proxy, monitor_delay, error_delay, 
			max_price, max_quantity, account) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""")
		query.addBindValue(self.txtLink.text())
		query.addBindValue(self.cbSite.currentText())
		query.addBindValue(self.cbMonitorProxy.currentText())
		query.addBindValue(int(self.txtMonitorDelay.text()))
		query.addBindValue(int(self.txtErrorDelay.text()))
		query.addBindValue(int(self.txtMaxPrice.text()))
		query.addBindValue(int(self.txtMaxQuantity.text()))
		query.addBindValue(self.txtAccount.text())
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			# add new row to table
			last_inserted_id = query.lastInsertId()
			print("jack | inserted id : {}".format(last_inserted_id))
			rowPosition = self.parent.tbListTask.rowCount()
			self.parent.tbListTask.insertRow(rowPosition)
			self.parent.tbListTask.setItem(rowPosition , 0, QTableWidgetItem(str(last_inserted_id)))
			self.parent.tbListTask.setItem(rowPosition , 1, QTableWidgetItem(self.cbSite.currentText()))
			self.parent.tbListTask.setItem(rowPosition , 2, QTableWidgetItem(self.txtLink.text()))
			self.parent.tbListTask.setItem(rowPosition , 3, QTableWidgetItem(self.txtAccount.text()))
			self.close()

	def update_task(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(""" UPDATE task SET product = ?, site = ?, monitor_proxy = ?, monitor_delay = ?, error_delay = ?, 
			max_price = ? , max_quantity = ? , account = ? WHERE id = ?""")
		query.addBindValue(self.txtLink.text())
		query.addBindValue(self.cbSite.currentText())
		query.addBindValue(self.cbMonitorProxy.currentText())
		query.addBindValue(self.txtMonitorDelay.text())
		query.addBindValue(self.txtErrorDelay.text())
		query.addBindValue(self.txtMaxPrice.text())
		query.addBindValue(self.txtMaxQuantity.text())
		query.addBindValue(self.txtAccount.text())
		query.addBindValue(self.task_id)
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			# udpate table
			row = self.parent.tbListTask.currentRow()
			self.parent.tbListTask.item(row, 1).setText(self.cbSite.currentText())
			self.parent.tbListTask.item(row, 2).setText(self.txtLink.text())
			self.parent.tbListTask.item(row, 3).setText(self.txtAccount.text())
			self.close()

	def btnAccountAddClicked(self):
		account = self.txtAccount.text()
		if account is None or account == "":
			account += self.cbAccount.currentText()
		else:
			account += "," + self.cbAccount.currentText()

		self.txtAccount.setText(account)

	def txtLinkChanged(self):
		product = self.txtLink.text()
		if "gamestop" in product:
			index = self.cbSite.findText("GameStop", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbSite.setCurrentIndex(index)

				self.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'GameStop'", self.db_conn)
				while query.next():
					self.cbAccount.addItem(query.value(1))
		elif "walmart" in product:
			index = self.cbSite.findText("Walmart", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbSite.setCurrentIndex(index)

				self.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Walmart'", self.db_conn)
				while query.next():
					self.cbAccount.addItem(query.value(1))
		elif "bestbuy" in product:
			index = self.cbSite.findText("Bestbuy", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbSite.setCurrentIndex(index)

				self.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Bestbuy'", self.db_conn)
				while query.next():
					self.cbAccount.addItem(query.value(1))
		elif "target" in product:
			index = self.cbSite.findText("Target", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbSite.setCurrentIndex(index)

				self.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Target'", self.db_conn)
				while query.next():
					self.cbAccount.addItem(query.value(1))