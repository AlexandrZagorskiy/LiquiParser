from json import JSONDecodeError

from liquipediapy import dota
import json
import time

from liquipediapy.exceptions import RequestsException

dota_obj = dota("Bot for creating knowledge base for OSTIS app (https://github.com/ostis-apps; alexandr_zagorskiy@mail.ru")

players = dota_obj.get_players()
players = [player['ID'] for player in players]
players_count = len(players)
counter = 0
players_details = []
players = iter(players)

with open('players_info.json', 'w') as f:
    for player in players:
        time.sleep(30)
        counter += 1
        if counter % 50 == 1:
            print("#{} from {}, nickname {}".format(counter, players_count, player))
        try:
            players_details.append(dota_obj.get_player_info(player, True))
        except RequestsException:
            print("error in #{}, nickname {}".format(counter, player))
            next(players, None)
            continue

    f.write(json.dumps(players_details, ensure_ascii=False))

    #
    # player_cleared_details = {
    #     "romanized_name": "John",
    #     "birth_details": 30,
    #     "country": "New York",
    #     "team": "New York",
    #     "history": "New York",
    # }
# print(player_details)
