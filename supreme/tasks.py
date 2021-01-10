import threading
import sys
import os
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class SupremeTaskManager:
	def __init__(self):
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.threadDict = {}
		self.create_thread()

	def create_thread(self):
		query = QSqlQuery("SELECT * FROM task WHERE status = 'Running'" , self.db_conn)
		while query.next():
			task_id = query.value(0)
			task_data = {}
			task_data['id'] = query.value(0)
			task_data['item'] = query.value(1)
			task_data['category'] = query.value(2)
			task_data['colour'] = query.value(3)
			task_data['size'] = query.value(4)
			task_data['profile'] = query.value(5)
			task_data['type'] = query.value(6)
			task_data['proxy'] = query.value(7)
			task_data['status'] = query.value(8)

			thread = threading.Thread(target=self.do_task, args=(task_data))
			thread.deamon = True
			self.threadDict[task_id] = thread

	def run_all_task(self):
		for key in self.threadDict:
			print("Start task id: " + str(key))
			self.threadDict[key].start()

	def remove_all_task(self):
		for key in self.threadDict:
			pass

	def do_task(self, task_data):
		print('Start task id: ' + str(task_data['id']))

	def add_new_task(self, task_id):
		thread = threading.Thread(target=self.do_task, args=())
		thread.deamon = True
		self.threadDict[task_id] = thread
		print("Add new task id : {} to dict".format(task_id))

	def update_task(self, task_id):
		if task_id in self.threadDict:
			pass

	def remove_task(self,task_id):
		if task_id in self.threadDict:
			del threadDict[task_id]
			print("Removed task id : {} from dict".format(task_id))


