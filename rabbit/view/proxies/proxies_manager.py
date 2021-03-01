import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.proxies.new_proxy_dialog import NewProxy


class ProxiesManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProxiesManager, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "proxies_manager.ui"), self)
		self.center()

		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		
		# create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.tbProxies.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tbProxies.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.tbProxies.setColumnHidden(0, True);
		self.loadProxyData()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadProxyData(self):
		self.tbProxies.setRowCount(0)
		query = QSqlQuery("SELECT * FROM proxies", self.db_conn)
		while query.next():
			rows = self.tbProxies.rowCount()
			self.tbProxies.setRowCount(rows + 1)
			self.tbProxies.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbProxies.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbProxies.setItem(rows, 2, QTableWidgetItem(query.value(2)))

	def btnAdd_clicked(self):
		self.new_proxy_frm = NewProxy()
		if self.new_proxy_frm.exec_() == QtWidgets.QDialog.Accepted:
			self.new_proxy_frm.create_proxy()
			self.loadProxyData()

	def btnEdit_clicked(self):
		index = self.tbProxies.currentRow()
		if index >= 0:
			proxy_id = self.tbProxies.item(index, 0).text()
			self.edit_proxy_frm = NewProxy(True, proxy_id)
			if self.edit_proxy_frm.exec_() == QtWidgets.QDialog.Accepted:
				self.edit_proxy_frm.update_proxy()
				self.loadProxyData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one proxy!',)

	def btnDelete_clicked(self):
		index = self.tbProxies.currentRow()
		if index >= 0:
			proxy_id = self.tbProxies.item(index, 0).text()
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM Proxies WHERE id = ?")
			query.addBindValue(proxy_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.loadProxyData()
		else:
			QMessageBox.critical(self, "Supreme - Error!", 'You must select one proxy to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all proxy?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM proxies")
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.loadProxyData()

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")