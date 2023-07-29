import pandas as pd
from tools.sql_cnx import sql_cnx

instance = sql_cnx(env_path='init/.env')
conn = instance.cnx

# data = pd.DataFrame({'test':[1,2,3,4,5],'i':[6,7,8,9,20]})
# data.to_sql('pandas_test_table',con=conn ,if_exists='replace')

# print(pd.read_sql('select * from pandas_test_table limit 100',con=conn))

instance.cleanup()