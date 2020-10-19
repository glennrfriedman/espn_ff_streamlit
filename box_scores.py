import requests
from espn_api.football import League
import pandas as pd
import numpy as np
# import pygsheets

league_id = 339211
year = 2020

swid = "{2DFE4612-834F-4F94-8E1A-492F7A4A07BA}"
espn_s2 = str("AECQDeW2ouDG9t696CAcSjh49xTD%2BDCWIIn%2BUo%2BV%2BKZ1%2Bw9CLNZpoME5iUP07iJet5wtqDfQnt9WkoWC03%2B4Y4YShn7VKwg8vZKPo%2Fgsq4hOEZcja%2Fc%2Fs5TuZ5uKp3PWmVK4VJRDXdTbmUghmovmp8UXAz191%2BCPESL54MBfU4Obspe1EJ9yQIa507Z%2Byy4VTFF456eKW3gvFnROELXH%2BONDIIkePwMe9oBDUpZCas7lB4rmjOWOJvOOVI%2Fj6B%2BOfJ%2BPI2kmDr332XmSpW5%2BRQGClPlNOJ0eWn2FtWBPkfKCmw%3D%3D")

league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

teams = league.teams
# print(league.current_week)
week = league.current_week
week_list = list(range(1,week))
# print(week_list)

box_score_list = []
box_score_objs = []
for x in week_list:
	box_scores = league.box_scores(x)
	box_score_objs.append(box_scores)
	for i in range(len(box_scores)):
		game = { 
			'week': x,
			'home_team': box_scores[i].home_team.team_name,
			'home_owner': box_scores[i].home_team.owner,
			'home_score': box_scores[i].home_score,
			'away_team': box_scores[i].away_team.team_name,
			'away_owner': box_scores[i].away_team.owner,
			'away_score': box_scores[i].away_score
		}
		box_score_list.append(game)

box_df = pd.DataFrame(box_score_list)
# print(len(box_score_list))

box_scores_player_list = []
for z in range(len(box_score_objs)):
	box_scores = box_score_objs[z]
	for y in range(len(box_scores)):
		home_players = box_scores[y].home_lineup
		for x in range(len(home_players)):
			home_player = {
				'week': z+1,
				'team': box_scores[y].home_team.team_name,
				'owner': box_scores[y].home_team.owner,
				'points': home_players[x].points,
				'name': home_players[x].name,
				'projected_points': home_players[x].projected_points,
				'slot_position': home_players[x].slot_position,
				'pro_opponent': home_players[x].pro_opponent,
				'pro_pos_rank': home_players[x].pro_pos_rank
			}
			box_scores_player_list.append(home_player)

for z in range(len(box_score_objs)):
	box_scores = box_score_objs[z]
	for y in range(len(box_scores)):
		away_players = box_scores[y].away_lineup
		for x in range(len(away_players)):
			away_player = {
				'week': z+1,
				'team': box_scores[y].away_team.team_name,
				'owner': box_scores[y].away_team.owner,
				'points': away_players[x].points,
				'name': away_players[x].name,
				'projected_points': away_players[x].projected_points,
				'slot_position': away_players[x].slot_position,
				'pro_opponent': away_players[x].pro_opponent,
				'pro_pos_rank': away_players[x].pro_pos_rank
			}
			box_scores_player_list.append(away_player)


box_player_df = pd.DataFrame(box_scores_player_list)

conditions = [
	(box_player_df['projected_points'] > box_player_df['points']),
	(box_player_df['points'] > box_player_df['projected_points'])
]

values = ['BUST', 'BOOM']

box_player_df['BOOM_BUST'] = np.select(conditions, values)

box_player_df['variance'] = box_player_df['points'] - box_player_df['projected_points']

print(box_player_df.head())

# gc = pygsheets.authorize(service_file='./wbtd_ff.json')
# sh = gc.open('2020 Keeper Sheet')

# worksheet = sh.worksheet('title','Player_Points')
# worksheet.set_dataframe(box_player_df,(1,1))

# worksheet = sh.worksheet('title','Detailed_Standings')
# worksheet.set_dataframe(box_df,(1,1))