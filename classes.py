import requests
import pandas as pd
from calendar import monthrange
import os.path
import sys
import datetime
import pickle
import click

# ========================== VALIDATIONS ============================


class Validations(object):

    @staticmethod
    def date_validation(command, start_date, end_date):
        try:
            if command == ('consecutive-increase' or 'export'):
                assert start_date.strftime('%Y-%m-%d') <= end_date.strftime('%Y-%m-%d')
            else:
                assert start_date.strftime('%Y-%m') <= end_date.strftime('%Y-%m')
        except AssertionError:
            click.secho(f"Data początkowa powinna być równa lub wcześniejsza od końcowej", fg='red')
            sys.exit()

        try:
            if command == ('consecutive-increase' or 'export'):
                today = datetime.date.today().strftime('%Y-%m-%d')
                assert start_date.strftime('%Y-%m-%d') <= today and end_date.strftime('%Y-%m-%d') <= today
            else:
                today = datetime.date.today().strftime('%Y-%m')
                assert start_date.strftime('%Y-%m') <= today and end_date.strftime('%Y-%m') <= today
        except AssertionError:
            click.secho(f"Data początkowa i końcowa nie powinny być późniejsze od dzisiejszej daty", fg='red')
            sys.exit()

    @staticmethod
    def format_validation(formats):
        try:
            assert formats == 'csv' or formats == 'json'
        except AssertionError:
            click.secho(f"błędny format, proszę wpisać 'csv' lub 'json", fg='red')
            sys.exit()

    @staticmethod
    def file_validation(formats, file):
        try:
            assert file.endswith(f'.{formats}')
        except AssertionError:
            click.secho(f"błędny format pliku do zapisu", fg='red')
            sys.exit()
        try:
            chars = ['#', '%', '&', '*', ':', '?', '/', '|', '\\']
            for char in chars:
                assert char not in file
        except AssertionError:
            click.secho(f"Podana nazwa zawiera niedozwolony znak/i z podanych w liście: '#','%','&','*',':','?','/','|'"
                        f",'\\'", fg='red')
            sys.exit()

    @staticmethod
    def coin_validation(coin):
        try:
            if not os.path.isfile('coins'):
                url = "https://api.coinpaprika.com/v1/coins"
                res = requests.get(url)
                data = res.json()
                list_of_coins = [i['id'] for i in data]
                with open('coins', 'wb') as file:
                    pickle.dump(list_of_coins, file)

            with open('coins', 'rb') as file:
                pickle_coins = pickle.load(file)

            assert coin in pickle_coins
        except Exception:
            click.echo(click.style(f"Błąd podczas próby połączenia się z API lub błędna nazwa kryptowaluty", fg='red'))
            sys.exit()


# ==============================DATA, AVERAGE, INCREASE, EXPORT =================================
class AvgPrice(object):
    def __init__(self, start_point, end_point, coin):
        self.start_point = start_point
        self.end_point = end_point
        self.coin = coin

    def get_data_to_calculate(self):
        get_data = GetHistoricalOHLC(str(self.start_point), str(self.end_point), self.coin, 'avg')
        get_data.check_params()

    def prepare_data(self):
        self.get_data_to_calculate()

        try:
            with open(f'caching_mechanism/caching_mechanism_data_avg', 'rb') as file:
                data = pickle.load(file)

            data_dict = {}
            n = 1
            for i in data:
                data_dict.setdefault(n, i)
                n += 1
            return data_dict
        except:
            click.echo(click.style(("Brak pliku o podanej nazwie"), fg='red'))
            sys.exit()


    def avg_per_month(self):
        def shorten_data(data):
            short_data = data[:7]
            return short_data
        prepared_data = self.prepare_data()

        df = pd.DataFrame.from_dict(prepared_data, orient='index', columns=['time_close', 'close'])
        df['time_close'] = df['time_close'].apply(shorten_data)
        groups = df.groupby(by='time_close')
        month_list = list(groups.size().index)
        price_list = []
        for month in month_list:
            avg_for_this_month = df['time_close'] == month
            price_list.append(round(float(df.where(avg_for_this_month).dropna(how='all').mean()), 2))
        new_df = pd.DataFrame({'Date': month_list, 'Average price ($)': price_list})
        click.echo(click.style((new_df.to_string(index=False)), fg='green'))
        today = datetime.date.today()
        days_in_month = monthrange(int(self.end_point[:4]), int(self.end_point[5:8]))[1]
        # if str(self.end_point)+f"-{days_in_month}" > str(today)[:10] and :
        #     click.echo(click.style(("W związku z tym, że aktualny miesiąc jeszcze się nie skończył to wartość średnia "
        #                            "ostatniego miesiąca liczona jest "
        #                             "od początku miesiąca do aktualnego dnia i godziny"), fg='yellow'))


class ConsecutiveIncrease(object):
    def __init__(self, start_point, end_point, coin):
        self.start_point = start_point
        self.end_point = end_point
        self.coin = coin

    def get_data_to_calculate(self):
        get_data = GetHistoricalOHLC(self.start_point, self.end_point, self.coin, 'inc')
        get_data.check_params()

    def prepare_data(self):
        self.get_data_to_calculate()

        with open(f'caching_mechanism/caching_mechanism_data_inc', 'rb') as file:
            data = pickle.load(file)

        data_dict = {}
        n = 1
        for i in data:
            data_dict.setdefault(n, i)
            n += 1
        return data_dict

    def longest_increase(self):
        def shorten_data(data):
            short_data = data[:10]
            return short_data

        prepared_data = self.prepare_data()
        pairs_date_price = []
        temporary_data = []

        df = pd.DataFrame.from_dict(prepared_data, orient='index', columns=['time_close', 'close'])
        df['time_close'] = df['time_close'].apply(shorten_data)

        for index, row in df.iterrows():
            if temporary_data:
                if row[1] > temporary_data[-1][1]:
                    temporary_data.append((row[0], row[1]))
                else:
                    if len(pairs_date_price) < len(temporary_data):
                        pairs_date_price = temporary_data.copy()
                        temporary_data.clear()
                        temporary_data.append((row[0], row[1]))

                    else:
                        temporary_data.clear()
                        temporary_data.append((row[0], row[1]))

            else:
                temporary_data.append((row[0], row[1]))

        click.echo(click.style(f"Longest consecutive period was from {pairs_date_price[0][0]} to "
                               f"{pairs_date_price[-1][0]} with increase of $"
                               f"{round(pairs_date_price[-1][1]-pairs_date_price[0][1],2)}", fg='green'))


