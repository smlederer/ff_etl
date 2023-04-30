# sql alchemy connection test
# https://planetscale.com/blog/using-mysql-with-sql-alchemy-hands-on-examples

from sqlalchemy import create_engine, text
from dotenv import dotenv_values


class sql_cnx():
# using mysql-connector-python as driver
# start alchemy wrapper engine and connect
    def __init__(self,env_path):
        self.config = dotenv_values(env_path)
        self.connection_string = f'''mysql+mysqlconnector://{self.config['user']}:{self.config['password']}@{self.config['host']}:3306/{self.config['database']}'''
        self.engine = create_engine(self.connection_string)
        self.cnx = self.engine.connect() # connect
        
#end the connection and cleanup
    def cleanup(self):
        self.cnx.close()
        self.engine.dispose()

    def drop_table(self,name):
        self.cnx.execute(text(f'DROP TABLE {name}'))
        print(f'{name} Table Successfully Dropped')
        


if __name__ == '__main__':
    pass


#example of writing and reading using pandas:

#import pandas as pd

#WRITING FROM DF
# instance = sql_cnx()
#
# data = pd.DataFrame({'test':[1,2,3,4,5],'i':[6,7,8,9,11]})
# data.to_sql(name = 'pandas_test_table',con=instance.cnx, if_exists='replace')
#
# instance.cleanup()

#READING FROM DF:
# instance = sql_cnx()
#
# result = pd.read_sql('select * from pandas_test_table',con = instance.cnx)
# print(result)
#
# instance.cleanup()


