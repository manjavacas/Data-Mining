import os
import chess.pgn as pgn
import pandas as pd

from numpy import mean, median, var

from datetime import datetime
from datetime import timedelta

GAMES_FILE = os.path.join('..', 'data', 'top200_sept2019', 'games0-199.pgn')
TARGET_DATA_FILE = os.path.join('..', 'data', 'target_data.csv')

COLUMNS = [
    'user_id',
    'game_link',
    'elo',
    'colour',
    'opening',
    'result',
    'movements',
    'total_time_player',
    'total_time',
    'early_times_mean',
    'early_times_median',
    'early_times_variance',
    'early_times_max',
    'early_times_min',
    'mid_times_mean',
    'mid_times_median',
    'mid_times_variance',
    'mid_times_max',
    'mid_times_min',
    'end_times_mean',
    'end_times_median',
    'end_times_variance',
    'end_times_max',
    'end_times_min',
    'points_balance',
    'taken_balance',
    'aggressiveness'
]

PIECE_WEIGHTS = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9
}

early_agressiveness = lambda early_taken_count: 0 if early_taken_count < 3 else (0.5 if early_taken_count < 6 else 1)

def time_metrics(times):
    '''
        Mean, median, variance, maximum, minimum
    '''
    return mean(times), median(times), var(times), max(times, default=None), min(times, default=None)

def partition_times(times, moves_count):
    '''
        Movement count / 2 => movements per player
        Movements per player / 3 => Movements per game stage
        
        Note: First movement time is omitted due to Lichess.org time format
    '''
    early_times = times[:int(moves_count/6)-1]
    mid_times = times[int(moves_count/6)-1:int(moves_count/3)]
    end_times = times[int(moves_count/3):]

    return early_times, mid_times, end_times


white_opening_aggressiveness = ['Sicilian Defense: Grand Prix Attack', 'Sicilian Defense: Smith-Morra Gambit', 'Trompowsky Attack', 'Trompowsky Attack: Classical Defense',
                                'Trompowsky Attack: Borg Variation', 'Trompowsky Attack: Raptor Variation', 'Trompowsky Attack: Edge Variation', 'Danish Gambit',
                                'Sicilian Defense: Alapin Variation', 'Sicilian Defense: Alapin Variation, Smith-Morra Declined', 'King\'s Gambit', 'Petrov\'s Defense',
                                'Four Knights Game: Italian Variation', 'Four Knights Game: Italian Variation, Noa Gambit', 'Four Knights Game: Scotch Variation Accepted',
                                'Four Knights Game: Scotch Variation, Belgrade Gambit', 'Four Knights Game: Spanish Variation', 'Four Knights Game: Spanish Variation, Classical Variation',
                                'Four Knights Game: Spanish Variation, Rubinstein Variation']
