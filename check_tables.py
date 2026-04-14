import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='school_db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA="school_db"')
count = cursor.fetchone()[0]
print(f'Total tables in school_db: {count}')
if count > 0:
    cursor.execute('SHOW TABLES')
    tables = [t[0] for t in cursor.fetchall()]
    print('Tables:', tables)
conn.close()
