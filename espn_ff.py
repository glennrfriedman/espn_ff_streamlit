import requests
from espn_api.football import League
import pandas as pd
import pygsheets

league_id = 339211
year = 2020

swid = "{2DFE4612-834F-4F94-8E1A-492F7A4A07BA}"
espn_s2 = str("AECQDeW2ouDG9t696CAcSjh49xTD%2BDCWIIn%2BUo%2BV%2BKZ1%2Bw9CLNZpoME5iUP07iJet5wtqDfQnt9WkoWC03%2B4Y4YShn7VKwg8vZKPo%2Fgsq4hOEZcja%2Fc%2Fs5TuZ5uKp3PWmVK4VJRDXdTbmUghmovmp8UXAz191%2BCPESL54MBfU4Obspe1EJ9yQIa507Z%2Byy4VTFF456eKW3gvFnROELXH%2BONDIIkePwMe9oBDUpZCas7lB4rmjOWOJvOOVI%2Fj6B%2BOfJ%2BPI2kmDr332XmSpW5%2BRQGClPlNOJ0eWn2FtWBPkfKCmw%3D%3D")


league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

teams = league.teams
# print(league.teams)

my_team = teams[6]
# print(my_team)

my_players = my_team.roster
# print(my_players)

# power_ranks = league.power_rankings(week=3)
# print(power_ranks)

# print(league.top_scorer())
# print(league.least_scorer())

# print(league.draft)

# draft_df = pd.DataFrame(columns = ['team', 'playerId','playerName','round_num','round_pick','bid_amount','keeper_status'])

draft_len = len(league.draft)
# print(league.draft[0].team)
# print(draft_len)

draft_list = []
for i in range(draft_len):
	draft_dict = {
					'team': league.draft[i].team,
					'playerId': league.draft[i].playerId,
					'playerName': league.draft[i].playerName,
					'round_num': league.draft[i].round_num,
					'round_pick': league.draft[i].round_pick,
					'bid_amount': league.draft[i].bid_amount,
					'keeper_status': league.draft[i].keeper_status
				}
	draft_list.append(draft_dict)
	# print(league.draft[i].team)
# print(draft_list)

# FULL DRAFT RESULTS TABLS
draft_df = pd.DataFrame(draft_list)  

# posRank = draft_df['playerId'][0].posRank
# print(posRank)

# print(draft_df)

# print(len(league.teams))
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

# print(team_rosters)
teams_df = pd.DataFrame(team_list)
# print(teams_df)

player_list = []
for i in range(len(team_list)):
	roster = team_list[i]['roster']
	for x in range(len(roster)):
		# print(roster[x].name)
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
					'points_scored': roster[x].total_points
		}
		player_list.append(player_dict)
		# print(roster[x].stats)

players_df = pd.DataFrame(player_list)
print(players_df['points_scored'][3])
print(players_df['name'][3])
# print(players_df['stats'][0])


# GOOGLE SHEETS OUTPUT
# https://erikrood.com/Posts/py_gsheets.html
# stack overflow --> THANK YOU! Had to share service account with sheet wbtd-ff-157@wbtd-291020.iam.gserviceaccount.com
# https://stackoverflow.com/questions/52159382/spreadsheet-not-found-using-service-account-file

# Connect to Google Sheets
gc = pygsheets.authorize(service_file='./wbtd_ff.json')
sh = gc.open('2020 Keeper Sheet')

# Output Team Data
# 

# Output Draft Results
# worksheet = sh.worksheet('title','Draft_Results')
# worksheet.set_dataframe(draft_df,(1,1))

# Output Players
worksheet = sh.worksheet('title','Rost_New')
worksheet.set_dataframe(players_df,(1,1))