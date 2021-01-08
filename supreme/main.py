from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from profile_manager import ProfileWindown
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import sys
import os


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "supreme.ui"), self)

		# create connection for button
		self.actionProfile_Manager.triggered.connect(self.actionProfileManaget_triggered)
		self.btnAddKeyword.clicked.connect(self.btnAddKeyword_clicked)
		
		self.btnStart.clicked.connect(self.btnStart_clicked)
		self.btnStartAll.clicked.connect(self.btnStartAll_clicked)

		self.btnStop.clicked.connect(self.btnStop_clicked)
		self.btnStopAll.clicked.connect(self.btnStopAll_clicked)

		self.btnEdit.clicked.connect(self.btnEdit_clicked)

		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.btnExit.clicked.connect(self.btnExit_clicked)

		# create table header
		self.tbListTask.setColumnCount(9)
		self.tbListTask.setHorizontalHeaderLabels(["ID", "ITEM", "CATEGORY", "COLOUR", "SIZE", "PROFILE", "TYPE", "PROXY", "STATUS"])
		self.tbListTask.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.loadTaskData()

	def loadTaskData(self):
		self.tbListTask.setRowCount(0)
		query = QSqlQuery("SELECT * FROM task", db_conn)
		while query.next():
			rows = self.tbListTask.rowCount()
			self.tbListTask.setRowCount(rows + 1)
			self.tbListTask.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbListTask.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbListTask.setItem(rows, 2, QTableWidgetItem(query.value(2)))
			self.tbListTask.setItem(rows, 3, QTableWidgetItem(query.value(3)))
			self.tbListTask.setItem(rows, 4, QTableWidgetItem(query.value(4)))
			self.tbListTask.setItem(rows, 5, QTableWidgetItem(query.value(5)))
			self.tbListTask.setItem(rows, 6, QTableWidgetItem(query.value(6)))
			self.tbListTask.setItem(rows, 7, QTableWidgetItem(query.value(7)))
			self.tbListTask.setItem(rows, 8, QTableWidgetItem(query.value(8)))

	def btnAddKeyword_clicked(self):
		self.keywordFrm = Keywords()
		self.keywordFrm.show()
		self.loadTaskData()

	def actionProfileManaget_triggered(self):
		self.profileFrm = ProfileWindown()
		self.profileFrm.show()

	def btnStart_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_index = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 8).text()
			if task_status == 'Running':
				QMessageBox.critical(self, "Supreme", 'Task have already running!',)
			else:	
				# TODO: run this task
				query = QSqlQuery(db_conn)
				query.prepare("UPDATE task SET status = ? WHERE id = ?")
				query.addBindValue('Running')
				query.addBindValue(task_index)
				if not query.exec():
					QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
				else:
					self.loadTaskData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one row!',)

	def btnStartAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to start all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			for row in range(self.tbListTask.rowCount()): 
				task_index = self.tbListTask.item(row, 0)
				task_status = self.tbListTask.item(row, 8)
				if task_status == 'Stop':
					query = QSqlQuery(db_conn)
					query.prepare("UPDATE task SET status = ? WHERE id = ?")
					query.addBindValue('Running')
					query.addBindValue(task_index)
			self.loadTaskData()
						

	def btnStop_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_index = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 8).text()
			if task_status == 'Stop':
				QMessageBox.critical(self, "Supreme", 'Task have already stopped!',)
			else:
				query = QSqlQuery(db_conn)
				query.prepare("UPDATE task SET status = ? WHERE id = ?")
				query.addBindValue('Stop')
				query.addBindValue(task_index)
				if not query.exec():
					QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
				else:
					self.loadTaskData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one task!',)

	def btnStopAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to stop all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			for row in range(self.tbListTask.rowCount()): 
				task_index = self.tbListTask.item(row, 0)
				task_status = self.tbListTask.item(row, 8)
				if task_status == 'Running':
					query = QSqlQuery(db_conn)
					query.prepare("UPDATE task SET status = ? WHERE id = ?")
					query.addBindValue('Stop')
					query.addBindValue(task_index)
			self.loadTaskData()

	def btnEdit_clicked(self):
		index = self.tbListTask.currentRow()
		task_index = self.tbListTask.item(index, 0).text()
		if index >= 0:
			task_data = (self.tbListTask.item(index, 1).text(),
				self.tbListTask.item(index, 2).text(),
				self.tbListTask.item(index, 3).text(),
				self.tbListTask.item(index, 4).text(),
				self.tbListTask.item(index, 5).text(),
				self.tbListTask.item(index, 7).text(),
				self.tbListTask.item(index, 8).text(),
				)
			self.keywordFrm = Keywords('modify', task_index)
			self.keywordFrm.loadData(task_data)
			self.keywordFrm.show()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one task!',)

	def btnDelete_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_id = self.tbListTask.item(index, 0).text()
			query = QSqlQuery(db_conn)
			query.prepare("DELETE FROM task WHERE id = ?")
			query.addBindValue(task_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
			else:
				self.loadTaskData()
		else:
			QMessageBox.critical(self, "Supreme - Error!", 'You must select one task to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(db_conn)
			query.prepare("DELETE FROM task")
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
			else:
				self.loadTaskData()

	def btnExit_clicked(self):
		self.close()


class Keywords(QtWidgets.QMainWindow):
	def __init__(self, mode='new', task_id=None):
		super(Keywords, self).__init__()
		uic.loadUi(os.path.join("ui", "add_keywords.ui"), self)
		self.mode = mode
		self.task_id = task_id

		self.btnCancel.clicked.connect(self.btnCancel_clicked)
		self.btnKeywordOK.clicked.connect(self.btnKeywordOK_clicked)

		query = QSqlQuery("SELECT * FROM profile", db_conn)
		while query.next():
			self.cbProfile.addItem(query.value(1))

	def loadData(self, task_data):
		self.txtKeyword.setText(task_data[0])

		index = self.cbCategory.findText(task_data[1], QtCore.Qt.MatchFixedString)
		if index >= 0:
			self.cbCategory.setCurrentIndex(index)

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

	def btnKeywordOK_clicked(self):
		if self.mode == 'new':
			query = QSqlQuery(db_conn)
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
			query.addBindValue(self.txtKeyword.text())
			query.addBindValue(self.cbCategory.currentText())
			query.addBindValue(self.cbSize.currentText())
			query.addBindValue(self.cbColor.currentText())
			query.addBindValue(self.cbProfile.currentText())
			query.addBindValue('Keywords')
			query.addBindValue(self.txtProxy.text())
			query.addBindValue('Stop')
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
		else:
			query = QSqlQuery(db_conn)
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
			query.addBindValue(self.txtKeyword.text())
			query.addBindValue(self.cbCategory.currentText())
			query.addBindValue(self.cbSize.currentText())
			query.addBindValue(self.cbColor.currentText())
			query.addBindValue(self.cbProfile.currentText())
			query.addBindValue('Keywords')
			query.addBindValue(self.txtProxy.text())
			query.addBindValue(self.cbStatus.currentText())
			query.addBindValue(self.task_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
			pass

		self.close()

	def btnCancel_clicked(self):
		self.close()


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	db_file = os.path.join('data', 'supreme_db.sqlite')

	if not os.path.isfile(db_file):
		QMessageBox.critical(
			None,
			'Supreme - Error!',
			'Can not find database file: %s' % db_file,
			)
		sys.exit(1)
	db_conn = QSqlDatabase.addDatabase("QSQLITE")
	db_conn.setDatabaseName(os.path.join('data', 'supreme_db.sqlite'))
	if not db_conn.open():
		QMessageBox.critical(
			None,
			'Supreme - Error!',
			'Database Error: %s' % db_conn.lastError().databaseText(),
			)
	else:
		window = MainWindow()
		window.show()
		sys.exit(app.exec_())