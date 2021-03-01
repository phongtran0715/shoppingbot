import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.task.new_task_dialog import NewTask
from model.task_model import TaskModel


class TaskManager():
	def __init__(self):
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)

	def get_task(self):
		
		

