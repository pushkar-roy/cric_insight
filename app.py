from flask import Flask, render_template, jsonify, request
from player_stats_career import get_player_stats
from player_stats_season import get_season_stats
from team_records import get_team_records
from player_records import get_player_records
from team_stats_career import get_team_stats
from team_stats_seasonwise import get_team_stats_by_season


app = Flask(__name__)

DB_PATH = "ipl_stats.db"

@app.route('/')
def home():
    player_data = get_player_records()
    team_data = get_team_records()
    return render_template('home.html', player_data=player_data, team_data=team_data)

@app.route('/player_stats', methods=['POST'])
def player_stats():
    player_name = request.form['player_name']
    return render_template('player_stats.html', player_name=player_name)

@app.route('/data/<player_name>')
def get_data(player_name):
    season_data = get_season_stats(player_name)
    career_data = get_player_stats(player_name)

    graph_data = []

    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["runs_scored_by_year"].keys()),
        'values': list(season_data["runs_scored_by_year"].values()),
        'rank_value': career_data["total_runs_scored"][0],
        'rank': career_data["total_runs_scored"][1],
        'title': 'Runs Scored each Year',
        'y_axis_label': 'Runs',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["runs_given_by_year"].keys()),
        'values': list(season_data["runs_given_by_year"].values()),
        'rank_value': career_data["total_runs_given"][0],
        'rank': career_data["total_runs_given"][1],
        'title': 'Runs Given each Year',
        'y_axis_label': 'Runs',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["fours_by_year"].keys()),
        'values': list(season_data["fours_by_year"].values()),
        'rank_value': career_data["total_fours_scored"][0],
        'rank': career_data["total_fours_scored"][1],
        'title': 'Fours each Year',
        'y_axis_label': 'Fours',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["sixes_by_year"].keys()),
        'values': list(season_data["sixes_by_year"].values()),
        'rank_value': career_data["total_sixes_scored"][0],
        'rank': career_data["total_sixes_scored"][1],
        'title': 'Sixes each Year',
        'y_axis_label': 'Sixes',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["wickets_by_year"].keys()),
        'values': list(season_data["wickets_by_year"].values()),
        'rank_value': career_data["total_wickets_taken"][0],
        'rank': career_data["total_wickets_taken"][1],
        'title': 'Wickets each Year',
        'y_axis_label': 'Wickets',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["catches_by_year"].keys()),
        'values': list(season_data["catches_by_year"].values()),
        'rank_value': career_data["total_catches"][0],
        'rank': career_data["total_catches"][1],
        'title': 'Catches each Year',
        'y_axis_label': 'Catches',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["ball_thrown_by_year"].keys()),
        'values': list(season_data["ball_thrown_by_year"].values()),
        'rank_value': career_data["total_ball_thrown"][0],
        'rank': career_data["total_ball_thrown"][1],
        'title': 'Balls Thrown each Year',
        'y_axis_label': 'Balls',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["hundreds_by_year"].keys()),
        'values': list(season_data["hundreds_by_year"].values()),
        'rank_value': career_data["hundreds"][0],
        'rank': career_data["hundreds"][1],
        'title': 'Hundreds each Year',
        'y_axis_label': 'Hundreds',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'bar',
        'labels': list(season_data["fifties_by_year"].keys()),
        'values': list(season_data["fifties_by_year"].values()),
        'rank_value': career_data["fifties"][0],
        'rank': career_data["fifties"][1],
        'title': 'Fifties each Year',
        'y_axis_label': 'Fifties',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["batting_avg_by_year"].keys()),
        'values': list(season_data["batting_avg_by_year"].values()),
        'rank_value': career_data["batting_avg"][0],
        'rank': career_data["batting_avg"][1],
        'title': 'yearwise Batting Average',
        'y_axis_label': 'Average',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["batting_strike_rate_by_year"].keys()),
        'values': list(season_data["batting_strike_rate_by_year"].values()),
        'rank_value': career_data["batting_strike_rate"][0],
        'rank': career_data["batting_strike_rate"][1],
        'title': 'yearwise Batting Strike Rate',
        'y_axis_label': 'Strike Rate',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["bowling_avg_by_year"].keys()),
        'values': list(season_data["bowling_avg_by_year"].values()),
        'rank_value': career_data["bowling_avg"][0],
        'rank': career_data["bowling_avg"][1],
        'title': 'Yearwise Bowling Average',
        'y_axis_label': 'Average',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["bowling_strike_rate_by_year"].keys()),
        'values': list(season_data["bowling_strike_rate_by_year"].values()),
        'rank_value': career_data["bowling_strike_rate"][0],
        'rank': career_data["bowling_strike_rate"][1],
        'title': 'Yearwise Bowling Strike Rate',
        'y_axis_label': 'Strike Rate',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["economy_by_year"].keys()),
        'values': list(season_data["economy_by_year"].values()),
        'rank_value': career_data["economy"][0],
        'rank': career_data["economy"][1],
        'title': 'Yearwise Economy Rate',
        'y_axis_label': 'Economy',
        'x_axis_label': 'Year'
    })
    graph_data.append({
        'type': 'line',
        'labels': list(season_data["dot_balls_by_year"].keys()),
        'values': list(season_data["dot_balls_by_year"].values()),
        'rank_value': career_data["dot_balls"][0],
        'rank': career_data["dot_balls"][1],
        'title': 'Yearwise dot balls',
        'y_axis_label': 'Dot Balls',
        'x_axis_label': 'Year'
    })

    last_3_data = [
        {
            'value': career_data["five_wickets"][0],
            'rank': career_data["five_wickets"][1],
            'title': 'Five Wicket Hauls'
        },
        {
            'value': career_data["high_score"][0],
            'rank': career_data["high_score"][1],
            'title': 'Highest Score'
        },
        {
            'value': career_data["best_figure"][0],
            'rank': career_data["best_figure"][1],
            'title': 'Best Bowling Figure'
        },
    ]

    return jsonify({
        'graphs': graph_data,
        'last_3': last_3_data,
        'total_players': career_data["total_players"]
    })
    
@app.route('/team_stats', methods=['POST'])
def team_stats():
    team_name = request.form['team_name']
    return render_template('team_stats.html', team_name=team_name)

@app.route('/team_data/<team_name>')
def get_team_data(team_name):
    season_data = get_team_stats_by_season(team_name)
    career_data = get_team_stats(team_name)

    return jsonify({
        'season_data': season_data,
        'career_data': career_data
    })

if __name__ == '__main__':
    app.run(debug=True)