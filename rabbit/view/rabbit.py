import sys
import os
import logging
from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

from model.task_model import TaskModel

from view.account.accounts_manager import AccountManager
from view.profile.profiles_manager import ProfileManager
from view.proxies.proxies_manager import ProxiesManager
from view.task.new_task_dialog import NewTask
from view.setting.settings import SettingManager

from sites.walmart import Walmart
from sites.bestbuy import BestBuy
from sites.target import Target
from sites.gamestop import GameStop

from model.task_model import TaskModel
import logging


logger = logging.getLogger(__name__)

class TaskThread(QtCore.QThread):
	status_signal = QtCore.pyqtSignal("PyQt_PyObject")
	image_signal = QtCore.pyqtSignal("PyQt_PyObject")
	wait_poll_signal = QtCore.pyqtSignal()
	def __init__(self, task_model):
		QtCore.QThread.__init__(self)
		self.task_model = task_model

	def run(self):
		if self.task_model.get_site() == "Walmart":
			Walmart(self.status_signal, self.image_signal,  self.wait_poll_signal, self.wait_condition, self.task_model)
		elif self.task_model.get_site() == "Bestbuy":
			BestBuy(self.status_signal, self.image_signal, self.task_model)
		elif self.task_model.get_site() == "Target":
			Target(self.status_signal, self.image_signal, self.task_model)
		elif self.task_model.get_site() == "GameStop":
			GameStop(self.status_signal, self.image_signal, self.task_model)

	def stop(self):
		self.terminate()


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "rabbit.ui"), self)
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		self.center()

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

		self.loadTaskData()

		self.tbListTask.setColumnWidth(0, 50)
		self.tbListTask.setColumnWidth(1, 100)
		self.tbListTask.setColumnWidth(2, 600)
		self.tbListTask.setColumnWidth(3, 200)

		self.dict_tasks = {}

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadTaskData(self):
		self.tbListTask.setRowCount(0)
		query = QSqlQuery("SELECT id, site, product, account FROM task", self.db_conn)
		while query.next():
			rows = self.tbListTask.rowCount()
			self.tbListTask.setRowCount(rows + 1)
			self.tbListTask.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbListTask.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbListTask.setItem(rows, 2, QTableWidgetItem(query.value(2)))
			self.tbListTask.setItem(rows, 3, QTableWidgetItem(query.value(3)))
			self.tbListTask.setItem(rows, 4, QTableWidgetItem("Stop"))

		# update total task label
		self.lbTotalTask.setText(str(self.tbListTask.rowCount()))

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
			task_id = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 4).text()
			if task_status == 'Running':
				QMessageBox.critical(self, "Rabbit", 'Task have already running!',)
			else:
				query = QSqlQuery("SELECT * FROM task WHERE id = " + task_id, self.db_conn)
				if query.next():
					task_model = TaskModel(str(query.value(0)),
						query.value(1), query.value(2), query.value(3) , str(query.value(4)),
						str(query.value(5)), str(query.value(6)),str(query.value(7)), query.value(8))
					self.dict_tasks[task_model.get_task_id()] = TaskThread(task_model)
					self.dict_tasks[task_model.get_task_id()].status_signal.connect(self.update_status)
					self.dict_tasks[task_model.get_task_id()].image_signal.connect(self.update_image)
					self.dict_tasks[task_model.get_task_id()].wait_condition = QtCore.QWaitCondition()
					self.dict_tasks[task_model.get_task_id()].start()
					# update task status on table
					msg = {
						'task_id' : task_id,
						'message' : 'Running',
						'status' : 'normal'
					}
					self.update_status(msg)
				else:
					print("Could not found task")


	def btnStartAllClicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to start all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			# update database
			for row in range(self.tbListTask.rowCount()): 
				task_id = self.tbListTask.item(row, 0).text()
				task_status = self.tbListTask.item(row, 4).text()
				pass
					
			self.loadTaskData()
						
	def btnStopClicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_id = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 4).text()
			if task_status == 'Stop':
				QMessageBox.critical(self, "Rabbit", 'Task have already stopped!',)
			else:
				self.dict_tasks[task_id].stop()
				msg = {
						'task_id' : task_id,
						'message' : 'Stop',
						'status' : 'normal'
					}
				self.update_status(msg)
		else:
			QMessageBox.critical(self, "Rabbit", 'You must select one task!',)

	def btnStopAllClicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to stop all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			# stop all task
			for row in range(self.tbListTask.rowCount()): 
				task_id = self.tbListTask.item(row, 0).text()
				task_status = self.tbListTask.item(row, 4).text()
				if task_status == 'Running':
					self.dict_tasks[task_id].stop()
					msg = {
						'task_id' : task_id,
						'message' : 'Stop',
						'status' : 'normal'
					}
					self.update_status(msg)

	def btnEditClicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_id = self.tbListTask.item(index, 0).text()
			self.edittask_frm = NewTask(True, task_id)
			if self.edittask_frm.exec_() == QtWidgets.QDialog.Accepted:
				self.edittask_frm.update_task()
				self.loadTaskData()
		else:
			QMessageBox.critical(self, "Rabbit", 'You must select one task!',)

	def btnDeleteClicked(self):
		index = self.tbListTask.currentRow()
		if index >= 0:
			task_id = self.tbListTask.item(index, 0).text()
			task_status = self.tbListTask.item(index, 4).text()
			if task_status == 'Running':
				QMessageBox.critical(self, "Rabbit", 'task is running. You must stop task before close')
				return
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM task WHERE id = ?")
			query.addBindValue(task_id)
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
				logging.info("Delete task id {} false".format(task_id))
			else:
				logging.info("Delete task id {} successful".format(task_id))
				self.loadTaskData()
		else:
			QMessageBox.critical(self, "Rabbit - Error!", 'You must select one task to delete!',)

	def btnDeleteAllClicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all task?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM task WHERE status != 'Running'")
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
				logging.info("Delete all task false")
			else:
				logging.info("Delete all task successful")
				self.loadTaskData()

	def btnNewTaskClicked(self):
		self.create_task_frm = NewTask()
		if self.create_task_frm.exec_() == QtWidgets.QDialog.Accepted:
			self.create_task_frm.create_task()
			self.loadTaskData()

	def btnExit_clicked(self):
		self.close()

	def update_status(self, msg):
		print("msg: {}".format(msg))
		for index in range(self.tbListTask.rowCount()):
			if msg['task_id'] == self.tbListTask.item(index, 0).text():
				self.tbListTask.item(index, 4).setText(msg['message'])
				if msg['status'] == 'normal':
					self.tbListTask.item(index, 4).setBackground(QtGui.QColor('green'))
				else:
					self.tbListTask.item(index, 4).setBackground(QtGui.QColor('red'))
				break

	def update_image(self,image_url):
		pass
		# self.image_thread = ImageThread(image_url)
		# self.image_thread.finished_signal.connect(self.set_image)
		# self.image_thread.start()