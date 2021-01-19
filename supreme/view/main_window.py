import sys
import os
import logging
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

from view.keyword.keywords_manager import KeywordManager
from view.link.links_manager import LinkManager
from view.profile.profiles_manager import ProfileManager
from model.task_model import TaskModel
from view.tasks import TaskManager

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
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "supreme.ui"), self)
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
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
		self.tbListTask.setHorizontalHeaderLabels(["ID", "ITEM", "CATEGORY", "COLOUR", "SIZE", "PROFILE", "TYPE", "PROXY", "STATUS", "DETAILS"])
		self.tbListTask.setColumnHidden(0, True);
		# self.tbListTask.setColumnHidden(9, True);
		self.loadTaskData()

		# Start existing task
		self.task_manager = TaskManager(self)


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
		query = QSqlQuery("SELECT * FROM task", self.db_conn)
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
			self.tbListTask.setItem(rows, 9, QTableWidgetItem(query.value(9)))

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
			task_info = TaskModel(
				self.tbListTask.item(index, 0).text(),
				self.tbListTask.item(index, 1).text(),
				self.tbListTask.item(index, 2).text(),
				self.tbListTask.item(index, 3).text(),
				self.tbListTask.item(index, 4).text(),
				self.tbListTask.item(index, 5).text(),
				self.tbListTask.item(index, 6).text(),
				self.tbListTask.item(index, 7).text(),
				self.tbListTask.item(index, 8).text())
			if task_info.get_status() == 'Running':
				QMessageBox.critical(self, "Supreme", 'Task have already running!',)
			else:	
				# run this task
				self.task_manager.add_new_task(task_info)

				# udpate database
				query = QSqlQuery(self.db_conn)
				query.prepare("UPDATE task SET status = ? WHERE id = ?")
				query.addBindValue('Running')
				query.addBindValue(task_info.get_task_id())
				if not query.exec():
					QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
					logging.info("Start task id {} false".format(task_info.get_task_id()))
				else:
					logging.info("Start task id {} successful".format(task_info.get_task_id()))
					self.loadTaskData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one row!',)

	def btnStartAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to start all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			# update database
			for row in range(self.tbListTask.rowCount()): 
				task_id = self.tbListTask.item(row, 0).text()
				task_status = self.tbListTask.item(row, 8).text()
				query = QSqlQuery(self.db_conn)
				query.prepare("UPDATE task SET status = ? WHERE id = ?")
				query.addBindValue('Running')
				query.addBindValue(task_id)
				if not query.exec():
					QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
					logging.info("Start task id {} false".format(task_id))
				else:
					logging.info("Start task id {} successful".format(task_id))
					
			self.loadTaskData()
			#  run all task
			self.task_manager.run_all_task()
						

	def btnStop_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_id = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 8).text()
			if task_status == 'Stop':
				QMessageBox.critical(self, "Supreme", 'Task have already stopped!',)
			else:
				# stop task
				self.task_manager.remove_task(task_id)
				# update datbase
				query = QSqlQuery(self.db_conn)
				query.prepare("UPDATE task SET status = ? WHERE id = ?")
				query.addBindValue('Stop')
				query.addBindValue(task_id)
				if not query.exec():
					QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
					logging.info("Start task id {} false".format(task_id))
				else:
					logging.info("Stop task id {} successful".format(task_id))
					self.loadTaskData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one task!',)

	def btnStopAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to stop all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			# stop all task
			self.task_manager.remove_all_task()
			# update database
			for row in range(self.tbListTask.rowCount()): 
				task_id = self.tbListTask.item(row, 0).text()
				task_status = self.tbListTask.item(row, 8).text()
				if task_status == 'Running':
					query = QSqlQuery(self.db_conn)
					query.prepare("UPDATE task SET status = ? WHERE id = ?")
					query.addBindValue('Stop')
					query.addBindValue(task_id)
					if not query.exec():
						QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
						logging.info("Start task id {} false".format(task_id))
					else:
						logging.info("Stop task id {} successful".format(task_id))
			self.loadTaskData()

	def btnEdit_clicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			# Check status, only edit if status != Running
			task_status = self.tbListTask.item(index, 0).text()
			task_id = self.tbListTask.item(index, 0).text()
			task_type = self.tbListTask.item(index, 6).text()
			task_info = TaskModel(
				self.tbListTask.item(index, 0).text(),
				self.tbListTask.item(index, 1).text(),
				self.tbListTask.item(index, 2).text(),
				self.tbListTask.item(index, 3).text(),
				self.tbListTask.item(index, 4).text(),
				self.tbListTask.item(index, 5).text(),
				self.tbListTask.item(index, 6).text(),
				self.tbListTask.item(index, 7).text(),
				self.tbListTask.item(index, 8).text())
			if task_type == 'Keywords':
				self.keywordFrm = KeywordManager('modify', task_id)
				self.keywordFrm.loadKeywordData(task_info)
				if self.keywordFrm.exec_() == QtWidgets.QDialog.Accepted:
					self.keywordFrm.updateKeyword()
					self.loadTaskData()
			elif task_type == 'Links':
				self.linkFrm = LinkManager('modify', task_id)
				self.linkFrm.loadLinkData(task_info)
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
			# reload table
			task_id = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 8).text()
			if task_status == 'Running':
				QMessageBox.critical(self, "Supreme", 'task is running. You must stop task before close')
				return
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM task WHERE id = ?")
			query.addBindValue(task_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
				logging.info("Delete task id {} false".format(task_id))
			else:
				logging.info("Delete task id {} successful".format(task_id))
				self.loadTaskData()

				# update task manager
				self.task_manager.remove_task(task_id)
		else:
			QMessageBox.critical(self, "Supreme - Error!", 'You must select one task to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM task WHERE status != 'Running'")
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
				logging.info("Delete all task false")
			else:
				logging.info("Delete all task successful")
				self.loadTaskData()

				# update task manager
				self.task_manager.remove_all_task()

	def btnExit_clicked(self):
		self.close()

	def updateTable(self):
		print('Update task table...')
		self.loadTaskData()