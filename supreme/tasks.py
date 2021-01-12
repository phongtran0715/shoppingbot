import threading
import sys
import os
import time
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from links_processing import LinksProcessing
from keywords_processing import KeywordsProcessing


class SupremeTaskManager:
	def __init__(self):
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.threadDict = {}
		self.create_thread()
		self.stop_thread = False
		self.MAX_TRY_COUNT = 10
		self.DELAY_TIME = 10 #second

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
				category, colour, size, profile, task_type, proxy, status))
			thread.deamon = True
			self.threadDict[task_id] = thread

	def run_all_task(self):
		for key in self.threadDict:
			print("Start task id: " + str(key))
			self.threadDict[key].start()

	def remove_all_task(self):
		self.stop_thread = True


	def do_task(self, task_id, item, 
				category, colour, size, profile, task_type, proxy, status):
		result = False
		msg = ''
		count = 1
		if task_type == 'Links':
			link_process_obj = LinksProcessing() 
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

	def update_task_status(self, task_id, run_status, msg):
		status = 'FALSE'
		if run_status:
			status = 'SUCCESS'
		query = QSqlQuery(self.db_conn)
		query.prepare(
				"""
				UPDATE task SET 
					status = ? ,
					details = ?
					WHERE id = ?
				"""
			)
		query.addBindValue(status)
		query.addBindValue(msg)
		query.addBindValue(task_id)
		if not query.exec():
			print('Can not update task status!')


