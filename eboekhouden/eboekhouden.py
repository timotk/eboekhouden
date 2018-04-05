import requests
import pandas as pd

from eboekhouden.parsers import parse_hours, parse_projects, parse_activities, parse_export


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

    def add_hours(self, hours, date, comment='', project_id=None, activity_id=None):
        if not project_id:
            project_id = self.get_selected(self.projects)['id']
        if not activity_id:
            activity_id = self.get_selected(self.activities)['id']

        payload = {
            'SelActiviteit': activity_id,
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

    def get_pdf_export(self, filename):
        params = {'dummy': 1,
                  'ACTION': 'LIST'}
        r = self.session.get(self.base_url + 'uren_ov.asp', params=params)
        url = self.base_url + parse_export(r.content)

        response = self.session.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True

    @property
    def projects(self):
        try:
            return self._projects
        except AttributeError:
            r = self.session.get(self.base_url + 'uren.asp?ACTION=ADDNEW')
            self._projects = parse_projects(r.content)
            return self._projects

    @property
    def activities(self):
        try:
            return self._activities
        except AttributeError:
            r = self.session.get(self.base_url + 'uren.asp?ACTION=ADDNEW')
            self._activities = parse_activities(r.content)
            return self._activities

    def get_selected(self, options):
        return [option for option in options if option['selected']][0]