black_opening_aggressiveness = ['Queen\'s Gambit Refused: Albin Countergambit', 'Queen\'s Gambit Refused: Albin Countergambit, Modern Line', 'Queen\'s Gambit Refused: Albin Countergambit, Normal Line',
                                'Scandinavian Defense: Portuguese Variation', 'Alekhine Defense', 'Alekhine Defense: Balogh Variation', 'Alekhine Defense: Brooklyn Variation', 'Alekhine Defense: Exchange Variation',
                                'Alekhine Defense: Four Pawns Attack', 'Alekhine Defense: Four Pawns Attack, Main Line', 'Alekhine Defense: Four Pawns Attack, Trifunovic Variation', 'Alekhine Defense: Hunt Variation',
                                'Alekhine Defense: Hunt Variation, Lasker Simul Gambit', 'Alekhine Defense: Maróczy Variation', 'Alekhine Defense: Modern Variation, Alekhine Gambit', 'Alekhine Defense: Modern Variation, Alekhine Variation',
                                'Alekhine Defense: Modern Variation, Larsen Variation', 'Alekhine Defense: Modern Variation, Larsen-Haakert Variation', 'Alekhine Defense: Modern Variation, Main Line',
                                'Alekhine Defense: Modern Variation, Panov Variation', 'Alekhine Defense: Normal Variation', 'Alekhine Defense: Scandinavian Variation', 'Alekhine Defense: Sämisch Attack', 'Alekhine Defense: Two Pawn Attack',
                                'Alekhine Defense: Two Pawn Attack, Lasker Variation', 'Budapest Defense', 'Budapest Defense: Adler Variation', 'Budapest Defense: Rubinstein Variation', 'Sicilian Defense', 'Sicilian Defense: Accelerated Dragon',
                                'Sicilian Defense: Accelerated Dragon, Maróczy Bind', 'Sicilian Defense: Accelerated Dragon, Modern Bc4 Variation', 'Sicilian Defense: Alapin Variation', 'Sicilian Defense: Alapin Variation, Smith-Morra Declined',
                                'Sicilian Defense: Bowdler Attack', 'Sicilian Defense: Canal Attack, Haag Gambit', 'Sicilian Defense: Canal-Sokolsky Attack', 'Sicilian Defense: Classical Variation', 'Sicilian Defense: Closed', 'Sicilian Defense: Closed Variation',
                                'Sicilian Defense: Closed Variation, Chameleon Variation', 'Sicilian Defense: Closed Variation, Traditional', 'Sicilian Defense: Delayed Alapin', 'Sicilian Defense: Delayed Alapin Variation', 'Sicilian Defense: Dragon Variation',
                                'Sicilian Defense: Dragon Variation, Classical Variation', 'Sicilian Defense: Dragon Variation, Levenfish Variation', 'Sicilian Defense: Dragon Variation, Yugoslav Attack', 'Sicilian Defense: Dragon Variation, Yugoslav Attack, Belezky Line',
                                'Sicilian Defense: Dragon Variation, Yugoslav Attack, Modern Line', 'Sicilian Defense: Dragon, 6. Be3', 'Sicilian Defense: Four Knights Variation', 'Sicilian Defense: Franco-Sicilian Variation', 'Sicilian Defense: French Variation',
                                'Sicilian Defense: Grand Prix Attack', 'Sicilian Defense: Hyperaccelerated Dragon', 'Sicilian Defense: Kalashnikov Variation', 'Sicilian Defense: Kan Variation, Modern Variation', 'Sicilian Defense: Kramnik Variation',
                                'Sicilian Defense: Lasker-Dunne Attack', 'Sicilian Defense: Lasker-Pelikan Variation, Exchange Variation', 'Sicilian Defense: Lasker-Pelikan Variation, Schlechter Variation', 'Sicilian Defense: Lasker-Pelikan Variation, Sveshnikov Variation',
                                'Sicilian Defense: Lasker-Pelikan Variation, Sveshnikov Variation, Chelyabinsk Variation', 'Sicilian Defense: McDonnell Attack', 'Sicilian Defense: McDonnell Attack, Tal Gambit', 'Sicilian Defense: Modern Variations, Anti-Qxd4 Move Order',
                                'Sicilian Defense: Modern Variations, Tartakower', 'Sicilian Defense: Morphy Gambit', 'Sicilian Defense: Najdorf Variation', 'Sicilian Defense: Najdorf Variation, Adams Attack', 'Sicilian Defense: Najdorf Variation, Amsterdam Variation',
                                'Sicilian Defense: Najdorf Variation, English Attack', 'Sicilian Defense: Najdorf Variation, Main Line', 'Sicilian Defense: Najdorf Variation, Opocensky Variation', 'Sicilian Defense: Najdorf, Lipnitsky Attack', 'Sicilian Defense: Nyezhmetdinov-Rossolimo Attack',
                                'Sicilian Defense: O\'Kelly Variation, Maróczy Bind, Robatsch Line', 'Sicilian Defense: Old Sicilian', 'Sicilian Defense: Open', 'Sicilian Defense: Paulsen Variation', 'Sicilian Defense: Paulsen Variation, Bastrikov Variation', 'Sicilian Defense: Paulsen Variation, Normal Variation',
                                'Sicilian Defense: Paulsen Variation, Szén Variation', 'Sicilian Defense: Scheveningen Variation, Classical Variation', 'Sicilian Defense: Scheveningen Variation, Delayed Keres Attack', 'Sicilian Defense: Scheveningen Variation, English Attack', 'Sicilian Defense: Smith-Morra Gambit',
                                'Sicilian Defense: Smith-Morra Gambit Accepted, Classical Formation', 'Sicilian Defense: Smith-Morra Gambit Accepted, Fianchetto Defense', 'Sicilian Defense: Smith-Morra Gambit Accepted, Kan Formation', 'Sicilian Defense: Smith-Morra Gambit Accepted, Paulsen Formation',
                                'Sicilian Defense: Smith-Morra Gambit Accepted, Pin Defense', 'Sicilian Defense: Smith-Morra Gambit Accepted, Scheveningen Formation', 'Sicilian Defense: Smith-Morra Gambit Declined, Dubois Variation', 'Sicilian Defense: Smith-Morra Gambit Declined, Push Variation',
                                'Sicilian Defense: Smith-Morra Gambit Declined, Scandinavian Formation', 'Sicilian Defense: Smith-Morra Gambit Deferred', 'Sicilian Defense: Staunton-Cochrane Variation', 'Sicilian Defense: Wing Gambit', 'Sicilian Defense: Wing Gambit, Carlsbad Variation',
                                'Sicilian Defense: Wing Gambit, Marshall Variation']

