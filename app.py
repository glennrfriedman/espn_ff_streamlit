import requests
import streamlit as st
from espn_api.football import League
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# WBTD League Details
# ID 339211
# SWID "{2DFE4612-834F-4F94-8E1A-492F7A4A07BA}"
# S2 "AECQDeW2ouDG9t696CAcSjh49xTD%2BDCWIIn%2BUo%2BV%2BKZ1%2Bw9CLNZpoME5iUP07iJet5wtqDfQnt9WkoWC03%2B4Y4YShn7VKwg8vZKPo%2Fgsq4hOEZcja%2Fc%2Fs5TuZ5uKp3PWmVK4VJRDXdTbmUghmovmp8UXAz191%2BCPESL54MBfU4Obspe1EJ9yQIa507Z%2Byy4VTFF456eKW3gvFnROELXH%2BONDIIkePwMe9oBDUpZCas7lB4rmjOWOJvOOVI%2Fj6B%2BOfJ%2BPI2kmDr332XmSpW5%2BRQGClPlNOJ0eWn2FtWBPkfKCmw%3D%3D"

def main():
	# GET LEAGUE INFORMATION 
	# league_id_input = ""
	# swid_input = ""
	# espn_s2_input = ""
	st.title("ESPN Fantasy Football App")
	menu = ["Enter League Data", "Explore League"]
	choice = st.sidebar.selectbox("Get Started", menu)
	if choice == "Enter League Data":
		if league_id_input == "" or swid_input == "" or espn_s2 == "":
			league_id_input = st.text_input("League ID", "")
			swid_input = st.text_input("SWID", "")
			espn_s2_input = st.text_input("S2", "")
		else: 
		# SET LEAGUE METADATA
			league_id = league_id_input
			year = 2020
			swid = swid_input
			espn_s2 = str(espn_s2_input)

			league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

			teams = league.teams
			week = league.current_week
			week_list = list(range(1,week))

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

			# GET TEAM DATA
			teams = league.teams
			team_list = []
			for i in range(len(league.teams)):
				team_list.append(
						{
						'team_id': teams[i].team_id,
						'team_abbrev': teams[i].team_abbrev,
						'team_name': teams[i].team_name,
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
						'roster': teams[i].roster
						})

			teams_df = pd.DataFrame(team_list)
			teams_df['drop_down'] = teams_df['team_name'] + ' (' + teams_df['owner'] + ')'

			player_list = []
			for i in range(len(team_list)):
				roster = team_list[i]['roster']
				for x in range(len(roster)):
					player_dict = {
								'team': team_list[i]['team_name'],
								'owner': team_list[i]['owner'],
								'name': roster[x].name,
								'playerId': roster[x].playerId,
								'posRank': roster[x].posRank,
								'eligibleSlots': roster[x].eligibleSlots,
								'acquisitionType': roster[x].acquisitionType,
								'proTeam': roster[x].proTeam,
								'position': roster[x].position,
								'injuryStatus': roster[x].injuryStatus,
								'injured': roster[x].injured,
								'stats': roster[x].stats,
								'points_scored': roster[x].total_points,
								'projected_points': roster[x].projected_total_points
					}
					player_list.append(player_dict)

			players_df_full = pd.DataFrame(player_list)

			st.sidebar.title("ESPN Fantasy Football League Dashboard")
			st.sidebar.markdown("A data explorer for your fantasy league.")
			st.sidebar.multiselect("Select Team(s)", players_df_full['team'].unique())
			# st.header("Customary quote")
			# st.markdown("> I just love to go home, no matter where I am [...]")
			player_box_plot_by_position = px.box(players_df_full, x="position", y="points_scored", points="all", color='position', hover_data=['name', 'posRank', 'position','team','owner','acquisitionType'])
			st.plotly_chart(player_box_plot_by_position)

main()
# st.dataframe(box_df)
# st.dataframe(box_player_df)
# st.table(box_player_df)