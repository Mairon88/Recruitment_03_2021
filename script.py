import click
from classes import Validations, AvgPrice, ConsecutiveIncrease, ExportToCSVorJSON


@click.group()
def main():
    pass

@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m"]))
@click.option('--coin', required=False, default='btc-bitcoin')
def average_price_by_month(start_date, end_date, coin):
    Validations.date_validation('average-price-by-month', start_date, end_date)
    Validations.coin_validation(coin)
    start_date = str(start_date)[:7]
    end_date = str(end_date)[:7]
    avg_price = AvgPrice(start_date, end_date, coin)
    avg_price.avg_per_month()


@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--coin', required=False, default='btc-bitcoin')
def consecutive_increase(start_date, end_date, coin):
    Validations.date_validation('consecutive-increase', start_date, end_date)
    Validations.coin_validation(coin)
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    longest_inc = ConsecutiveIncrease(start_date, end_date, coin)
    longest_inc.longest_increase()


@main.command()
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--format', required=True)
@click.option('--file', required=True)
@click.option('--coin', required=False, default='btc-bitcoin')
def export(start_date, end_date, format, file, coin):
    Validations.date_validation('export', start_date, end_date)
    Validations.format_validation(format)
    Validations.file_validation(format, file)
    Validations.coin_validation(coin)
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    export_to_file = ExportToCSVorJSON(start_date, end_date, format, file, coin)
    export_to_file.export_to_file()


if __name__ == '__main__':
    main()