games = []

# Load games from PGN file
with open(GAMES_FILE, encoding="utf-8-sig") as f:
    game = pgn.read_game(f)
    
    game_index = 0
    while game:
        game_index += 1
        print(f"\r{game_index} {game.headers['Site']}", end='', flush=True)

        row_white = []
        row_black = []

        # USER_ID
        row_white.append(game.headers['White'])
        row_black.append(game.headers['Black'])

        # GAME_LINK
        row_white.append(game.headers['Site'])
        row_black.append(game.headers['Site'])

        # ELO
        try:
            white_elo = int(game.headers['WhiteElo'])
        except ValueError:
            white_elo = None

        try:
            black_elo = int(game.headers['BlackElo'])
        except ValueError:
            black_elo = None
        
        # Si el ELO es '?' (es la IA), rellenamos con el ELO del oponente (porque Lichess genera partidas de ELO similar)
        if white_elo is None:
            white_elo = black_elo
        if black_elo is None:
            black_elo = white_elo
        
        row_white.append(white_elo)
        row_black.append(black_elo)

        # COLOUR
        row_white.append('White')
        row_black.append('Black')

        # OPENING
        row_white.append(game.headers['Opening'])
        row_black.append(game.headers['Opening'])

        # RESULT

        if "1/2" in game.headers['Result']:
            result_white = 1
            result_black = 1
        elif game.headers['Result'][0] == "1":
            result_white = 2
            result_black = 0
        else:
            result_white = 0
            result_black = 2

        row_white.append(result_white)
        row_black.append(result_black)

        ## TIME_PER_MOVEMENT, POINTS_BALANCE, TAKEN_BALANCE

        white = {'taken': [], 'times': [], '_last_time': None}
        black = {'taken': [], 'times': [], '_last_time': None}
        time_increase = int(game.headers['TimeControl'].split('+')[-1])

        board = game.board()

        for i, node in enumerate(game.mainline()):
            # Parse remaining time from GameMove
            try:
                t = datetime.strptime(node.comment[6:-1], "%H:%M:%S")
            except ValueError:
                t = datetime.strptime('0:0:0', "%H:%M:%S")
                
            remaining_time = timedelta(
                hours=t.hour, minutes=t.minute, seconds=t.second)

            # TIME_PER_MOVEMENT
            if i % 2 == 0:  # White player
                if white['_last_time'] is not None:
                    white['times'].append(
                        (white['_last_time'] - remaining_time).total_seconds() + time_increase)
                white['_last_time'] = remaining_time
            else:  # Black player
                if black['_last_time'] is not None:
                    black['times'].append(
                        (black['_last_time'] - remaining_time).total_seconds() + time_increase)
                black['_last_time'] = remaining_time

            ## TAKEN_BALANCE & POINTS_BALANCE
            if 'x' in node.san():
                taken_piece = board.piece_at(node.move.to_square)
                if taken_piece is None: # Take "on passant" (the Pawn is not in the dst square)
                    piece_weight = PIECE_WEIGHTS['P']
                else:
                    piece_weight = PIECE_WEIGHTS[taken_piece.symbol().upper()]
                
                if i % 2 == 0:  # White player takes the piece
                    white['taken'].append(1 * piece_weight)
                    black['taken'].append(-1 * piece_weight)
                else:  # Black player takes the piece
                    black['taken'].append(1 * piece_weight)
                    white['taken'].append(-1 * piece_weight)
            else:  # No takes in this movement
                white['taken'].append(0)
                black['taken'].append(0)

            board.push(node.move)

        del white['_last_time']
        del black['_last_time']

        # NUMBER_OF_MOVEMENTS
        assert len(white['taken']) == len(black['taken'])
        moves_count = len(white['taken'])

        row_white.append(moves_count)
        row_black.append(moves_count)

        # TOTAL_TIME_PER_PLAYER

        row_white.append(sum(white['times']))
        row_black.append(sum(black['times']))

        # TOTAL_TIME

        total_time = sum(white['times']) + sum(black['times'])

        row_white.append(total_time)
        row_black.append(total_time)

        # Partition movement times in early/mid/end
        w_early, w_mid, w_end = partition_times(white['times'], moves_count)
        b_early, b_mid, b_end = partition_times(black['times'], moves_count)

        
        if(any(len(t) == 0 for t in [w_early, w_mid, w_end, b_early, b_mid, b_end])):
            print()
            print(w_early, w_mid, w_end)
            print(b_early, b_mid, b_end)

        # TIME_METRICS (mean, median, var, max, min) to player rows
        row_white.extend(time_metrics(w_early))
        row_white.extend(time_metrics(w_mid))
        row_white.extend(time_metrics(w_end))

        row_black.extend(time_metrics(b_early))
        row_black.extend(time_metrics(b_mid))
        row_black.extend(time_metrics(b_end))


        ## POINTS_BALANCE & TAKEN_BALANCE

        row_white.append(sum(white['taken']))
        row_white.append(sum([1 if t > 0 else 0 for t in white['taken']]) +
                        sum([-1 if t < 0 else 0 for t in white['taken']]))

        row_black.append(sum(black['taken']))
        row_black.append(sum([1 if t > 0 else 0 for t in black['taken']]) +
                        sum([-1 if t < 0 else 0 for t in black['taken']]))

        # AGGRESSIVENESS

        white_aggressiveness = 0
        black_aggressiveness = 0

        # EARLY_TAKEN

        white_early_taken = sum([1 for white_taken in white['taken'][:int(moves_count/3)] if white_taken > 0])
        black_early_taken = sum([1 for black_taken in black['taken'][:int(moves_count/3)] if black_taken > 0])

        white_aggressiveness += early_agressiveness(white_early_taken)
        black_aggressiveness += early_agressiveness(black_early_taken)

        # CASTLING

        white_castling = False
        black_castling = False

        for i, move in enumerate(game.mainline()):
            if move.san() == 'O-O':
                if i % 2 == 0:  # White player
                    white_castling = True
                else:  # Black player
                    black_castling = True

        if not white_castling:
            white_aggressiveness += 2

        if not black_castling:
            black_aggressiveness += 2

        # AGGRESSIVE_OPENING

        white_aggressive_opening = False
        black_aggressive_opening = False

        if game.headers['Opening'] in white_opening_aggressiveness:
            white_aggressive_opening = True
            white_aggressiveness += 2

        if game.headers['Opening'] in black_opening_aggressiveness:
            black_aggressive_opening = True
            black_aggressiveness += 2

        row_white.append(white_aggressiveness)
        row_black.append(black_aggressiveness)

        games.append(row_white)
        games.append(row_black)

        # Read next game. Iterate again
        game = pgn.read_game(f)

# Save target data into csv
df = pd.DataFrame(games, columns=COLUMNS)
df.to_csv(path_or_buf=TARGET_DATA_FILE)
