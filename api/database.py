import sqlite3

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.cursor = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_url, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print("Connection successful")
        else: 
            print("You're already connected, please disconnect first")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
        else: 
            print("No connection")

    def find_user(self, username):
        if not self.connection:
            print("Not connected to any database.")
            return
        
        query = f"SELECT * FROM users WHERE username = ?"
        res = self.cursor.execute(query, (username,))
        return res.fetchall()

    def insert_user(self, username, hash): 
        if not self.connection:
            print("Not connected to any database.")
            return
        cash = 10000
        query = "INSERT INTO users (username, hash, cash) VALUES (?, ?, ?)"
        self.cursor.execute(query, (username, hash, cash))
        self.connection.commit()
        print(f"Inserted {username} to database")

    def delete(self, id, table):
        if not self.connection:
            print("Not connected to any database.")
            return

        query = f"DELETE FROM {table} WHERE user_id = ?"
        self.cursor.execute(query, (id,))
        self.connection.commit()

        if self.cursor.rowcount == 0:
            print(f"No record with user_id {id} found in {table}")
        else:
            print(f"Deleted record with user_id {id} from {table}")


