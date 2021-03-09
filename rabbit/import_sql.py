from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def import_sql():
	db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
	query = QSqlQuery(db_conn)
	query.prepare('''
		CREATE TABLE "account" (
			"id"	INTEGER NOT NULL,
			"site"	TEXT,
			"name"	TEXT,
			"user_name"	TEXT,
			"password"	TEXT,
			"proxy"	TEXT,
			"billing_profile"	TEXT,
			PRIMARY KEY("id" AUTOINCREMENT)
			)
		''')
	query.exec()

	query.prepare('''
		CREATE TABLE "profile" (
			"id"	INTEGER NOT NULL,
			"profile_name"	TEXT,
			"shipping_first_name"	TEXT,
			"shipping_last_name"	TEXT,
			"shipping_email"	TEXT,
			"shipping_phone"	TEXT,
			"shipping_address_1"	TEXT,
			"shipping_address_2"	TEXT,
			"shipping_city"	TEXT,
			"shipping_zipcode"	TEXT,
			"shipping_state"	TEXT,
			"shipping_country"	TEXT,
			"billing_first_name"	TEXT,
			"billing_last_name"	TEXT,
			"billing_email"	TEXT,
			"billing_phone"	TEXT,
			"billing_address_1"	TEXT,
			"billing_address_2"	TEXT,
			"billing_city"	TEXT,
			"billing_zipcode"	TEXT,
			"billing_state"	TEXT,
			"billing_country"	TEXT,
			"card_type"	TEXT,
			"card_number"	TEXT,
			"card_name"	TEXT,
			"card_cvv"	TEXT,
			"exp_month"	TEXT,
			"exp_year"	TEXT,
			PRIMARY KEY("id" AUTOINCREMENT)
		)
		''')
	query.exec()

	query.prepare('''
		CREATE TABLE "proxies" (
			"id"	INTEGER NOT NULL,
			"name"	TEXT,
			"content"	TEXT,
			PRIMARY KEY("id" AUTOINCREMENT)
		)
		''')
	query.exec()

	query.prepare('''
		CREATE TABLE "task" (
			"id"	INTEGER NOT NULL,
			"product"	TEXT,
			"site"	TEXT,
			"monitor_proxy"	TEXT,
			"monitor_delay"	INTEGER,
			"error_delay"	INTEGER,
			"max_price"	INTEGER,
			"max_quantity"	INTEGER,
			"account"	TEXT,
			PRIMARY KEY("id" AUTOINCREMENT)
		)
		''')
	query.exec()