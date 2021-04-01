import click
from classes import Validations, AvgPrice

@click.group()
def main():
    pass

@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m"]))
@click.option('--coin', required=False, default='btc-bitcoin')
def average(start_date, end_date, coin):
    Validations.date_validation('average', start_date, end_date)
    Validations.coin_validation(coin)
    avg_price = AvgPrice(str(start_date)[:7], str(end_date)[:7], coin)
    avg_price.avg_per_month()


@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--coin', required=False, default='btc-bitcoin')
def increase(start_date, end_date, coin):
    Validations.date_validation('increase', start_date, end_date)
    Validations.coin_validation(coin)
    click.echo(f"TO jest opcja INC dla dat {start_date.strftime('%Y-%m-%d')} i {end_date.strftime('%Y-%m-%d')}")

@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--format', required=True) # csv, json
@click.option('--file', required=True)
@click.option('--coin', required=False, default='btc-bitcoin')
def export(start_date, end_date, format, file, coin):
    Validations.date_validation('export', start_date, end_date)
    Validations.format_validation(format)
    Validations.file_validation(format, file)
    Validations.coin_validation(coin)
    click.echo(f"TO jest opcja INC dla dat {start_date.strftime('%Y-%m-%d')} i {end_date.strftime('%Y-%m-%d')} oraz formatu {format} i pliku {file}")

if __name__ == '__main__':
    main()