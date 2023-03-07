import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="pratha",
    password="12345",
    database="AdvertisementsDb"
)
mycursor = mydb.cursor()

mycursor.execute("SELECT * from ad")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)