class ExportToCSVorJSON(object):
    def __init__(self, start_point, end_point, formats, file, coin):
        self.start_point = start_point
        self.end_point = end_point
        self.formats = formats
        self.file = file
        self.coin = coin

    def get_data_to_calculate(self):
        get_data = GetHistoricalOHLC(self.start_point, self.end_point, self.coin, 'exp')
        get_data.check_params()

    def prepare_data(self):
        self.get_data_to_calculate()

        with open(f'caching_mechanism/caching_mechanism_data_exp', 'rb') as file:
            data = pickle.load(file)

        data_dict = {}
        n = 1
        for i in data:
            data_dict.setdefault(n, i)
            n += 1

        return data_dict

    def export_to_file(self):
        def shorten_data(data):
            short_data = data[:10]
            return short_data


        prepared_data = self.prepare_data()
        df = pd.DataFrame.from_dict(prepared_data, orient='index', columns=['time_close', 'close'])
        df['time_close'] = df['time_close'].apply(shorten_data)
        df['close'] = df['close'].round(2)
        df = df.rename(columns={'time_close': 'Date', 'close': 'Price'})
        if self.formats == 'json':
            df.to_json(self.file, orient='records')
        elif self.formats == 'csv':
            df.to_csv(self.file, sep=',', index=False)
        click.echo(click.style(f'Zapisano dane do pliku: {self.file}', fg='green'))


class GetHistoricalOHLC(object):
    def __init__(self, start_point, end_point, coin, option):
        self.option = option
        if len(start_point) == 7:
            self.start_point = start_point+"-01"
        elif len(start_point) == 10:
            self.start_point = start_point

        if len(end_point) == 7:
            today = datetime.date.today()
            if end_point[5:7] == str(today)[5:7]:
                self.end_point = end_point + f"-{str(today)[8:]}"
            else:
                days_in_month = monthrange(int(end_point[:4]), int(end_point[5:8]))[1]
                self.end_point = end_point + f"-{days_in_month}"
        elif len(end_point) == 10:
            self.end_point = end_point
        self.coin = coin

    # POBIERANIE DANYCH Z API
    def get_data_from_api(self):
        try:
            url = f"https://api.coinpaprika.com/v1/coins/{self.coin}/ohlcv/" \
                  f"historical?start={self.start_point}&end={self.end_point}"
            res = requests.get(url)
            data = res.json()
            print("DATA Z API")

        except Exception:
            click.echo(click.style(f"Błąd podczas próby połączenia się z API", fg='red'))
            sys.exit()


        self.caching_mechanism(data)
        self.save_params()
        return data

    # ZAPIS PARAMETROW DO PLIKU
    def save_params(self):
        with open(f'caching_mechanism/caching_mechanism_param_{self.option}', 'wb') as file:
            data = [self.start_point, self.end_point, self.coin]
            pickle.dump(data, file)
            # file.write(self.start_point+"\n")
            # file.write(self.end_point + "\n")
            # file.write(self.coin)

    # METODA SPRAWDZAJACA CZY PARAMETRY POKRYWAJA SIE Z POPRZEDNIM POBRANIEM DANYCH
    def check_params(self):

        if os.path.isfile(f'caching_mechanism/caching_mechanism_param_{self.option}') and os.path.isfile(f'caching_mechanism/caching_mechanism_data_{self.option}'):
            with open(f'caching_mechanism/caching_mechanism_param_{self.option}', 'rb') as file:
                data = pickle.load(file)
                param_line_1 = data[0]
                param_line_2 = data[1]
                param_line_3 = data[2]

                # JESLI PODANE PARAMETRY POKRYWAJA SIE Z POPRZEDNIMI ZAPISANYMI W PLIKU TO DANE BEDA POBRANE Z PLIKU
                if not (param_line_1 == self.start_point and param_line_2 == self.end_point and
                        param_line_3 == self.coin):
                    self.get_data_from_api()
                    print("Zapisujemy nowe parametry i odpalamy api")

                # W INNYM PRZYPADKU ZOSTANA ZAPISANE NOWE PARAMETRY A DANE ZOSTANA POBRANE Z API
                else:
                    print("Powtórzone parametry, mozna zczytywac z pliku dane")

        # JESLI BEDZIE BRAK ZAPISANYCH PARAMETROW LUB PLIKU  Z DANYMI TO ZOSTANA ZAPISANE NOWE PARAMETRY A DANE
        # ZOSTANA POBRANE Z API
        else:
            self.get_data_from_api()

    # KONWERTOWANIE DANYCH DO CSV I ZAPIS DO PLIKU W CELU  LEPSZEJ OBROBKI W PANDASIE
    def caching_mechanism(self, data):
        if not os.path.exists('caching_mechanism'):
            os.makedirs('caching_mechanism')
        try:

            with open(f'caching_mechanism/caching_mechanism_data_{self.option}', 'wb') as file:
                pickle.dump(data, file)
        except IOError:
            print("Coś nie tak z konwertowaniem")
