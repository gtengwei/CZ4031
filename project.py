from interface import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='postgresql connection host')
    parser.add_argument('--database', help='the tpch database to connect')
    parser.add_argument('--user', help='db user')
    parser.add_argument('--password', help='db password')
    args = parser.parse_args()
    host = args.host
    database = args.database
    user = args.user
    password = args.password
    interface(host,database,user,password)