import threading
import sys
import os
import time
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from links_processing import LinksProcessing
from keywords_processing import KeywordsProcessing
from model.task_model import TaskModel


class TaskController():
	def __init__(self, parentForm):
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.threadDict = {}
		self.create_thread()
		self.stop_thread = False
		self.MAX_TRY_COUNT = 10
		self.DELAY_TIME = 10 #second
		self.parent = parentForm

	def create_thread(self):
		query = QSqlQuery("SELECT * FROM task WHERE status = 'Running'" , self.db_conn)
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

			thread = threading.Thread(target=self.do_task, args=(task_id, item, 
				category, colour, size, profile, task_type, proxy))
			thread.deamon = True
			self.threadDict[task_id] = thread
			self.threadDict[task_id].start()

	def do_task(self, task_id, item, 
			category, colour, size, profile, task_type, proxy):
		print("do task...")
		result = False
		msg = 'unknow'
		count = 1
		print("task type : " + str(task_type))
		if task_type == 'Links':
			link_process_obj = LinksProcessing() 
			print("000000")
			while result:
				if self.stop_thread:
					break
				result , msg = link_process_obj.process_links(item)
				print("(count = {})task id: {} result {}".format(count, task_id, result))
				if count > 10:
					break
				count += 1
				time.sleep(10) # seconds
		elif task_type == 'Keywords':
			keyword_process_obj = KeywordsProcessing()
			while result:
				if self.stop_thread:
					break;
				result , msg = keyword_process_obj.process_keyword(item)
				print("count({})task id: {} result {}".format(count, task_id, result))
				if count > 10:
					break
				count += 1
				time.sleep(10) # seconds
		else:
			print('Task type is invalid!')
			return
		# Update task status
		self.update_task_status(task_id, result, msg)

	def run_all_task(self):
		for key in self.threadDict:
			print("Start task id: " + str(key))
			if not self.threadDict[key].is_alive():
				self.threadDict[key].start()

	def remove_all_task(self):
		print('Remove all task')
		self.stop_thread = True
		self.threadDict.clear()

	def add_new_task(self, task_info):
		print('Add new task id : ' + str(task_info.get_task_id()))
		thread = threading.Thread(target=self.do_task, args=(task_info.get_task_id(),
			task_info.get_item(),
			task_info.get_category(),
			task_info.get_colour(),
			task_info.get_size(),
			task_info.get_billing_profile(),
			task_info.get_task_type(),
			task_info.get_proxy()
			))
		thread.deamon = True
		self.threadDict[task_info.get_task_id()] = thread
		self.threadDict[task_info.get_task_id()].start()
		print("Add new task id : {} to dict".format(task_info.get_task_id()))

	def update_task(self, task_id):
		print('Update task id : ' + str(task_id))
		query = QSqlQuery("SELECT * FROM task WHERE id = " + str(task_id), self.db_conn)
		if(query.next()):
			status = query.value(8)
			if task_id in self.threadDict:
				pass
				

	def remove_task(self,task_id):
		print('Remove task id : ' + str(task_id))
		if task_id in self.threadDict:
			del threadDict[task_id]
			print("Removed task id : {} from dict".format(task_id))

	def update_task_status(self, task_id, run_status, msg):
		print("update task status : id : {} - status : {} - msg {}".format(task_id, run_status, msg))
		status = 'FALSE'
		if run_status:
			status = 'SUCCESS'
		query = QSqlQuery(self.db_conn)
		query.prepare("UPDATE task SET status = ? WHERE id = ?")
		query.addBindValue('abc')
		query.addBindValue(22)
		if not query.exec():
			print('Can not update task status!')
		# self.parent.updateTable()


