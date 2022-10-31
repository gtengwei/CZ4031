import psycopg2

def get_query_result(query,host,database,user,password):
    print("Query:", query)
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
        # host="localhost",
        # database="TCP-H",
        # user="postgres",
        # password="1234")

    cur = conn.cursor()

    cur.execute(query)
    rows = cur.fetchall()
    print(rows)

    cur.close()