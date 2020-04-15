from json import JSONDecodeError

from liquipediapy import dota
import json
import time
import os.path
from liquipediapy.exceptions import RequestsException
from getpass import getpass
from string import Template

def parse_teams(teams, path="", file_type="scs"):
    # look files in path directory
    # if files exist ask for update files
    # if not then start writing files
    for team in teams:
        if os.path.isfile('{}/teams/{}/{}.{}'.format(path, team, team.lower().replace(" ", "_"), file_type)):            
            print ("Team {} exist, update? [yes/any]".format(team))
            ans = getpass(prompt="")
            if ans == "y" or ans == "yes":
                _create_new_teams([team], path=path, file_type=file_type)
            else:
                continue

        else:
            try:
                os.mkdir('{}/teams/{}'.format(path, team))
            except FileExistsError:
                pass
            _create_new_teams([team], path=path)

def _create_new_teams(teams, path="", file_type="scs"):
    # for request to liquipedia
    dota_obj = dota("Bot for creating knowledge base for OSTIS app (https://github.com/ostis-apps; alexandr_zagorskiy@mail.ru")
    
    # for every team get json from liquipedia api
    # parse it and get new json with need info
    # then save new json file or .scs files in path directory
    for team in teams:
        team_idtf = team.lower().replace(" ", "_")
        team_info = dota_obj.get_team_info(team, True)
        team_info = _sort_team_data(team, team_info)
        
        if file_type == "json":            
            with open('{}/teams/{}/{}.json'.format(path, team, team_idtf), 'w') as f:
                f.write(json.dumps(team_info, ensure_ascii=False))

        elif file_type == "scs":
            team_info = _team_json_to_scs(team, team_idtf, team_info)

            with open('{}/teams/{}/{}.scs'.format(path, team, team_idtf), 'w') as r:
                r.write(team_info[0])

            with open('{}/teams/{}/{}_roster.scs'.format(path, team, team_idtf), 'w') as r:
                r.write(team_info[1])

        print("create {} team".format(team))

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
    location = [country.lower().replace(" ", "_") for country in team_info['location']]
    sponsor = [single.lower().replace(" ", "_") for single in team_info['sponsor']]

    format_location = ""
    for country in location:
        format_location += '\n\t=>nrel_location: {};'.format(country)
    
    format_director = "" if team_info['director'] == "" else '\t=>nrel_director: {};'.format(
        team_info['director'].lower().replace(" ", "_")
        )
    format_manager = "" if team_info['manager'] == "" else '\t=>nrel_manager: {};'.format(
        team_info['manager'].lower().replace(" ", "_")
        )
    format_coach = "" if team_info['coach'] == "" else '\t=>nrel_coach: {};'.format(
        team_info['coach'].lower().replace(" ", "_")
        )
    format_director = "" if team_info['director'] == "" else '\t=>nrel_director: {};'.format(
        team_info['director'].lower().replace(" ", "_")
        )
    
    format_sponsors = ""
    for single in sponsor:
        format_location += '\n\t=>nrel_sponsor: {};'.format(single)

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
        player_idtf = player['nickname'].lower().replace(" ", "_")
        if player['pos'] == "1":
            roster += '\n\t->rrel_carry_dota: {};'.format(player_idtf)
        if player['pos'] == "2":
            roster += '\n\t->rrel_midlaner_dota: {};'.format(player_idtf)
        if player['pos'] == "3":
            roster += '\n\t->rrel_offlaner_dota: {};'.format(player_idtf)
        if player['pos'] == "4":
            roster += '\n\t->rrel_semi_support_dota: {};'.format(player_idtf)
        if player['pos'] == "5":
            roster += '\n\t->rrel_full_support_dota: {};'.format(player_idtf)

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

