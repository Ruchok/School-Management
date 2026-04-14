try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL isn't installed yet this will silently continue;
	# Django will raise a clear import error when starting if it's required.
	pass
