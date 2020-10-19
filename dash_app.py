# RESOURCES: 
# https://medium.com/@kumar.niteen/how-to-build-and-deploy-an-enterprise-grade-dashboard-using-dash-and-plotly-34275d35d3f2
# https://towardsdatascience.com/build-a-web-data-dashboard-in-just-minutes-with-python-d722076aee2b
# https://dash.plotly.com/layout
# https://plotly.com/dash-community-components/ <--- dash-ui installed in venv and sd-material-ui
# https://plotly.com/python/bar-charts/#bar-chart-with-sorted-or-ordered-categories
# CALLBACKS --> https://dash.plotly.com/basic-callbacks
# FIXED CALLBACK ISSUE WITH DATA TABLE --> https://stackoverflow.com/questions/61987062/update-values-in-a-dash-datatable-column-based-on-user-input
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd
import requests
from espn_api.football import League
from espn_api.football import Player
from espn_api.football import BoxPlayer
import pygsheets
import json
import datetime

# GRABBING ESPN DATA 
league_id = 339211
year = 2020
week = 3
swid = "{2DFE4612-834F-4F94-8E1A-492F7A4A07BA}"
espn_s2 = str("AECQDeW2ouDG9t696CAcSjh49xTD%2BDCWIIn%2BUo%2BV%2BKZ1%2Bw9CLNZpoME5iUP07iJet5wtqDfQnt9WkoWC03%2B4Y4YShn7VKwg8vZKPo%2Fgsq4hOEZcja%2Fc%2Fs5TuZ5uKp3PWmVK4VJRDXdTbmUghmovmp8UXAz191%2BCPESL54MBfU4Obspe1EJ9yQIa507Z%2Byy4VTFF456eKW3gvFnROELXH%2BONDIIkePwMe9oBDUpZCas7lB4rmjOWOJvOOVI%2Fj6B%2BOfJ%2BPI2kmDr332XmSpW5%2BRQGClPlNOJ0eWn2FtWBPkfKCmw%3D%3D")

# SET UP LEAGUE
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

# GET DRAFT DATA
draft_len = len(league.draft)

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
	
# FULL DRAFT RESULTS TABLE
draft_df = pd.DataFrame(draft_list)  

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
# slice teams_df for just table data 
team_table_df = teams_df[['owner', 'team_name', 'division_name', 'wins', 'losses', 'points_for', 'points_against', 'standing']]
team_table_df.round(1)


# GET PLAYER DATA
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
players_df = players_df_full.drop(['playerId', 'eligibleSlots', 'injured', 'stats'], axis=1)

# SET DRAFT + PLAYERS DF
players_df_full['playerId'].astype(str)
draft_df['playerId'].astype(str)
draft_players_df = pd.merge(players_df_full,  
                     draft_df,  
                     on ='playerId',  
                     how ='left') 
draft_players_df = draft_players_df.dropna()


# GET ACTIVITY DATA
# recent = 100
# activity = league.recent_activity(recent)
# activity_list =[]
# for i in range(len(activity)):
# 	mills = activity[i].date
# 	trans_date = datetime.datetime.fromtimestamp(mills / 1000)
# 	player_class = activity[i].actions[0][2]
# 	team_class = activity[i].actions[0][0]
# 	action = activity[i].actions[0][1]
# 	activity_dict = {
# 			'trans_date': trans_date,
# 			'team': team_class.team_name,
# 			'playerName': player_class.name,
# 			'proTeam': player_class.proTeam,
# 			'poisition': player_class.position,
# 			'action': action,
# 			'points_scored': player_class.total_points,
# 			'pos_rank': player_class.posRank
# 	}
# 	activity_list.append(activity_dict)
# activity_df = pd.DataFrame(activity_list)
# print(activity_df)

# SETTING UP APPLICATION WITH CSS 
# DIFFERENT BOOTSTRAP OPTIONS: https://www.bootstrapcdn.com/bootswatch/
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css"
app = dash.Dash('FF_DASH', external_stylesheets=[BS], suppress_callback_exceptions=True)

# SET UP BAR CHART - POINTS BY TEAM
team_points_fig = px.bar(teams_df, x="owner", y="points_for", color="division_name", barmode="group")
team_points_fig.update_layout(xaxis={'categoryorder':'total ascending'})

# SET UP PIE CHART - POINTS BY POSITION BY TEAM
pie_title = 'Showing Points data by Position for All Teams'
team_players_fig = px.pie(players_df, values='points_scored', names='position', title=pie_title)

# SET UP PLAYER BY TEAM SCATTER
player_scatter_by_team = px.scatter(players_df_full, x="projected_points", y="points_scored", color="team", hover_data=['name', 'posRank', 'position'])

# SET UP DRAFT SCATTER
draft_scatter = px.scatter(draft_players_df, x="bid_amount", y="points_scored", color="keeper_status", hover_data=['name', 'posRank', 'position'])

