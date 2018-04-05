import click
import keyring
import dateparser
from tabulate import tabulate

from eboekhouden import eboekhouden
from eboekhouden.stats import hours_summary, hours_per_project


SERVICE_ID = 'eboekhouden'


def get_keyring():
    username = keyring.get_password(SERVICE_ID, "username")
    password = keyring.get_password(SERVICE_ID, "password")

    if not username or not password:
        raise Exception('No credentials found in keyring')

    return username, password


def set_keyring(username, password):
    keyring.set_password(SERVICE_ID, "username", username)
    keyring.set_password(SERVICE_ID, "password", password)
    click.echo('Saved credentials to system keyring')


def login_required(func):
    def wrap_function(*args, **kwargs):
        try:
            ebh = eboekhouden.Eboekhouden(*get_keyring())
            return func(ebh, *args, **kwargs)
        except eboekhouden.LoginFailedException as e:
            click.echo(e)
            ebh = setup()
            return func(ebh, *args, **kwargs)
    return wrap_function


@click.group()
@click.pass_context
def cli(ctx):
    """eboekhouden.nl from the command line"""
    pass


@cli.command()
@click.pass_context
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def setup(ctx, username, password):
    """Store credentials in system keyring."""
    try:
        ebh = eboekhouden.Eboekhouden(username, password)
    except eboekhouden.LoginFailedException:
        click.echo('Incorrect username or password!')
        click.invoke(setup())
    set_keyring(username, password)


@cli.command(name='list', help='Show hours for this month.')
@login_required
def list_hours(ebh):
    df = ebh.get_hours()
    click.echo('Hours:')
    click.echo(tabulate(df, headers='keys', tablefmt='psql'))

    click.echo('Hours stats:')
    click.echo(tabulate(hours_summary(df), tablefmt='psql'))

    click.echo('Hours per project:')
    click.echo(tabulate(hours_per_project(df), tablefmt='psql'))


@cli.command(name='projects', help='List available projects.')
@login_required
def projects(ebh):
    click.echo(tabulate(ebh.projects, headers='keys', tablefmt='psql'))


@cli.command(name='activities', help='List available activities.')
@login_required
def projects(ebh):
    click.echo(tabulate(ebh.activities, headers='keys', tablefmt='psql'))


@cli.command(name='add', help='Add hours for a given date. Defaults to today.')
@click.argument('hours', type=float)
@click.argument('date', default='today')
@click.option('--project_id', type=int, default=None)
@click.option('--activity_id', type=int, default=None)
@login_required
def add(ebh, hours, date, project_id, activity_id):
    if not project_id:
        project = ebh.get_selected(ebh.projects)
    else:
        project = [p for p in ebh.projects if p['id'] == project_id][0]

    date = dateparser.parse(date).date()
    click.echo('Adding {} hours for {} to "{}"...'.format(hours, date, project['name']))
    ebh.add_hours(hours, date, project_id=project_id, activity_id=activity_id)


@cli.command(name='remove', help='Remove hours for a given id.')
@click.argument('hours_id', type=int)
@login_required
def remove(ebh, hours_id):
    df = ebh.get_hours()
    try:
        item = df.loc[[hours_id]].iloc[0]
    except KeyError as e:
        click.echo("Error: Could not find these hours_id in this month's hours")
        raise SystemExit

    if click.confirm('Are you sure you want to remove {} hours for "{}" on {}?'\
                        .format(item['Aantal uren'],
                                item['Project'],
                                item['Datum'])):
        click.echo('Removing {} hours for "{}" on {}'.format(item['Aantal uren'],
                                                             item['Project'],
                                                             item['Datum']))
        ebh.remove_hours(hours_id)


@cli.command(name='export', help='Export PDF for this months hours')
@click.argument('filename')
@login_required
def export(ebh, filename):
    click.echo('Getting pdf...')
    result = ebh.get_pdf_export(filename)
    if result:
        click.echo('Downloaded pdf export to {}'.format(filename))
    else:
        click.echo('Could not download file')
if __name__ == '__main__':
    cli()
