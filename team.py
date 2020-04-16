from json import JSONDecodeError

from liquipediapy import dota
import json
import time
import os.path
from liquipediapy.exceptions import RequestsException
from getpass import getpass
from string import Template
import player
from tools import *

def parse_teams(teams, path=""):
    try:
        os.mkdir('{}/teams'.format(path))
    except FileExistsError:
        pass
    # look files in path directory
    # if files exist ask for update files
    # if not then start writing files
    for team in teams:
        if os.path.isfile('{}/teams/{}/{}.json'.format(path, team, team.lower().replace(" ", "_"))):            
            print ("Team {} exist, update json? [yes/any]".format(team))
            ans = input()
            if ans == "y" or ans == "yes":
                roster = _create_new_teams([team], path, create=True)

                print ("Update {} players? [yes/any]".format(team))
                ans = input()
                if ans == "y" or ans == "yes":
                    player.parse_players(roster, path, create=True)
                else:
                    player.parse_players(roster, path, create=False)
            else:
                _create_new_teams([team], path, create=False)

        else:
            try:
                os.mkdir('{}/teams/{}'.format(path, team))
            except FileExistsError:
                pass
            roster = _create_new_teams([team], path, create=True)
            player.parse_players(roster, path, create=True)


def _create_new_teams(teams, path, create=False):
    # for request to liquipedia
    dota_obj = dota("KB_Parser (https://github.com/Finger228/LiquiParser; alexandr_zagorskiy@mail.ru")
    
    # for every team get json from liquipedia api
    # parse it and get new json with need info
    # then save new json file or .scs files in path directory
    # return list of players from teams

    players = []
    for team in teams:
        team_idtf = get_idtf(team)
        
        if create == True:
            team_info = dota_obj.get_team_info(team, True)
            team_info = _sort_team_data(team, team_info)
            for player in team_info['roster']:
                players.append(player['nickname'])  

            with open('{}/teams/{}/{}.json'.format(path, team, team_idtf), 'w') as f:
                f.write(json.dumps(team_info, ensure_ascii=False))
            print("Json of {} created".format(team))
                
        else:
            with open('{}/teams/{}/{}.json'.format(path, team, team_idtf), 'r') as f:
                team_info = json.load(f)
        
        team_info = _team_json_to_scs(team, team_idtf, team_info)

        with open('{}/teams/{}/{}.scs'.format(path, team, team_idtf), 'w') as r:
            r.write(team_info[0])

        with open('{}/teams/{}/{}_roster.scs'.format(path, team, team_idtf), 'w') as r:
            r.write(team_info[1])

        print("scs of {} created".format(team))

    return players


def _sort_team_data(team, team_info):
    # parse needed fields and create dict for json
    try:
        location = team_info['info']['location']
    except KeyError:
        location = ""
    
    try:
        created = team_info['info']['created'][-10:]
    except KeyError:
        created = ""

    try:
        sponsor = team_info['info']['sponsor']
    except KeyError:
        sponsor = ""

    try:
        manager = team_info['info']['manager'][1:]
    except KeyError:
        manager = ""

    try:
        director = team_info['info']['director'][1:]
    except KeyError:
        director = ""

    try:
        coach = team_info['info']['coach'][1:]
    except KeyError:
        coach = ""
    
    try:
        team_roster = [{"nickname": player['ID'][1:], "pos": player['Position'][-1:]} for player in team_info['team_roster']]
    except KeyError:
        team_roster = [{"nickname": player['ID'][1:], "pos": ""} for player in team_info['team_roster']]
        
    team_data = {
        'id': team,
        'location': location,
        'coach': coach,
        'director': director,
        'manager': manager,
        'sponsor': sponsor,
        'created': created,
        'roster': team_roster,
    }
    
    return team_data


def _team_json_to_scs(team, team_idtf, team_info):
    # transform json to .scs files
    # templates of .scs files in /templates/ dir 
    result = []
    location = [get_idtf(country) for country in team_info['location']]
    sponsor = [get_idtf(single) for single in team_info['sponsor']]

    format_location = ""
    for country in location:
        format_location += '\n\t=>nrel_location: {};'.format(country)
    
    format_director = "" if team_info['director'] == "" else '=>nrel_director: {};'.format(
        get_idtf(team_info['director'])
        )
    format_manager = "" if team_info['manager'] == "" else '=>nrel_manager: {};'.format(
        get_idtf(team_info['manager'])
        )
    format_coach = "" if team_info['coach'] == "" else '=>nrel_coach: player_{}_dota;'.format(
        get_idtf(team_info['coach'])
        )
    
    format_sponsors = ""
    for single in sponsor:
        format_sponsors += '\n\t=>nrel_sponsor: {};'.format(single)

    with open('templates/team.scs') as f:
        src = Template(f.read())
        team_data = {
            'team_sys_idtf': "team_{}_dota".format(team_idtf),
            'team_main_idtf': team,
            'location': format_location,
            'director': format_director,
            'manager': format_manager,
            'coach': format_coach,
            'created': team_info['created'].replace("-", "_"),
            'created_idtf': team_info['created'],
            'created_day': team_info['created'][-2:],
            'created_month': team_info['created'][5:-3],
            'created_year': team_info['created'][:4],
            'sponsor': format_sponsors,
            'roster': "roster_{}_dota".format(team_idtf),
        }

        # first part for team file
        result.append(src.substitute(team_data))

    roster = ""
    for player in team_info['roster']:
        player_idtf = get_idtf(player['nickname'])
        if player['pos'] == "1":
            roster += '\n\t->rrel_carry_dota: player_{}_dota;'.format(player_idtf)
        if player['pos'] == "2":
            roster += '\n\t->rrel_midlaner_dota: player_{}_dota;'.format(player_idtf)
        if player['pos'] == "3":
            roster += '\n\t->rrel_offlaner_dota: player_{}_dota;'.format(player_idtf)
        if player['pos'] == "4":
            roster += '\n\t->rrel_semi_support_dota: player_{}_dota;'.format(player_idtf)
        if player['pos'] == "5":
            roster += '\n\t->rrel_full_support_dota: player_{}_dota;'.format(player_idtf)

    with open('templates/roster.scs') as f:
        src = Template(f.read())
        team_roster = {
            'roster_sys_idtf': "roster_{}_dota".format(team_idtf),
            'roster_idtf_en': "{} Dota 2 roster".format(team),
            'roster_idtf_ru': "Dota 2 состав {}".format(team),
            'roster': roster,
        }       

        #second part for roster file  
        result.append(src.substitute(team_roster))
    
    return result

