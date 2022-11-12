import psycopg2
import json

class Database:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        self.cur = self.connection.cursor()
    
    

    def get_query_result(self, query):
        try:
            self.cur.execute(query)
            rows = self.cur.fetchall()

            return rows[0][0][0]
        except Exception as e:
            print(e)
            return None

    def execute_query(self, query):
        print("Query:", query)

        self.cur.execute(query)
        self.connection.commit()
        print("Query executed successfully")

def get_json(json_file):
        """ read json content """
        with open("config.json", 'r') as f:
            config = json.loads(f.read())
            print(config)
            return config