import psycopg2
import json

# Database Class to connect to the database
class Database:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        self.cur = self.connection.cursor()
    
    
    # Function to return the json format query plan
    def get_query_result(self, query):
        try:
            self.cur.execute(query)
            rows = self.cur.fetchall()

            return rows[0][0][0]
        except Exception as e:
            print(e)
            return None

    # Function to configure the planner method configurations
    def execute_query(self, query):
        self.cur.execute(query)
        self.connection.commit()

# Function to load the credentials of PostgreSQL server from the json file
def get_json():
        """ read json content """
        with open("config.json", 'r') as f:
            config = json.loads(f.read())
            return config