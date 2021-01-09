from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from keywords import KeywordManager
from profiles import ProfileManager
from links import LinkManager
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import sys
import os
import logging


class QTextEditLogger(logging.Handler):
	def __init__(self, parent):
		super().__init__()
		self.widget = QtWidgets.QPlainTextEdit(parent)
		self.widget.setReadOnly(True)

	def emit(self, record):
		msg = self.format(record)
		self.widget.appendPlainText(msg)


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "supreme.ui"), self)
		self.center()

		# custom console text box
		self.txtConsole = QTextEditLogger(self.groupBox)
		self.gridLayout_2.addWidget(self.txtConsole.widget, 3, 0, 1, 1)
		self.txtConsole.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
		logging.getLogger().addHandler(self.txtConsole)
		# You can control the logging level
		logging.getLogger().setLevel(logging.INFO)


		# create connection for button
		self.actionProfile_Manager.triggered.connect(self.actionProfileManaget_triggered)
		self.btnProfileManager.clicked.connect(self.btnProfileManager_clicked)
		self.btnAddKeyword.clicked.connect(self.btnAddKeyword_clicked)
		self.btnAddLink.clicked.connect(self.btnAddLink_clicked)
		
		self.btnStart.clicked.connect(self.btnStart_clicked)
		self.btnStartAll.clicked.connect(self.btnStartAll_clicked)

		self.btnStop.clicked.connect(self.btnStop_clicked)
		self.btnStopAll.clicked.connect(self.btnStopAll_clicked)

		self.btnEdit.clicked.connect(self.btnEdit_clicked)

		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.btnExit.clicked.connect(self.btnExit_clicked)

		# create table header
		self.tbListTask.setHorizontalHeaderLabels(["ID", "ITEM", "CATEGORY", "COLOUR", "SIZE", "PROFILE", "TYPE", "PROXY", "STATUS"])
		self.loadTaskData()

	def center(self):
		# geometry of the main window
		qr = self.frameGeometry()
		# center point of screen
		cp = QDesktopWidget().availableGeometry().center()
		# move rectangle's center point to screen's center point
		qr.moveCenter(cp)
		# top left of rectangle becomes top left of window centering it
		self.move(qr.topLeft())

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

	def btnProfileManager_clicked(self):
		self.profileFrm = ProfileManager()
		self.profileFrm.show()

	def actionProfileManaget_triggered(self):
		self.profileFrm = ProfileManager()
		self.profileFrm.show()

	def btnAddKeyword_clicked(self):
		self.keywordFrm = KeywordManager()
		if self.keywordFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.keywordFrm.updateKeyword()
			self.loadTaskData()

	def btnAddLink_clicked(self):
		self.linkFrm = LinkManager()
		if self.linkFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.linkFrm.updateLink()
			self.loadTaskData()

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
					logging.info("Start task id {} false".format(task_index))
				else:
					logging.info("Start task id {} successful".format(task_index))
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
					if not query.exec():
						QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
						logging.info("Start task id {} false".format(task_index))
					else:
						logging.info("Start task id {} successful".format(task_index))
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
					logging.info("Start task id {} false".format(task_index))
				else:
					logging.info("Stop task id {} successful".format(task_index))
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
					if not query.exec():
						QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % db_conn.lastError().databaseText(),)
						logging.info("Start task id {} false".format(task_index))
					else:
						logging.info("Stop task id {} successful".format(task_index))
			self.loadTaskData()

	def btnEdit_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_index = self.tbListTask.item(index, 0).text()
			task_type = self.tbListTask.item(index, 6).text()
			task_data = (self.tbListTask.item(index, 1).text(),
				self.tbListTask.item(index, 2).text(),
				self.tbListTask.item(index, 3).text(),
				self.tbListTask.item(index, 4).text(),
				self.tbListTask.item(index, 5).text(),
				self.tbListTask.item(index, 7).text(),
				self.tbListTask.item(index, 8).text(),
				)
			if task_type == 'Keywords':
				self.keywordFrm = KeywordManager('modify', task_index)
				self.keywordFrm.loadKeywordData(task_data)
				if self.keywordFrm.exec_() == QtWidgets.QDialog.Accepted:
					self.keywordFrm.updateKeyword()
					self.loadTaskData()
			elif task_type == 'Links':
				self.linkFrm = LinkManager('modify', task_index)
				self.linkFrm.loadLinkData(task_data)
				if self.linkFrm.exec_() == QtWidgets.QDialog.Accepted:
					self.linkFrm.updateLink()
					self.loadTaskData()
			else:
				pass
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
				logging.info("Delete task id {} false".format(task_index))
			else:
				logging.info("Delete task id {} successful".format(task_index))
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
				logging.info("Delete task id {} false".format(task_index))
			else:
				logging.info("Delete task id {} successful".format(task_index))
				self.loadTaskData()

	def btnExit_clicked(self):
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
	db_conn = QSqlDatabase.addDatabase("QSQLITE", "supreme_db_conn")
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