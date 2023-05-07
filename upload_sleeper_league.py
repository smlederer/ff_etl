import sys
from tools.sql_cnx  import sql_cnx
import tools.sleeper_read as sr

#upload to planetscale
id = sys.argv[1]
print(f'running {id}...')

data = sr.ffData(id)

instance = sql_cnx('init/.env')
conn = instance.cnx

# upload users
data.users_table.to_sql(name='users',con=conn, if_exists='append')

# upload matchups
data.matchup_table.to_sql(name='matchup',con=conn, if_exists='append')

# upload results
data.results_table.to_sql(name='results',con=conn, if_exists='append')

# upload trades
data.trade_table.to_sql(name='trades_transactions',con=conn, if_exists='append')

# upload free_agents
data.free_agent_table.to_sql(name='free_agent_transactions',con=conn, if_exists='append')

instance.cleanup()

print(f'{id} uploaded successfully!')