# SET UP PLAYER BY POSITION BOX PLOT
player_box_plot_by_position = px.box(players_df_full, x="position", y="points_scored", points="all", color='position', hover_data=['name', 'posRank', 'position','team','owner','acquisitionType'])

# SET UP CARD TEXT
top_dawg = str(league.top_scored_week()[0]) + ' : ' + str(league.top_scored_week()[1])
bottom_feeder = str(league.least_scored_week()[0]) + ' : ' + str(league.least_scored_week()[1])

def team_players_table(player_data):
 		return dbc.Row(dbc.Col(dash_table.DataTable(
				    	id='team_player_table',
				    	columns=[{"name": i, "id": i} for i in player_data.columns],
				    	data=player_data.to_dict('records'),
				    	filter_action="native",
				        sort_action="native",
				        sort_mode="multi"
				        # export_format='xlsx'
				    	), width={"size": 10, "offset": 1}))

# def recent_activity(player_data):
#  		return dbc.Row(dbc.Col(dash_table.DataTable(
# 				    	id='recent_activity_table',
# 				    	columns=[{"name": i, "id": i} for i in activity_df.columns],
# 				    	data=activity_df.to_dict('records'),
# 				    	filter_action="native",
# 				        sort_action="native",
# 				        sort_mode="multi"
# 				        # export_format='xlsx'
# 				    	), width={"size": 10, "offset": 1}))

# TABS
league_tab_content = html.Div(children=[

			dbc.Row([
				dbc.Col(dbc.Card(
					dbc.CardBody(
						[
							html.H4("TOP DAWG OF THE WEEK", className='card-title'),
							html.P(top_dawg, className="card-text")

						]
					))),

				dbc.Col(dbc.Card(
					dbc.CardBody(
						[
							html.H4("BOTTOM FEEDER OF THE WEEK", className='card-title'),
							html.P(bottom_feeder, className="card-text")

						]
				)))]),

			dbc.Row([
				dbc.Col(
					dbc.Card([
						dbc.CardHeader("The Boring Exportable Standings"),
							dbc.CardBody(
								[
									# html.H4("League Standings", className='card-title'),
									dash_table.DataTable(
							    	id='team_table',
							    	columns=[{"name": i, "id": i} for i in team_table_df.columns],
							    	data=team_table_df.to_dict('records'),
							    	filter_action="native",
							        sort_action="native",
							        sort_mode="multi",
							        export_format='xlsx'
						    	)])
					]), 
				width={"size": 6}),
				dbc.Col(
					dbc.Card([
						dbc.CardHeader("The Good, The Bad, and the Ugly"),
						dbc.CardBody(
	            			[
		               			dcc.Graph(id='example-graph',figure=team_points_fig)
	                		])
					])
					, width={"size": 6})
				]),

  			dbc.Row(dbc.Col(dbc.CardBody(
            		[
                		html.H4("Player Total Expected Points vs. Actual Points (to Date) by Team", className="card-title"),
               			dcc.Graph(
						        id='team-scatter-graph',
						        figure=player_scatter_by_team
   							)
                	]), width={"size": 10, "offset": 1})),

  			dbc.Row(dbc.Col(dbc.CardBody(
            		[
                		html.H4("Player Box Plot by Position", className="card-title"),
               			dcc.Graph(
						        id='team-scatter-graph',
						        figure=player_box_plot_by_position
   							)
                	]), width={"size": 10, "offset": 1})),

			dbc.Row(dbc.Col(dbc.CardBody(
            		[
                		html.H4("Draft Plot", className="card-title"),
                		dcc.Dropdown(id='position_dropdown',
							options=[
								dict(label=draft_players_df.position.unique()[0], value=draft_players_df.position.unique()[0]),
			                    dict(label=draft_players_df.position.unique()[1], value=draft_players_df.position.unique()[1]),
			                    dict(label=draft_players_df.position.unique()[2], value=draft_players_df.position.unique()[2]),
			                    dict(label=draft_players_df.position.unique()[3], value=draft_players_df.position.unique()[3]),
			                    dict(label=draft_players_df.position.unique()[4], value=draft_players_df.position.unique()[4]),
			                    dict(label=draft_players_df.position.unique()[5], value=draft_players_df.position.unique()[5])
								],
							searchable=True,
							placeholder='All Positions',
							value='ALL',
							style=dict(width='30%')),
               			dcc.Graph(
						        id='draft-scatter-graph',
						        figure=draft_scatter
   							)
                	]), width={"size": 10, "offset": 1}))])

