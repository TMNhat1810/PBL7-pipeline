import psycopg2

connection = psycopg2.connect(database='postgres',
                              user='postgres',
                              password='123456a@A',
                              host='localhost',
                              port='5432',
                              options="-c search_path=pbl7,public")