import pyodbc
conn = pyodbc.connect ('Driver={SQL Server};)'
                       'Server =localhost ',
                       'Database = AdvertisementsDb;',
                       'Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute ('SELECT * FROM AdvertisementsDb')

for row in cursor:
    print(row)