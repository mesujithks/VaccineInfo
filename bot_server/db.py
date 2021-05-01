import sqlite3


class DBHelper:

    def __init__(self, dbname="vaccine_info.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS users (chat_id integer NOT NULL PRIMARY KEY, user_name text, user_state text, user_city text, user_pincode integer, user_location text)"
        self.conn.execute(tblstmt)
        self.conn.commit()

    def add_user(self, chat_id, user_name):
        stmt = "INSERT INTO users (chat_id, user_name) VALUES (?, ?)"
        args = (chat_id, user_name)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, chat_id):
        stmt = "DELETE FROM users WHERE chat_id = (?)"
        args = (chat_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_all_chat_id(self):
        stmt = "SELECT chat_id FROM users"
        return [x[0] for x in self.conn.execute(stmt)]

    def check_user_by_chat_id(self, chat_id):
        stmt = "SELECT count(*) FROM users WHERE chat_id = (?)"
        args = (chat_id,)
        result = self.conn.execute(stmt, args).fetchall()
        return result[0][0]