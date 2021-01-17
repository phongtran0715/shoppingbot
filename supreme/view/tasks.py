import sys
import os
import time
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from view.link.links_processing import LinksProcessing
from view.keyword.keywords_processing import KeywordsProcessing
from model.task_model import TaskModel

# Create a worker class
class Worker(QObject):
	finished = pyqtSignal()
	# progress = pyqtSignal(int)

	def __init__(self, parentFrm =None, task_id=None, item=None, 
			category=None, colour=None, size=None, profile=None, task_type=None, proxy=None, parent=None):
		QObject.__init__(self, parent)
		self.parentFrm = parentFrm
		self.task_id = task_id
		self.item = item
		self.category = category
		self.colour = colour
		self.size = size
		self.profile = profile
		self.task_type = task_type
		self.proxy = proxy

	def run(self):
		result = False
		msg = 'unknow'
		count = 1
		print("task type : " + str(self.task_type))
		if self.task_type == 'Links':
			while True:
				link_process = LinksProcessing(self.item, self.category, self.colour, self.size, self.profile, self.proxy)
				result , msg = link_process.process_links()
				print("(count = {})task id: {} - result {} - message {}".format(count, self.task_id, result, msg))
				if result or count > 3:
					break
				count += 1
				time.sleep(10) # seconds
		elif self.task_type == 'Keywords':
			keyword_process_obj = KeywordsProcessing(self.item, self.category, self.colour, self.size, self.profile, self.proxy)
			while True:
				result , msg = keyword_process_obj.process_keyword()
				print("count({})task id: {} result {}".format(count, self.task_id, result))
				if result or count > 3:
					break
				count += 1
				time.sleep(10) # seconds
		else:
			print('Task type is invalid!')
			return
		# Update task status
		self.parentFrm.update_task_status(self.task_id, result, msg)
		self.finished.emit()


class TaskManager():
	def __init__(self, parentForm):
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.threadDict = {}
		self.create_thread()
		self.stop_thread = False
		self.MAX_TRY_COUNT = 10
		self.DELAY_TIME = 10 #second
		self.parent = parentForm

	def create_thread(self):
		query = QSqlQuery("SELECT * FROM task" , self.db_conn)
		while query.next():
			task_id = query.value(0)
			
			item = query.value(1)
			category = query.value(2)
			colour = query.value(3)
			size = query.value(4)
			profile = query.value(5)
			task_type = query.value(6)
			proxy = query.value(7)
			status = query.value(8)

			# Create a QThread object
			self.thread = QThread()
			# Create a worker object
			self.worker = Worker(self, task_id, item, 
			category, colour, size, profile, task_type, proxy)
			#  Move worker to the thread
			self.worker.moveToThread(self.thread)
			# Connect signals and slots
			self.thread.started.connect(self.worker.run)
			self.worker.finished.connect(self.update_task_table)
			self.worker.finished.connect(self.thread.quit)
			
			self.threadDict[task_id] =self. thread
			if str(status) == 'RUNNING':
				print("Start task id : " + str(task_id))
				self.threadDict[task_id].start()

	def run_all_task(self):
		for key in self.threadDict:
			print("Start task id: " + str(key))
			self.threadDict[key].start()

	def remove_all_task(self):
		print('Remove all task')
		self.stop_thread = True
		self.threadDict.clear()

	def add_new_task(self, task_info):
		print('Add new task id : ' + str(task_info.get_task_id()))

		# Create a QThread object
		self.thread = QThread()
		# Create a worker object
		self.worker = Worker(self, task_info.get_task_id(),
			task_info.get_item(),
			task_info.get_category(),
			task_info.get_colour(),
			task_info.get_size(),
			task_info.get_billing_profile(),
			task_info.get_task_type(),
			task_info.get_proxy())
		#  Move worker to the thread
		self.worker.moveToThread(self.thread)
		# Connect signals and slots
		self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.update_task_table)
		self.worker.finished.connect(self.thread.quit)			
		self.threadDict[task_info.get_task_id()] =self. thread
		self.threadDict[task_info.get_task_id()].start()

	def remove_task(self,task_id):
		print('Remove task id : ' + str(task_id))
		if task_id in self.threadDict:
			del self.threadDict[task_id]
			print("Removed task id : {} from dict".format(task_id))

	def update_task_status(self, task_id, run_status, msg):
		print("update task status : id : {} - status : {} - msg {}".format(task_id, run_status, msg))
		status = 'FALSE'
		if run_status:
			status = 'SUCCESS'
		query = QSqlQuery(self.db_conn)
		query.prepare("UPDATE task SET status = ?, details = ? WHERE id = ?")
		query.addBindValue(status)
		query.addBindValue(msg)
		query.addBindValue(task_id)
		if not query.exec():
			print('Can not update task status!')

	def update_task_table(self):
		self.parent.updateTable()



