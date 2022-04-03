from time import sleep
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import boxscoretraditionalv2
import pandas as pd

# each quarters
periodes = [["0", "7200"], ["7200", "14400"], ["14400", "21600"], ["21600", "28800"]]

nba_teams = teams.get_teams()

for team in nba_teams :
    team_id = team['id']
    # Query for games where the team were playing
    is_error = True
    while is_error :
        try :
            sleep(0.6)
            gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, timeout=_timeout)
            is_error = False
        except Exception as e :
            print(e)
            is_error = True
            
    games = gamefinder.get_data_frames()[0]
    # Get only the actual season matchups
    games_2021 = games[games.SEASON_ID.str[-4:] == '2021']
    # header
    resume = [['Where?', 'date', 'matchup','Q1','Q2','Q3','Q4', 'Q1 adversary','Q2 adversary','Q3 adversary','Q4 adversary']]
    team_name = games_2021.iloc[-1]['TEAM_NAME']

    # change here to get only team in []
    if team_name not in ['Charlotte Hornets', 'Denver Nuggets',
    'Indiana Pacers', 'Atlanta Hawks' , 'Cleveland Cavaliers', 'Orlando Magic'] :
        continue

    for i in range (0,len(games_2021)-1):
        quarters = []
        game = games_2021.iloc[i]
        game_id = game['GAME_ID']
        where = 'home' if 'vs.' in game['MATCHUP'] else 'ext'
        date = game['GAME_DATE']
        matchup = game['MATCHUP']
        quarters.append(where)
        quarters.append(date)
        quarters.append(matchup)
        print(matchup)
        print(date)
        quarters_team = []
        quarters_team_vs = []
        for period in periodes :
            is_error = True
            while is_error :
                try:
                    sleep(0.6)
                    quarter = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id,range_type=2, start_period=1,end_period=10, start_range=period[0], end_range=period[1], timeout=2).get_data_frames()[0]
                    is_error = False
                except Exception as e:
                    print(e)
                    is_error = True
                    """ quarters_team.append("Not Found")
                    quarters_team_vs.append("Not Found") """
            quarter_team = quarter[quarter.TEAM_ID == team_id].sum(axis = 0, skipna = True)["PTS"]
            quarter_team_vs = quarter[quarter.TEAM_ID != team_id].sum(axis = 0, skipna = True)["PTS"]
            quarters_team.append(quarter_team)
            quarters_team_vs.append(quarter_team_vs)
        quarters = quarters + quarters_team + quarters_team_vs
        print(quarters)
        resume.append(quarters)

    df = pd.DataFrame(resume)
    file_title = team_name + '.csv'
    df.to_csv(file_title) 