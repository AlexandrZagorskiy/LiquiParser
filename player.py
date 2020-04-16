from json import JSONDecodeError

from liquipediapy import dota
import json
import os.path
import re
import time
from liquipediapy.exceptions import RequestsException
from getpass import getpass
from string import Template
from tools import *

def parse_players(players, path="", create=False):      
    try:
        os.mkdir('{}/players'.format(path))
    except FileExistsError:
        pass
    _create_new_players(players, path, create)


def _create_new_players(players, path, create):
    # https://liquipedia.net/api-terms-of-use
    if players == []:
        return
    
    dota_obj = dota("KB_Parser (https://github.com/Finger228/LiquiParser; alexandr_zagorskiy@mail.ru")
    
    for player in players:  
        player_idtf = get_idtf(player)
        if create == True:
            # time.sleep(5)
            player_info = dota_obj.get_player_info(player, True)
            player_info = _sort_player_data(player, player_info)                       
            with open('{}/players/{}.json'.format(path, player_idtf), 'w') as f:
                f.write(json.dumps(player_info, ensure_ascii=False))
            print("Json of {} created".format(player))
        else:
            with open('{}/players/{}.json'.format(path, player_idtf), 'r') as f:
                player_info = json.load(f)
                
        player_info = _player_json_to_scs(player, player_idtf, player_info)

        with open('{}/players/{}.scs'.format(path, player_idtf), 'w') as r:
            r.write(player_info)

        print("scs of {} created".format(player))


def _sort_player_data(player, player_info):  
    try:
        name = str(player_info['info']['name'])
    except KeyError:
        name = ""
    try:
        romanized_name = player_info['info']['romanized_name']
    except KeyError:
        romanized_name = player_info['info']['name']
    
    try:
        country = player_info['info']['country']
    except KeyError:
        country = ""

    try:
        birthday = re.search(r'(\d|\?){4}(-(\d|\?){2}){2}', player_info['info']['birth_details']).group(0)
    except KeyError:
        birthday = ""

    try:
        history = [{"team": team['name'], "duration": team['duration']} for team in player_info['history']]
    except KeyError:
        history = []

    player_data = {
        'nickname': player,
        'name': name,
        'romanized_name': romanized_name,
        'country': country,
        'birthday': birthday,
        'history': history,
    }

    return player_data


def _player_json_to_scs(player, player_idtf, player_info):
    # transform json to .scs filesplayer_idtf
    # templates of .scs files in /templates/ dir 
    contracts = ""
    for team in player_info['history']:
        team_idtf = get_idtf(team['team'])
        start_date = team['duration'][:10].replace("?", "x")
        end_date = team['duration'][13:].replace("?", "x")
        if end_date == "Present":
            end_date = 'xxxx_xx_xx'
        contract_idtf = 'contract_{}_and_team_{}_dota'.format(player_idtf, team_idtf)
        with open('templates/contract.scs') as с:
            src = Template(с.read())
            contract_data = {
                'contract_idtf': contract_idtf,
                'player': player,
                'team': team['team'],
                'team_idtf': team_idtf,
                'start_date_idtf': get_idtf(start_date),
                'start_date': start_date,
                'end_date_idtf': get_idtf(end_date),
                'end_date': end_date,
                'start_day': start_date[-2:],
                'start_month': start_date[5:-3],
                'start_year': start_date[:4],
                'end_day': end_date[-2:],
                'end_month': end_date[5:-3],
                'end_year': end_date[:4],
            }

            # first part for team file
            contracts += src.substitute(contract_data)

    format_country = ""
    for country in player_info['country']:
        format_country += '\n\t=>nrel_country: {};'.format(country.lower().replace(" ", "_"))
    
    format_firstname, format_surname = list(player_info['romanized_name'].split(" ", 1))
    format_firstname = get_idtf(format_firstname)
    format_surname = get_idtf(format_surname)
    
    with open('templates/player.scs') as f:
        src = Template(f.read())
        team_data = {
            'player_sys_idtf': "player_{}_dota".format(player_idtf),
            'player_main_idtf': player,
            'country': format_country,
            'surname': format_surname,
            'firstname': format_firstname,
            'nickname': "player_{}_dota".format(player_idtf),
            'birthday': player_info['birthday'].replace("-", "_"),
            'birthday_idtf': player_info['birthday'],
            'birthday_day': player_info['birthday'][-2:],
            'birthday_month': player_info['birthday'][5:-3],
            'birthday_year': player_info['birthday'][:4],
            'contracts': contracts,
        }

        # first part for team file
        result = src.substitute(team_data) 
    
    return result

