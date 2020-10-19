import requests
import streamlit as st
from espn_api.football import League
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from annotated_text import annotated_text
import streamlit.components.v1 as components
import SessionState
from BoxData import BoxData
from TeamData import TeamData

# SET LEAGUE YEAR
year = 2020 
# WBTD League Details
# ID 339211
# SWID "{2DFE4612-834F-4F94-8E1A-492F7A4A07BA}"
# S2 "AECQDeW2ouDG9t696CAcSjh49xTD%2BDCWIIn%2BUo%2BV%2BKZ1%2Bw9CLNZpoME5iUP07iJet5wtqDfQnt9WkoWC03%2B4Y4YShn7VKwg8vZKPo%2Fgsq4hOEZcja%2Fc%2Fs5TuZ5uKp3PWmVK4VJRDXdTbmUghmovmp8UXAz191%2BCPESL54MBfU4Obspe1EJ9yQIa507Z%2Byy4VTFF456eKW3gvFnROELXH%2BONDIIkePwMe9oBDUpZCas7lB4rmjOWOJvOOVI%2Fj6B%2BOfJ%2BPI2kmDr332XmSpW5%2BRQGClPlNOJ0eWn2FtWBPkfKCmw%3D%3D"

st.sidebar.header('NAVIGATION')
menu = ["Enter League Credentials", "Explore League"]
choice = st.sidebar.selectbox("Get Started", menu)

session_state = SessionState.get(league_id='', espn_s2='', swid='', login=False)

if choice == "Enter League Credentials" :
	st.header("Enter League Credentials")
	st.write("To get started; please enter your league data following the instructions below.")
	st.write("This app runs entirely using browser storage so the information provided here along with all your league data will not be collected or stored.")
	session_state.league_id = st.text_input("League ID", "")
	session_state.swid = st.text_input("SWID", "")
	session_state.espn_s2 = st.text_input("S2", "")
	if session_state.league_id=='' or session_state.swid=='' or session_state.espn_s2=='' :
			st.write('You need to ener your league info')
			st.subheader("Instructions to get League Credentials")
			st.write("I promise it's not that bad, just head over to your EPSN league in your browser; this will take less than 5 minutes.")
			st.subheader("Step 1: Get League ID")
			st.write("Navigate to your ESPN league in your browser (not the app) and get the following piece of highlighted information.")
			st.image('./assets/league_id.png', width=800)
			st.write("Now copy that into the 'League ID' text input above as is. Just the number.")
			st.subheader("Step 2: Get SWID")
			st.write("In Chrome go to tools menu then 'More Tools' then 'Developer Tools'. Don't worry image below.")
			st.image('./assets/dev_tools.png', width=800)
			st.write("Now with the developer tools open navigate to the Storage --> Cookies section, click on the https://fantasy.espn.com option.")
			st.write("Then search for SWID in the search.")
			st.write("Once you find the SWID copy the entire value INCLUDING the {} and paste into the SWID input above. Screenshot below.")
			st.image('./assets/swid.png', width=800)
			st.subheader("Step 3: Get S2")
			st.write("For step 3 stay right where you are, and replace the SWID search with espn_s2.")
			st.write("Double click and copy the ENTIRE SUPER LONG S2 value.")
			st.write("Copy the S2 value above into the S2 input above...it's really long so please make sure you get the whole thing.")
			st.subheader("When you're all done it should look like the following...")
			st.image('./assets/example_login.png', width=800)
			st.subheader("Not so bad, right? (I hope). Save these values in a text file on your computer somewhere so you can re-use them if you want to come back!")
			st.subheader("Change the Navigation option on the right to Explore League to check out your data.")	
	else :
			# st.text_input("League ID", session_state.league_id)
			# st.text_input("SWID", session_state.swid)
			# st.text_input("S2", session_state.espn_s2)
			st.subheader('DOPE!')
			st.write('Your league data has been entered; check out the Explore League page and start crushing your friends with data.')
