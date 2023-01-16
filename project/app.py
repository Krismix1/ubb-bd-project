from pyhive import hive

# https://github.com/dropbox/PyHive
cursor = hive.connect("localhost", "20000").cursor()
(cursor.execute("SELECT * FROM bdp.aircrafts_csv_table LIMIT 10"))
print(cursor.fetchall())
