import requests
import pandas as pd

from eboekhouden.parsers import parse_hours, parse_projects


class LoginFailedException(Exception):
    """Failed to login"""


class Eboekhouden:
    """Eboekhouden wrapper"""

    def __init__(self, email, password):
        self.base_url = 'https://secure2.e-boekhouden.nl/bh/'
        self.session = self.login(email, password)

    def login(self, email, password):
        s = requests.Session()
        s.headers.update({'User-Agent': 'Mozilla/5.0'})

        payload = {'txtEmail': email, 'txtWachtwoord': password}
        r = s.post(self.base_url + 'inloggen.asp?login=1',
                   data=payload)

        if not 'U bent nu ingelogd' in r.text:
            raise LoginFailedException()

        return s

    def get_hours(self):
        params = {'dummy': 1,
                  'ACTION': 'LIST'}
        r = self.session.get(self.base_url + 'uren_ov.asp', params=params)
        return parse_hours(r.content)

    def add_hours(self, hours, date, comment='', project_id=None, activiteit=14458):
        if not project_id:
            project_id = self.get_selected_project()['id']

        payload = {
            'SelActiviteit': activiteit,
            'SelProject': project_id,
            'submit1': 'Opslaan',
            'txtAantal': hours,
            'txtDatum': date.strftime('%d-%m-%Y'),
            'txtOpmerkingen': comment
        }

        r = self.session.post(self.base_url + 'uren.asp?ACTION=ADDNEW&SAVE=1&ID=&POPUP=&RETURNURL=',
                              data=payload)

    def remove_hours(self, hours_id):
        params = {
            'ACTION': 'DELETE',
            'ID': hours_id
        }
        r = self.session.get(self.base_url + 'uren_ov.asp',
                         params=params)

    @property
    def projects(self):
        try:
            return self._projects
        except AttributeError:
            r = self.session.get(self.base_url + 'uren.asp?ACTION=ADDNEW')
            self._projects = parse_projects(r.content)
            return self._projects

    def get_selected_project(self):
        return [p for p in self.projects if p['selected']][0]
