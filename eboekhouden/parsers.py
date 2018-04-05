import re
import io

import pandas as pd
from bs4 import BeautifulSoup


def parse_removal_ids(html_table):
    """
    Parse IDs used for removal
    Args:
        html_table (Tag): BeautifulSoup html table element

    Returns:
        list: list of removal_ids
    """
    remove_ids = []
    for tr in html_table.find_all('tr'):
         try:
             href = tr.find('a')['href']
             match = re.search('\d{7,}', href)
             if match:
                 remove_ids.append(int(match.group()))
         except TypeError or IndexError:
             pass
    return remove_ids


def parse_hours(raw):
    """
    Parse hours from eboekhouden overview

    Args:
        raw (str): raw html

    Returns:
        DataFrame: Hours
    """
    soup = BeautifulSoup(raw, 'lxml')
    html_table = soup.find_all('table')[15]
    df = pd.read_html(io.StringIO(str(html_table)), header=0)[0]

    if len(df) == 0:
        return pd.DataFrame(columns=['Datum', 'Weekdag', 'Project', 'Activiteit', 'Opmerkingen', 'Aantal uren'])

    df['Date'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y').dt.date
    df['Weekdag'] = df['Date'].dt.strftime('%A')
    df = df.fillna('')
    df['Aantal uren'] = df['Aantal uren'] / 100
    df = df.drop(df.index[[-1]])  # drop total row
    remove_ids = parse_removal_ids(html_table)
    df['id'] = remove_ids
    df = df.drop(df.columns[0:2], axis=1)
    df = df.set_index('id')

    return df[['Datum', 'Weekdag', 'Project', 'Activiteit', 'Opmerkingen', 'Aantal uren']]


def get_selected(option):
    try:
        if option['selected'] == '':
            return True
    except KeyError:
        return False


def parse_projects(raw):
    """
    Parse the list of projects on eboekhouden overview

    Args:
        raw (str): raw html

    Returns:
        list: list of project dictionaries
    """

    soup = BeautifulSoup(raw, 'lxml')

    projects_select = soup.find_all('select')[0]

    projects = []
    for option in projects_select.find_all('option'):
        project = {
        'id': int(option['value']),
        'name': option.text,
        'selected': get_selected(option)
        }
        projects.append(project)

    return projects


def parse_activities(raw):
    """
    Parse the list of activities on eboekhouden overview

    Args:
        raw (str): raw html

    Returns:
        list: list of activities dictionaries
    """

    soup = BeautifulSoup(raw, 'lxml')

    activities_select = soup.find_all('select')[1]
    activities = []
    for option in activities_select.find_all('option'):
        activity = {
        'id': int(option['value']),
        'name': option.text,
        'selected': get_selected(option)
        }
        activities.append(activity)

    return activities


def parse_export(raw):
    """
    Parse the exports on eboekhouden overview

    Args:
        raw (str): raw html

    Returns:
        str: url to export pdf
    """

    soup = BeautifulSoup(raw, 'lxml')

    results = {}
    for a in soup.select('a'):
        if 'export' in a['href'].lower():
            filetype = a.select_one('img')['title'].split()[-1]
            results[filetype] = a['href']

     # if a['alt'].contains('Export')]
    return results['PDF']
