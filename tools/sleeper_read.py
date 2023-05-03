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
        
        self.results_table = build_results_table(self.matchups,
                                                    self.users_table,
                                                    self._season)

        self.matchup_table = build_matchup_table(self.results_table)
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

def build_results_table(matchups_json,users_table,season):
    results_table = pd.DataFrame()
    for j in range(0,len(matchups_json)):
    
        matchups_raw = matchups_json[j]['matchups']
        week_results_table = pd.DataFrame()

        for i in range(0,len(matchups_raw)):
            temp_mu = matchups_raw[i]

            rnm_tbl_temp = pd.DataFrame({'player_id':list(temp_mu['players_points'].keys()),'points':list(temp_mu['players_points'].values())})
            rnm_tbl_temp['roster_id'] = temp_mu['roster_id']
            rnm_tbl_temp['matchup_id'] = temp_mu['matchup_id']
            rnm_tbl_temp['week'] = j+1
            rnm_tbl_temp['starters'] = str(temp_mu['starters'])
            rnm_tbl_temp['is_starter'] = rnm_tbl_temp['player_id'].apply(lambda x: any([x in k for k in list(rnm_tbl_temp['starters'])]))
            rnm_tbl_temp = rnm_tbl_temp.drop('starters',axis =1 )

            rnm_tbl_temp = rnm_tbl_temp.merge(users_table, on='roster_id')
            
            week_results_table = pd.concat([week_results_table,rnm_tbl_temp[['league_id','week','user_id','username','roster_id','matchup_id','player_id','points','is_starter']]])
        results_table = pd.concat([results_table,week_results_table])
        

    results_table['season'] = season

    return results_table

def build_matchup_table(results_table):
    tmp_mu = results_table[results_table['is_starter']==True][['season','league_id','week','user_id','username','roster_id','matchup_id','points']].groupby(['season','league_id','week','user_id','username','roster_id','matchup_id']).sum('points').reset_index()
    tmp_mu = tmp_mu.merge(tmp_mu,on=['week','matchup_id','league_id','season'],suffixes=['_root','_challenger']).query('username_root != username_challenger').drop_duplicates()
    matchup_table = tmp_mu[['league_id','season','week','matchup_id','roster_id_root','user_id_root','username_root','points_root','roster_id_challenger','user_id_challenger','username_challenger','points_challenger']]

    return matchup_table

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