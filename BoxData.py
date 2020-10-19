import requests
from espn_api.football import League
import pandas as pd
import numpy as np

class BoxData(object):
	def __init__(self, year, league_id, espn_s2, swid):
		self.league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
		self.teams = self.league.teams
		self.week = self.league.current_week
		self.week_list = list(range(1,self.week))
		self.box_score_list = []
		self.box_score_objs = []
		self.box_scores_player_list = []

	def getBoxData(self):
		for x in self.week_list:
			box_scores = self.league.box_scores(x)
			self.box_score_objs.append(box_scores)
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
				self.box_score_list.append(game)
		box_df = pd.DataFrame(self.box_score_list)

		for z in range(len(self.box_score_objs)):
			box_scores = self.box_score_objs[z]
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
					self.box_scores_player_list.append(home_player)

		for z in range(len(self.box_score_objs)):
			box_scores = self.box_score_objs[z]
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
					self.box_scores_player_list.append(away_player)
		
		box_player_df = pd.DataFrame(self.box_scores_player_list)
		conditions = [
			(box_player_df['projected_points'] > box_player_df['points']),
			(box_player_df['points'] > box_player_df['projected_points'])
		]
		values = ['BUST', 'BOOM']
		box_player_df['BOOM_BUST'] = np.select(conditions, values)
		box_player_df['variance'] = box_player_df['points'] - box_player_df['projected_points']
		data = [box_player_df, box_df, self.week_list]
		return data
