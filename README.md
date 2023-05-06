# Fantasy Football League Data ETL

Testing ETL process to take data from [Sleeper Fantasy Football API](https://docs.sleeper.com/) and import it into [Planetscale](https://planetscale.com) MYSQL Data Warehouse.

### Files:

```
tools/
---> sleeper_read.py :: package to interface with Sleeper API
---> sql_cxn.py :: package that wrappes SQL Alchemy to grab secrets from a .env file

sleeper_read_playground.ipynb :: instance the sleeper_read data build and test with
upload_sleeper_league.py :: cmd line uploader using sleeper_ids
```

