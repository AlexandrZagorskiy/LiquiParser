from json import JSONDecodeError

from liquipediapy import dota
import json
import time
import os.path
from liquipediapy.exceptions import RequestsException
from getpass import getpass
from string import Template

def parse_teams(teams):
    for team in teams:
        if os.path.isfile('teams/{}.json'.format(team)):            
            print ("Team {} exist, update? [yes/any]".format(team))
            ans = getpass(prompt="")
            if ans == "y" or ans == "yes":
                _create_new_teams([team])
            else:
                continue

        else:
            _create_new_teams([team])

def _create_new_teams(teams, file_type="scs"):

    dota_obj = dota("Bot for creating knowledge base for OSTIS app (https://github.com/ostis-apps; alexandr_zagorskiy@mail.ru")
    
    for team in teams:
        team_info = dota_obj.get_team_info(team, True)

        try:
            location = team_info['info']['location']
        except KeyError:
            location = []
        
        try:
            created = team_info['info']['created']
        except KeyError:
            created = []

        try:
            sponsor = team_info['info']['sponsor']
        except KeyError:
            sponsor = []

        try:
            manager = team_info['info']['manager']
        except KeyError:
            manager = []

        try:
            director = team_info['info']['director']
        except KeyError:
            director = []

        try:
            coach = team_info['info']['coach']
        except KeyError:
            coach = []
        
        try:
            team_roster = [{"nickname": player['ID'], "pos": player['Position']} for player in team_info['team_roster']]
        except KeyError:
            team_roster = [{"nickname": player['ID'], "pos": ""} for player in team_info['team_roster']]
            
        if file_type == "json":
            team_data = {
                'id': team,
                "location": location,
                'coach': coach,
                'director': director,
                'manager': manager,
                'sponsor': sponsor,
                'created': created,
                'roster': team_roster,
            }
            with open('teams/{}.json'.format(team), 'w') as f:
                f.write(json.dumps(team_data, ensure_ascii=False))
            print("create {} team".format(team))

        elif file_type == "scs":
            format_location = location
            format_sponsors = sponsor
            format_roster = team_roster

            src = Template(open('templates/team.scs').read())
            team_data = {
                'team_sys_idtf': "team_{}_dota".format(team.lower().replace(" ", "_")),
                'team_main_idtf': team,
                'location': format_location,
                'directror': director,
                'manager': manager,
                'coach': coach,
                'created': created.replace("-", "_"),
                'created_idtf': created,
                'created_day': created[-2:],
                'created_month': created[5:-3],
                'created_year': created[:4],
                'sponsors': format_sponsors,
                'roster': format_roster,
            }
            result = src.substitute(team_data)
            with open('teams/{}.scs'.format(team), 'w') as f:
                f.write(result)
            print("create {} team".format(team))
