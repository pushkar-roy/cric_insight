from flask import Flask, render_template, request
from database import get_player_stats, get_team_stats

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/player', methods=['GET'])
def player():
    player_name = request.args.get('name')
    if not player_name:
        return "Please provide a player name."
    
    stats = get_player_stats(player_name)
    return render_template('player.html', player_name=player_name, stats=stats)

@app.route('/team', methods=['GET'])
def team():
    team_name = request.args.get('name')
    if not team_name:
        return "Please provide a team name."
    
    stats = get_team_stats(team_name)
    return render_template('team.html', team_name=team_name, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
