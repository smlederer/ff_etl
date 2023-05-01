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
        self.users_table = build_user_table(self.users,
                                            self.rosters,
                                            self._season,
                                            league_id)
        
        self.results_and_leg_roster_table, self.matchup_table = build_legacy_rosters_and_matchup_table(self.matchups,
                                                                                                       self.users_table,
                                                                                                       self._season,
                                                                                                       league_id)


# region _fetch functions


    def get_league(self,league_id):
        self.league = requests.get(f'https://api.sleeper.app/v1/league/{league_id}').json()
        self._season = self.league['season']
        self._playoff_week = self.league['settings']['playoff_week_start']


    def get_nfl_state(self):
        self.nfl = requests.get('https://api.sleeper.app/v1/state/nfl').json()
        if self._season < self.nfl['season']:
            self._current_week = self._playoff_week #set the week to the max reg season week
        else:
            self._current_week = self.nfl['week'] # set the week to the actual week
            
    def get_users(self,league_id):
        self.users = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/users').json()

    def get_rosters(self,league_id):
        self.rosters = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters').json()

    # require _current_week -- have to build after 
    # get_nfl_state, self._current_week

    def get_transactions(self,league_id): 
        self.transactions = []
        for i in range(1,self._current_week):
            time.sleep(0.1) #@remove when in prod, api ping buffer
            trans = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/transactions/{i}').json()
            self.transactions.append({'week':i,'transactions':trans})

    def get_matchups(self,league_id):
        self.matchups = []
        for i in range(1,self._current_week):
            #time.sleep(0.1) #@remove when in prod, api ping buffer
            mu = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/matchups/{i}').json()
            self.matchups.append({'week':i,'matchups':mu})


# endregion

# region _build functions

def build_user_table(users_json,roster_json,season,league_id):
    user_id = []
    username = []
    for i in users_json:
        user_id.append(i['user_id'])
        username.append(i['display_name'])
    df1 = pd.DataFrame({'league_id':league_id,'season':season,'user_id':user_id,'username':username})

    user_id = []
    roster_id = []
    for i in roster_json:
        user_id.append(i['owner_id'])
        roster_id.append(i['roster_id'])
    df2 = pd.DataFrame({'user_id':user_id,'roster_id':roster_id})

    users_table = df1.join(df2.set_index('user_id'), on = 'user_id')
    return users_table


def build_legacy_rosters_and_matchup_table(matchups_json,users_table,season,league_id):

    #build the rosters table w/ matchup
    r_m_table = pd.DataFrame()
    for i in range(1,len(matchups_json)+1):
        r_n_m_tbl_temp = pd.DataFrame(matchups_json[i-1]['matchups']).drop(['starters_points','players_points'],axis = 1).explode(['players'])
        r_n_m_tbl_temp['is_starter'] = r_n_m_tbl_temp['players'].apply(lambda x: any([x in k for k in list(r_n_m_tbl_temp['starters'])]))
        r_n_m_tbl_temp = r_n_m_tbl_temp.drop('starters',axis = 1)
        r_n_m_tbl_temp = r_n_m_tbl_temp.merge(users_table,on='roster_id')
        r_n_m_tbl_temp['week'] = i


        r_m_table = pd.concat([r_m_table,r_n_m_tbl_temp])
    r_n_m_tbl_temp['season'] = season
    r_n_m_tbl_temp['league_id'] = league_id

    mu_temp = r_m_table[['league_id','season','roster_id','user_id','username','matchup_id','week']]
    mu_temp = mu_temp.drop_duplicates()
    mu_temp2 = mu_temp.merge(mu_temp[['user_id','username','matchup_id','week','roster_id']], on=['matchup_id','week'],suffixes=['_root','_challenger']).query('username_root != username_challenger')
    matchup_table = mu_temp2[['league_id','season','week','matchup_id','roster_id_root','user_id_root','username_root','roster_id_challenger','user_id_challenger','username_challenger']]



    return r_m_table, matchup_table

# endregion

# Player data doesn't neet to be rebuild every time so saved as a seperate class. 
# Might consolidate to a singleton function


class PlayerData():
    
    def __init__(self):
        self.get_and_build_players()
    

    def get_and_build_players(self):
        self.player_raw = requests.get('https://api.sleeper.app/v1/players/nfl').json()
        players = pd.DataFrame(self.player_raw).transpose()
        players = players.reset_index().drop('index',axis = 1)
        players = players.infer_objects()

        for n,i in enumerate(players.dtypes):
            if i == 'object':
                players[str(players.columns[n])] = players[str(players.columns[n])].astype(str)

        self.players_table = players



if __name__ == '__main__':
    pass