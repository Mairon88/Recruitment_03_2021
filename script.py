import click
from classes import Validations

@click.group()
def main():
    pass

@main.command()
@click.option('--start-date', '-s', required=True, type=click.DateTime(formats=["%Y-%m"]))
@click.option('--end-date', '-e', required=True, type=click.DateTime(formats=["%Y-%m"]))
def average(start_date, end_date):
    Validations.date_validation('average', start_date, end_date)
    click.echo(f"TO jest opcja AVG dla dat {start_date.strftime('%Y-%m')} i {end_date.strftime('%Y-%m')}")

@main.command()
@click.option('--start-date', '-s', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', '-e', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
def increase(start_date, end_date):
    Validations.date_validation('increase', start_date, end_date)
    click.echo(f"TO jest opcja INC dla dat {start_date.strftime('%Y-%m-%d')} i {end_date.strftime('%Y-%m-%d')}")

@main.command()
@click.option('--start-date', '-s', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', '-e', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--format', '-fo', required=True) # csv, json
@click.option('--file', '-fi', required=True)
def export(start_date, end_date, format, file):
    Validations.date_validation('export', start_date, end_date)
    Validations.format_validation(format)
    Validations.validation_file(format, file)
    click.echo(f"TO jest opcja INC dla dat {start_date.strftime('%Y-%m-%d')} i {end_date.strftime('%Y-%m-%d')} oraz formatu {format} i pliku {file}")

if __name__ == '__main__':
    main()