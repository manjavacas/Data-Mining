from datetime import datetime
import json
import os

from berserk.formats import PGN, NDJSON
from berserk import PerfType
import berserk.models

def export_by_player(self, username, as_pgn=None, since=None, until=None,
                         max=None, vs=None, rated=None, perf_type=None,
                         color=None, analysed=None, moves=None, tags=None,
                         evals=None, opening=None, clocks=None):
    path = f'api/games/user/{username}'
    params = {
        'since': since,
        'until': until,
        'max': max,
        'vs': vs,
        'rated': rated,
        'perfType': perf_type,
        'color': color,
        'analysed': analysed,
        'moves': moves,
        'tags': tags,
        'clocks': str(clocks).lower(), # manually included
        'evals': evals,
        'opening': str(opening).lower(), # manually included
    }
    self.pgn_as_default = True
    fmt = PGN if (as_pgn if as_pgn is not None else self.pgn_as_default) else NDJSON
    yield from self._r.get(path, params=params, fmt=fmt, stream=True,
                            converter=berserk.models.Game.convert)

USER_COUNT = 200

# API client
client = berserk.Client()

user_ids = [u['id'] for u in client.users.get_leaderboard(PerfType.CLASSICAL, USER_COUNT)]

print(f'Top {len(user_ids)} users:\n{user_ids}')

with open(os.path.join('..', 'data', 'user_ids.json'), 'w') as f:
  json.dump({'user_ids': user_ids}, f)

START_TIME = datetime(year=2019, month=9, day=1)
END_TIME = datetime(year=2019, month=10, day=1)


games = []
user_ids_subset = user_ids[100:]
for user_id in user_ids_subset:
  # Get list of games for each player
  user_games = list(export_by_player(client, user_id,
                                clocks=True,
                                opening=True,
                                since=int(1000 * START_TIME.timestamp()),
                                until=int(1000 * END_TIME.timestamp()),
                                perf_type=PerfType.CLASSICAL))
  
  games.extend(user_games)
  print(f"> {len(user_games)} games from '{user_id}'")
  

print(f"Got {len(games)} games from {len(user_ids_subset)} top users ({START_TIME.strftime('%d/%m/%Y')} - {END_TIME.strftime('%d/%m/%Y')})")

# Sample game
print(games[0])

# Save games as PGN file
with open(os.path.join('..', 'data', 'games.pgn'), 'a') as f:
  for game in games:
    f.write(game)
    f.write("\n\n")
