import click





@click.group()
def main():
    pass

@main.command()
@click.option('--start-date', '-s', required=True)
@click.option('--end-date', '-e', required=True)
def average(start_date, end_date):
    click.echo(f"TO jest opcja AVG dla dat {start_date} i {end_date}")

@main.command()
@click.option('--start-date', '-s', required=True)
@click.option('--end-date', '-e', required=True)
def increase(start_date, end_date):
    click.echo(f"TO jest opcja INC dla dat {start_date} i {end_date}")

@main.command()
@click.option('--start-date', '-s', required=True)
@click.option('--end-date', '-e', required=True)
@click.option('--format', '-fo', required=True) # csv, json
@click.option('--file', '-fi', required=True)
def export(start_date, end_date, format, file):
    click.echo(f"TO jest opcja INC dla dat {start_date} i {end_date} oraz formatu {format} i pliku {file}")

if __name__ == '__main__':
    main()