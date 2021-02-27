import sys
import os
import logging
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

from model.task_model import TaskModel

from view.account.accounts_manager import AccountManager
from view.profile.profiles_manager import ProfileManager
from view.proxies.proxies_manager import ProxiesManager
from view.task.tasks_manager import TaskManager
from view.task.new_task_dialog import NewTask
from view.setting.settings import SettingManager


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "rabbit.ui"), self)
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.center()
		# custom console text box


		# create connection for button
		self.btnNewTask.clicked.connect(self.btnNewTaskClicked)
		self.btnStartAll.clicked.connect(self.btnStartAllClicked)
		self.btnStopAll.clicked.connect(self.btnStopAllClicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAllClicked)

		self.btnStart.clicked.connect(self.btnStartClicked)
		self.btnStop.clicked.connect(self.btnStopClicked)
		self.btnEdit.clicked.connect(self.btnEditClicked)
		self.btnDelete.clicked.connect(self.btnDeleteClicked)

		self.actionAccount.triggered.connect(self.actionAccountClicked)
		self.actionBilling_Profile.triggered.connect(self.actionBilling_ProfileClicked)
		self.actionProxies.triggered.connect(self.actionProxiesClicked)
		self.actionSetting.triggered.connect(self.actionSettingClicked)

		# # create table header
		# self.tbListTask.setHorizontalHeaderLabels(["ID", "ITEM", "CATEGORY", "COLOUR", "SIZE", "PROFILE", "TYPE", "PROXY", "STATUS", "DETAILS"])
		# self.tbListTask.setColumnHidden(0, True);
		# # self.tbListTask.setColumnHidden(9, True);
		# self.loadTaskData()

		# # Start existing task
		# self.task_manager = TaskManager(self)


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

	def actionAccountClicked(self):
		self.accountFrm = AccountManager()
		self.accountFrm.show()

	def actionBilling_ProfileClicked(self):
		self.profileFrm = ProfileManager()
		self.profileFrm.show()

	def actionProxiesClicked(self):
		self.proxieFrm = ProxiesManager()
		self.proxieFrm.show()

	def actionSettingClicked(self):
		self.settingFrm = SettingManager()
		self.settingFrm.show()

	def btnStartClicked(self):
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

	def btnStartAllClicked(self):
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
						
	def btnStopClicked(self):
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

	def btnStopAllClicked(self):
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

	def btnEditClicked(self):
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

	def btnDeleteClicked(self):
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

	def btnDeleteAllClicked(self):
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

	def btnNewTaskClicked(self):
		self.taskFrm = NewTask()
		self.taskFrm.show()

	def btnExit_clicked(self):
		self.close()

	def updateTable(self):
		print('Update task table...')
		self.loadTaskData()