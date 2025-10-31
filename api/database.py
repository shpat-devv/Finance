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

    def find_user(self, value, column):
        if not self.connection:
            print("Not connected to any database.")
            return
        
        query = f"SELECT * FROM users WHERE {column} = ?"
        res = self.cursor.execute(query, (value,))
        return res.fetchone()

    def insert_user(self, username, hash, cash): 
        if not self.connection:
            print("Not connected to any database.")
            return
        query = "INSERT INTO users (username, hash, cash) VALUES (?, ?, ?)"
        self.cursor.execute(query, (username, hash, cash))
        self.connection.commit()
        print(f"Inserted {username} to database")

    def insert_stock(self, name, price, symbol, shares, user_id): #i could've made a function that can insert into both the users and the stocks table but eh, maybe later
        if not self.connection:
            print("Not connected to any database")
            return
        query = "INSERT INTO stocks (name, price, symbol, shares, user_id) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(query, (name, price, symbol, shares, user_id)) 
        self.connection.commit()
        print(f"Inserted {name} into database")

    def insert_transaction(self, stock_id):
        if not self.connection:
            print("Not connected to any database")
            return
        query = "INSERT INTO transactions (stock_id) VALUES (?)"
        self.cursor.execute(query, (stock_id,))
        self.connection.commit()

    def get_stocks(self, user_id, columns):
        if not self.connection:
            print("Not connected to any database")
            return

        query = f"SELECT {columns} FROM stocks WHERE user_id = ?"
        res = self.cursor.execute(query, (user_id,))
        return res.fetchall() 

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

    def update_table(self, id, table, columns, new_value):
        if not self.connection:
            print("Not connected to any database.")
            return
        query = f"UPDATE {table} SET {columns} = ? WHERE id = ?"
        self.cursor.execute(query, (new_value, id))
        self.connection.commit()

    def get_last(self, table, columns): #mostly written cause i needed something to get the last added stock_id 
        if not self.connection:
            print("Not connected to any database.")
            return
        query = f"SELECT {columns} FROM {table} ORDER BY ID DESC LIMIT 1" 
        res = self.cursor.execute(query)
        return res.fetchone()
        


