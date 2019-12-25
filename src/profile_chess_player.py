import os
import pandas as pd
import json

TARGET_DATA_FILE = os.path.join('..', 'data', 'target_data.csv')
TARGET_TEST_FILE = os.path.join('..', 'data', 'test', 'target_data_test.csv')
PLAYER_DATA_FILE = os.path.join('..', 'data', 'player_data.csv')

USER_ID_COLUMN = 1
AGGRESSIVENESS_COLUMN = 27
OPENING_COLUMN = 5
ELO_COLUMN = 3
RESULT_COLUMN = 6
COLOUR_COLUMN = 4
TOTAL_TIME_PLAYER_COLUMN = 8
MOVEMENTS_COLUMN = 7
POINTS_BALANCE_COLUMN = 25
TAKEN_BALANCE_COLUMN = 26

COLUMNS = [
    'user_id',
    'aggressiveness_mean',
    'most_common_opening',
    'maximum_elo',
    'winning_colour',
    'time_per_game_mean',
    'movements_mean',
    'points_balance_mean',
    'taken_balance_mean'
]

def most_frequent(l):
    return max(set(l), key = l.count)

with open(os.path.join('..', 'data', 'top200_sept2019', 'user_ids_top200.json'), 'r') as f:
    users = json.load(f)['user_ids']

players = []
read_players = []

# Load the data
data = pd.read_csv(TARGET_DATA_FILE)
data_test = pd.read_csv(TARGET_TEST_FILE)

data = data.append(data_test, ignore_index=True)
data['user_id'] = data['user_id'].str.lower()

for player_id in users:
    if data[data['user_id'] == player_id].empty:
        continue

    row_player = []

    # User id
    row_player.append(player_id)

    # Aggressiveness mean
    aggressiveness_mean = data[data['user_id'] == player_id].iloc[:, AGGRESSIVENESS_COLUMN].mean()
    row_player.append(aggressiveness_mean)

    # Most common opening
    opening_used = data[data['user_id'] == player_id].iloc[:, OPENING_COLUMN]
    opening_list = []
    for i in range(0, len(opening_used)):
        opening_list.append(opening_used.iloc[i].split(':')[0])

    most_common_opening = most_frequent(opening_list)
    row_player.append(most_common_opening)

    # Maximum elo
    maximum_elo = data[data['user_id'] == player_id].iloc[:, ELO_COLUMN].max()
    row_player.append(maximum_elo)

    # Winning colour
    win_games = data[data['user_id'] == player_id].iloc[:, [RESULT_COLUMN, COLOUR_COLUMN]]

    win_white_game = win_games[win_games['result'] == 2]
    games_win_white = len(win_white_game[win_white_game['colour'] == 'White'])

    win_black_game = win_games[win_games['result'] == 0]
    games_win_black = len(win_black_game[win_black_game['colour'] == 'Black'])

    if (games_win_white >= games_win_black):
        row_player.append('White')
    else:
        row_player.append('Black')

    # Time per game mean
    time_per_game_mean = data[data['user_id'] == player_id].iloc[:, TOTAL_TIME_PLAYER_COLUMN].mean()
    row_player.append(time_per_game_mean)

    # Movements mean
    movements_mean = data[data['user_id'] == player_id].iloc[:, MOVEMENTS_COLUMN].mean()
    row_player.append(round(movements_mean))

    # Points balance mean
    points_balance_mean = data[data['user_id'] == player_id].iloc[:, POINTS_BALANCE_COLUMN].mean()
    row_player.append(round(points_balance_mean))

    # Taken balance mean
    taken_balance_mean = data[data['user_id'] == player_id].iloc[:, TAKEN_BALANCE_COLUMN].mean()
    row_player.append(round(taken_balance_mean))

    # Add the row
    players.append(row_player)
    read_players.append(player_id)

    # Row print
    print(row_player)

# Save target data into csv
df = pd.DataFrame(players, columns=COLUMNS)

df.to_csv(path_or_buf=PLAYER_DATA_FILE)