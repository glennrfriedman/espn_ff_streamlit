import requests
from espn_api.football import League
import pandas as pd
import numpy as np

class TeamData(object):
	def __init__(self, year, league_id, espn_s2, swid):
		self.league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
		self.week = self.league.current_week
		self.week_list = list(range(1,self.week))
		self.box_score_list = []
		self.box_score_objs = []
		self.team_list = []
		self.player_list = []

	def getBoxData(self):
		for x in self.week_list:
			box_scores = self.league.box_scores(x)
			self.box_score_objs.append(box_scores)
			for i in range(len(box_scores)):
				variance = box_scores[i].home_score - box_scores[i].away_score
				game = { 
					'week': x,
					'home_team': box_scores[i].home_team.team_name,
					'home_owner': box_scores[i].home_team.owner,
					'home_score': box_scores[i].home_score,
					'away_team': box_scores[i].away_team.team_name,
					'away_owner': box_scores[i].away_team.owner,
					'away_score': box_scores[i].away_score,
					'variance': abs(variance)
				}
				self.box_score_list.append(game)
		box_df = pd.DataFrame(self.box_score_list)
		return box_df

	def getTeamData(self):
		teams = self.league.teams
		for i in range(len(self.league.teams)):
			record = str(teams[i].wins) + " - " + str(teams[i].losses)
			self.team_list.append(
					{
					'team_id': teams[i].team_id,
					'team_abbrev': teams[i].team_abbrev,
					'team': teams[i].team_name,
					'division_id': teams[i].division_id,
					'division_name': teams[i].division_name,
					'wins': teams[i].wins,
					'losses': teams[i].losses,
					'points_for': teams[i].points_for,
					'points_against': teams[i].points_against,
					'owner': teams[i].owner,
					'streak_type': teams[i].streak_type,
					'streak_length': teams[i].streak_length,
					'standing': teams[i].standing,
					'roster': teams[i].roster,
					'record': record
					})
		teams_df = pd.DataFrame(self.team_list)
		return teams_df

	def getPlayerData(self):
		self.getTeamData()
		for i in range(len(self.team_list)):
			roster = self.team_list[i]['roster']
			for x in range(len(roster)):
				player_dict = {
							'team': self.team_list[i]['team'],
							'owner': self.team_list[i]['owner'],
							'name': roster[x].name,
							'playerId': roster[x].playerId,
							'posRank': roster[x].posRank,
							'eligibleSlots': roster[x].eligibleSlots,
							'acquisitionType': roster[x].acquisitionType,
							'proTeam': roster[x].proTeam,
							'position': roster[x].position,
							'injuryStatus': roster[x].injuryStatus,
							'injured': roster[x].injured,
							'points_scored': roster[x].total_points,
							'projected_points': roster[x].projected_total_points
				}
				self.player_list.append(player_dict)
		players_df = pd.DataFrame(self.player_list)
		players_df.drop_duplicates(subset=['name'])
		return players_df

