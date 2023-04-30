#sleeper api: https://docs.sleeper.com/
#league read

import requests
import json
import numpy as np
import pandas as pd
import time

class ffData():

    def __init__(self,league_id):
        #fetchloads
        self.get_league(league_id)
        self.get_users(league_id)
        self.get_rosters(league_id)
        self.get_nfl_state()
        #fetchloads dependant on nfl_state:
        self.get_transactions(league_id)
        self.get_matchups(league_id)


        #buildings
        self.users_table = build_user_table(self.users,self.rosters)



# region _fetch functions


    def get_league(self,league_id):
        self.league = requests.get(f'https://api.sleeper.app/v1/league/{league_id}').json()
        self.season = self.league['season']
        self.playoff_week = self.league['settings']['playoff_week_start']


    def get_nfl_state(self):
        self.nfl = requests.get('https://api.sleeper.app/v1/state/nfl').json()
        if self.season < self.nfl['season']:
            self.current_week = self.playoff_week #set the week to the max reg season week
        else:
            self.current_week = self.nfl['week'] # set the week to the actual week
            
    def get_users(self,league_id):
        self.users = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/users').json()

    def get_rosters(self,league_id):
        self.rosters = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters').json()

    #require current_week

    def get_transactions(self,league_id): #have to build after get_nfl_state, self.current_week
        self.transactions = []
        for i in range(1,self.current_week):
            time.sleep(0.1) #@remove when in prod, api ping buffer
            trans = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/transactions/{i}').json()
            self.transactions.append({'week':i,'transactions':trans})

    def get_matchups(self,league_id):
        self.matchups = []
        for i in range(1,self.current_week):
            time.sleep(0.1) #@remove when in prod, api ping buffer
            mu = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/matchups/{i}').json()
            self.matchups.append({'week':i,'matchups':mu})


# endregion

# region _build functions

def build_user_table(users_json,roster_json):
    user_id = []
    username = []
    for i in users_json:
        user_id.append(i['user_id'])
        username.append(i['display_name'])
    df1 = pd.DataFrame({'user_id':user_id,'username':username})

    user_id = []
    roster_id = []
    for i in roster_json:
        user_id.append(i['owner_id'])
        roster_id.append(i['roster_id'])
    df2 = pd.DataFrame({'user_id':user_id,'roster_id':roster_id})

    dfFinal = df1.join(df2.set_index('user_id'), on = 'user_id')
    return dfFinal

# def fetch_transactions(weeks):
#     for i in range(weeks):
        
def build_transactions_table(transactions_table_json):
    pass #@todo


# endregion

if __name__ == '__main__':
    pass