team_tab_content = html.Div(children=[

      dcc.Dropdown(id='team_picker',options=[
					dict(label=teams_df['drop_down'][0], value=teams_df['team_name'][0]),
                    dict(label=teams_df['drop_down'][1], value=teams_df['team_name'][1]),
                    dict(label=teams_df['drop_down'][2], value=teams_df['team_name'][2]),
                    dict(label=teams_df['drop_down'][3], value=teams_df['team_name'][3]),
                    dict(label=teams_df['drop_down'][4], value=teams_df['team_name'][4]),
                    dict(label=teams_df['drop_down'][5], value=teams_df['team_name'][5]),
                    dict(label=teams_df['drop_down'][6], value=teams_df['team_name'][6]),
                    dict(label=teams_df['drop_down'][7], value=teams_df['team_name'][7]),
                    dict(label=teams_df['drop_down'][8], value=teams_df['team_name'][8]),
                    dict(label=teams_df['drop_down'][9], value=teams_df['team_name'][9]),
                    dict(label=teams_df['drop_down'][10], value=teams_df['team_name'][10]),
                    dict(label=teams_df['drop_down'][11], value=teams_df['team_name'][11])
				],
				searchable=True,
				placeholder='Search Team Name...',
				value='Team YETI',
				style=dict(
                    width='60%'
                )),

      dcc.Graph(
				id='player_team_pie',
				figure=team_players_fig
   				),

      html.H4("Team Roster", className="card-title"),
		
	  team_players_table(players_df)

	  # html.H4("Team Activity", className="card-title"),

	  # recent_activity(activity_df)

	  ])

# RENDERING HTML
app.layout = html.Div(children=[

	dbc.NavbarSimple(
	    children=[
	        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
	        dbc.DropdownMenu(
	            children=[
	                dbc.DropdownMenuItem("More pages", header=True),
	                dbc.DropdownMenuItem("Page 2", href="#"),
	                dbc.DropdownMenuItem("Page 3", href="#"),
	            ],
	            nav=True,
	            in_navbar=True,
	            label="More",
	        ),
	    ],
	    brand="Who Brough Their Dad?",
	    brand_href="#",
	    color="primary",
	    dark=True,
	),

    html.Div(
    	[
	        dbc.Tabs(
	            [
	                dbc.Tab(label="LEAGUE DASHBOARD", tab_id="league_data"),
	                dbc.Tab(label="TEAMS DASHBOARD", tab_id="team_data"),
	            ],
	            id="tabs",
	            active_tab="league_data",
	        ),
	        html.Div(id="content"),
    	]
	)

])

# CALLBACKS 

# TAB CALLBACK 
@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "league_data":
        return league_tab_content
    elif at == "tab-2":
        return team_data
    return team_tab_content

# TEAM SWITCH FOR PIE CHART & TABLE CALLBACK
@app.callback([Output('player_team_pie', 'figure'), Output('team_player_table', 'data'), Output('team_player_table', 'columns')], [Input('team_picker', 'value')])
def update_team_players_fig(team_picker_value):
    players_df_filtered_by_team = players_df[players_df['team'] == team_picker_value]
    pie_title = 'Showing Points data by Position for ' + team_picker_value
    _cols = [{"name": i, "id": i} for i in players_df_filtered_by_team.columns]
    return [px.pie(players_df_filtered_by_team, values='points_scored', names='position', title=pie_title), players_df_filtered_by_team.to_dict('records'), _cols]

# TEAM SWITCH FOR ACTIVITY TABLE
# @app.callback([Output('recent_activity_table', 'data')], Output('recent_activity_table', 'columns'), [Input('team_picker', 'value')])
# def update_activity_fig(team_picker_value):
# 	activity_df_filtered_by_team = activity_df[activity_df['team'] == team_picker_value]
# 	activity_df_len = len(activity_df_filtered_by_team)
# 	if activity_df_len == 0:
# 		_cols = [{"name": i, "id": i} for i in activity_df.columns]
# 		return [activity_df.to_dict('records'), _cols]
# 	else:
# 		_cols = [{"name": i, "id": i} for i in activity_df_filtered_by_team.columns]
# 		return [activity_df_filtered_by_team.to_dict('records'), _cols]

# POSITION SWITCH FOR DRAFT FIGURE
@app.callback(Output('draft-scatter-graph', 'figure'), [Input('position_dropdown', 'value')])
def update_draft_scatter_fig(position_dropdown_value):
	if position_dropdown_value == 'ALL':
		return px.scatter(draft_players_df, x="bid_amount", y="points_scored", color="keeper_status", hover_data=['name', 'posRank', 'position'])
	else: 
		draft_players_df_filtered_by_position = draft_players_df[draft_players_df['position'] == position_dropdown_value]
		return px.scatter(draft_players_df_filtered_by_position, x="bid_amount", y="points_scored", color="keeper_status", hover_data=['name', 'posRank', 'position'])

# RUN SERVER
if __name__ == '__main__':
    app.run_server(debug=True)