else:
	if session_state.league_id=='' or session_state.swid =='' or session_state.espn_s2 =='' :
		st.header('Nothing to see here ... please enter your league credentials to get started.')
		st.image('./assets/butt_fumble.gif', width=800)
	else:
		page = st.sidebar.radio("View", ("Player Performance", "Team Performance", "Fun Facts", "Player Movement", "Buy Lows"))
		def getData():
			data = BoxData(year, int(session_state.league_id), str(session_state.espn_s2), str(session_state.swid))
			return data

		@st.cache
		def getPlayerTeamBoxData():
			data = getData()
			team_box_data = data.getBoxData()
			return team_box_data

		weeks = getPlayerTeamBoxData()[2]
		def returnPlayerBoxPlot():
			player_variances = getPlayerTeamBoxData()[0]
			return player_variances

		@st.cache
		def filterByWeek(week):
			player_variances = returnPlayerBoxPlot()
			if week == 'Year':
				return px.box(player_variances, x="slot_position", y="points", points="all", color='slot_position', hover_data=['week', 'name', 'slot_position', 'team','owner'])
			else:
				filtered_player_var = player_variances[player_variances['week'] == week]
				return px.box(filtered_player_var, x="slot_position", y="points", points="all", color='slot_position', hover_data=['week', 'name', 'slot_position', 'team','owner'])

		@st.cache
		def getLeagueData():
			data = TeamData(year, int(session_state.league_id), str(session_state.espn_s2), str(session_state.swid))
			box_data = data.getBoxData()
			team_data = data.getTeamData()
			return box_data, team_data

		def getPlayerSeasonData():
			data = TeamData(year, int(session_state.league_id), str(session_state.espn_s2), str(session_state.swid))
			player_data = data.getPlayerData()
			return player_data

		if page == "Player Performance":
			st.header("Season Long Player Performance")
			st.write("Let's take a look at total points scored for the player's currently on rosters in your league.")
			player_season_df = getPlayerSeasonData()
			player_season_points_box = px.box(player_season_df, x="position", y="points_scored", points="all", color='position', hover_data=['name', 'posRank', 'position','team','owner','acquisitionType'])
			st.plotly_chart(player_season_points_box)
			st.header("Player Performance by Game")
			st.write("Note: The dataset only contains players that were on a team roster.")		
			options = ['Season', 'Weekly']
			week_or_all = st.selectbox("View Season Long or Week by Week Data", options)
			
			if week_or_all == 'Season':
				filterByYearData = pd.DataFrame(returnPlayerBoxPlot())
				high_scorer = filterByYearData.loc[filterByYearData['points'].idxmax()]
				name = high_scorer['name']
				week = str(high_scorer['week'])
				points_scored = str(high_scorer['points'])
				opponent = high_scorer['pro_opponent']
				team = high_scorer['team']
				st.subheader("The best performance of the year so far was " + name + " in week " + week + " balling out with " + points_scored + " for team " + team + " against " + opponent)
				st.plotly_chart(filterByWeek('Year'))
			else:
				filterByWeekData = pd.DataFrame(returnPlayerBoxPlot())
				week_selection = st.slider('Filter by Week', value=weeks[-1], min_value=weeks[0], max_value=weeks[-1], step=1)
				filteredDataByWeek = filterByWeekData[filterByWeekData['week'] == week_selection]
				high_scorer = filteredDataByWeek.loc[filteredDataByWeek['points'].idxmax()]
				name = high_scorer['name']
				week = str(high_scorer['week'])
				points_scored = str(high_scorer['points'])
				opponent = high_scorer['pro_opponent']
				team = high_scorer['team']
				st.subheader("The best performance of the week was " + name + " balling out with " + points_scored + " for team " + team + " against " + opponent)
				st.plotly_chart(filterByWeek(week_selection))
		elif page == "Team Performance":
			team_season_data = getLeagueData()[1]
			st.header("Team Performance")
			st.write("Let's take a look at how the other iditos (I mean teams) in your league are doing.")
			team_var_df = returnPlayerBoxPlot()
			team_var_df_filtered = team_var_df[team_var_df['slot_position'] != 'BE']
			st.write("Note: Bench player performances not counted here people, the bench does NOT score points!")
			st.write("First; let's see how ESPN is doing overall in your league ... not too shabby Mike Clay, Field Yates, and TMR.")
			week_group_team_var_df = team_var_df_filtered.groupby(by='week', as_index=False).sum().drop(columns=['pro_pos_rank'])
			relabel_week_df = week_group_team_var_df.rename(columns={"week": "Week", "points": "Total Points Scored", "projected_points": "Total Projected Points", "variance": "Variance"}) 
			st.subheader('ESPN Projection Performance')
			st.write(relabel_week_df)
			team_group_var_df = team_var_df_filtered.groupby(by='team', as_index=False).sum().drop(columns=['pro_pos_rank'])
			conditions = [
				(team_group_var_df['variance'] >= 0),
				(team_group_var_df['variance'] <= 0)
			]
			values = ['BOOM', 'BUST']
			team_group_var_df['BOOM_BUST'] = np.select(conditions, values)
			team_group_var_df_join = pd.merge(team_group_var_df, team_season_data, on='team', how='inner')
			team_group_var_df_join['Team (Record)'] = team_group_var_df_join['team'] + ' (' + team_group_var_df_join['record'] + ')'
			team_variances_fig = px.bar(team_group_var_df_join,
		           x='variance',
		           y='Team (Record)',
		           color='BOOM_BUST',
		           orientation='h',  hover_data=['team', 'record', 'points_for', 'points_against'], width=800)
			st.subheader("Projected vs. Actual Points Variance by Team")
			st.write("Check out which teams are over and underperforming the ESPN projections.")
			st.plotly_chart(team_variances_fig)
			team_var_df_bar = pd.merge(team_var_df_filtered, team_season_data, on='team', how='inner')
			team_var_df_bar['Team (Record)'] = team_var_df_bar['team'] + ' (' + team_var_df_bar['record'] + ')'
			season_points_bar = px.bar(team_var_df_bar, x="points", y="Team (Record)", color='slot_position', orientation='h',
		            hover_data=["name", "week"],
		            height=400, width=800)
			season_points_bar.update_layout(yaxis={'categoryorder':'total ascending'})
			st.subheader("Breakdown of total points scored by team and position")
			st.write("See how every performance from every week adds up, hover over the graph for more detail.")
			st.plotly_chart(season_points_bar)
		elif page == "Fun Facts":
			st.header("Fun Facts")
			st.write("A few fun, or not fun, data points for your league. Depends on who's looking I guess.")
			st.subheader("Top 10 Bench Performances of the Year")
			team_var_df = returnPlayerBoxPlot()
			team_var_df_be = team_var_df[team_var_df['slot_position'] == 'BE'].sort_values(by=['points'], ascending=False).drop(columns=['owner', 'slot_position'])
			team_var_df_be = team_var_df_be[['week', 'name', 'points', 'team']]
			team_var_df_be = team_var_df_be.assign(hack='').set_index('hack')
			st.write(team_var_df_be.head(10))
			be_team_group = team_var_df_be.head(10).groupby(by='team').count()
			dumb_team = be_team_group.sort_values(by='name', ascending=False).head(1).index[0]
			num_dumb = be_team_group.sort_values(by='name', ascending=False).head(1)['name'][0]
			st.write("No one in your league is surprised to see " + dumb_team + " appear on this list " + str(num_dumb) + " times.")
			st.subheader("Smackdown of the Year")
			match_data = getLeagueData()[0]
			blowout_match_data = match_data.sort_values(by='variance', ascending=False).head(1)
			annotated_text(
		   "The biggest beat down of the season happened when ",
		   (blowout_match_data['home_team'], blowout_match_data['home_score'], "#afa"),
		   " squared off with ",
		   (blowout_match_data['away_team'], blowout_match_data['away_score'], "#fea"),
		    " in ",
		    ("Week", blowout_match_data['week'], "#8ef"), 
		    " that ended up being a ",
		    (blowout_match_data['variance'], "point", "#faa"),
		    " beat down!"
		    )
			st.subheader("Nail biter of the Year")
			close_match_data = match_data.sort_values(by='variance', ascending=True).head(1)
			annotated_text(
		   "The closest game of the season happened when ",
		   (close_match_data['home_team'], close_match_data['home_score'], "#afa"),
		   " squared off with ",
		   (close_match_data['away_team'], close_match_data['away_score'], "#fea"),
		    " in ",
		    ("Week", close_match_data['week'], "#8ef"), 
		    " that ended up being a ",
		    (close_match_data['variance'], "point", "#faa"),
		    " down to the wire showdown!"
		    )
			# COME BACK HERE AND: 
			# SHOW TOTAL TRADED PLAYERS
			# SHOW TOTAL PLAYERS PICKED UP
		elif page == "Player Movement":
			st.header("Player Movement")
			player_data = getPlayerSeasonData()
			player_data["All"] = "All"
			st.subheader('Breakdown of Rosters by Acquisition Type')
			st.write('The below shows how players currently on teams came to be there.')
			acq_path = player_data['acquisitionType'].unique()
			player_acquisition_fig = px.treemap(player_data, path=["All", "acquisitionType", 'position'], values='points_scored', color='acquisitionType')
			st.subheader("Treemap of Player acquisition by position")
			st.plotly_chart(player_acquisition_fig)
			st.subheader("By the Numbers")
			table_sum_data = player_data.groupby(['acquisitionType']).agg({'points_scored': 'sum', 'name': 'count'})
			table_sum_data = table_sum_data.rename(columns={"points_scored": "Total Points", "name": "Count of Players"})
			st.table(table_sum_data)
			acquisition_menu = ["ADD", "DRAFT", "TRADE"]
			acq_choice = st.selectbox("Filter by Acquisition Type", acquisition_menu)
			player_data_table = player_data.drop(columns=['owner', 'playerId', 'eligibleSlots', 'proTeam', 'injured', 'All'])
			def filterByPos(acq_table, pos_choice):
				if pos_choice == 'All':
					return acq_table
				else:
					filtered_acq_table = acq_table[acq_table['position'] == pos_choice]
					return filtered_acq_table
			if acq_choice == "ADD":
				acq_table = player_data_table[player_data_table['acquisitionType'] == "ADD"]
				pos_menu = acq_table['position'].unique().tolist()
				pos_menu.insert(0, "All")
				pos_choice = st.selectbox("Filter by Position", pos_menu)
				acq_table = acq_table[['name', 'position', 'points_scored', 'posRank', 'team']]
				acq_table = filterByPos(acq_table, pos_choice).sort_values(by=['points_scored'], ascending=False)
				st.write(acq_table)
			elif acq_choice == "DRAFT":
				acq_table = player_data_table[player_data_table['acquisitionType'] == "DRAFT"]
				pos_menu = acq_table['position'].unique().tolist()
				pos_menu.insert(0, "All")
				pos_choice = st.selectbox("Filter by Position", pos_menu)
				acq_table = acq_table[['name', 'position', 'points_scored', 'posRank', 'team']]
				acq_table = filterByPos(acq_table, pos_choice).sort_values(by=['points_scored'], ascending=False)
				st.write(acq_table)
			else: 
				acq_table = player_data_table[player_data_table['acquisitionType'] == "TRADE"]
				pos_menu = acq_table['position'].unique().tolist()
				pos_menu.insert(0, "All")
				pos_choice = st.selectbox("Filter by Position", pos_menu)
				acq_table = acq_table[['name', 'position', 'points_scored', 'posRank', 'team']]
				acq_table = filterByPos(acq_table, pos_choice).sort_values(by=['points_scored'], ascending=False)
				st.write(acq_table)
		else: 
			st.write("TBD")



