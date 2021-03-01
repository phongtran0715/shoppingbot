import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase
from view.rabbit import MainWindow
import logging


if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO,
                            handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ])

	logger = logging.getLogger('__name__')
	logger.addHandler(logging.StreamHandler())

	app = QApplication(sys.argv)
	db_file = os.path.join('data', 'supreme_db.sqlite')

	# setting database conection
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