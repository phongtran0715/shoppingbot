from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os


class LinkManager(QtWidgets.QDialog):
	def __init__(self, mode='new', task_id=None):
		super(LinkManager, self).__init__()
		uic.loadUi(os.path.join("ui", "new_link_dialog.ui"), self)
		self.center()
		self.mode = mode
		self.task_id = task_id
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)

		query = QSqlQuery("SELECT * FROM profile", self.db_conn)
		while query.next():
			self.cbProfile.addItem(query.value(1))

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadLinkData(self, task_data):
		self.txtLink.setPlainText(task_data[0])

		# index = self.cbCategory.findText(task_data[1], QtCore.Qt.MatchFixedString)
		# if index >= 0:
		# 	self.cbCategory.setCurrentIndex(index)

		index = self.cbSize.findText(task_data[2], QtCore.Qt.MatchFixedString)
		if index >= 0:
			self.cbSize.setCurrentIndex(index)

		index = self.cbColor.findText(task_data[3], QtCore.Qt.MatchFixedString)
		if index >= 0:
			self.cbColor.setCurrentIndex(index)

		index = self.cbProfile.findText(task_data[4], QtCore.Qt.MatchFixedString)
		if index >= 0:
			self.cbProfile.setCurrentIndex(index)

		self.txtProxy.setText(task_data[5])

		index = self.cbStatus.findText(task_data[6], QtCore.Qt.MatchFixedString)
		if index >= 0:
			self.cbStatus.setCurrentIndex(index)

	def updateLink(self):
		if self.mode == 'new':
			query = QSqlQuery(self.db_conn)
			query.prepare(
					"""
					INSERT INTO task (
						items,
						category,
						size,
						colour,
						billing_profile,
						type,
						proxy,
						status
					)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?)
					"""
				)
			query.addBindValue(self.txtLink.toPlainText())
			query.addBindValue('')
			query.addBindValue(self.cbSize.currentText())
			query.addBindValue(self.cbColor.currentText())
			query.addBindValue(self.cbProfile.currentText())
			query.addBindValue('Links')
			query.addBindValue(self.txtProxy.text())
			query.addBindValue('Stop')
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.db_conn.lastError().databaseText(),)
			else:
				self.close()
		else:
			query = QSqlQuery(self.db_conn)
			query.prepare(
					"""
					UPDATE task SET 
						items = ?, 
						category = ?, 
						size = ?, 
						colour =?, 
						billing_profile =?, 
						type = ?, 
						proxy = ?, 
						status = ? 
						WHERE id = ?
					"""
				)
			query.addBindValue(self.txtLink.toPlainText())
			query.addBindValue('')
			query.addBindValue(self.cbSize.currentText())
			query.addBindValue(self.cbColor.currentText())
			query.addBindValue(self.cbProfile.currentText())
			query.addBindValue('Links')
			query.addBindValue(self.txtProxy.text())
			query.addBindValue(self.cbStatus.currentText())
			query.addBindValue(self.task_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.db_conn.lastError().databaseText(),)
			else:
				self.close()