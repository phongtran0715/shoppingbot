import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase
from view.rabbit import MainWindow
from import_sql import *
import logging


if __name__ == "__main__":
	logging.basicConfig(format='[%(asctime)s %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s',
							datefmt='%H:%M:%S',
							level=logging.INFO,
							handlers=[
		logging.FileHandler("app.log"),
		logging.StreamHandler()
	])

	logger = logging.getLogger('__name__')
	logger.addHandler(logging.StreamHandler())

	app = QApplication(sys.argv)
	db_file = os.path.join('data', 'rabbit_db.sqlite')

	# setting database conection
	is_new_db = False
	if not os.path.isfile(db_file):
		is_new_db = True

	db_conn = QSqlDatabase.addDatabase("QSQLITE", "rabbit_db_conn")
	db_conn.setDatabaseName(os.path.join('data', 'rabbit_db.sqlite'))
	if not db_conn.open():
		QMessageBox.critical(
			None,
			'Rabbit - Error!',
			'Database Error: %s' % db_conn.lastError().text(),
			)
	else:
		if is_new_db:
			print("New db. Starting to create table...")
			import_sql()
		window = MainWindow()
		window.show()
		sys.exit(app.exec_())