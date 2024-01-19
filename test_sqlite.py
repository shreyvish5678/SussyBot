import sqlite3
with sqlite3.connect("user_db.db") as connection:
    cursor = connection.cursor()
    print("\nAll Rows in user_usage Table:")
    cursor.execute("SELECT * FROM user_usage")
    rows = cursor.fetchall()
    for row in rows:
        print(row)