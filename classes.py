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
            click.secho(f"Start date should be equal or earlier than the end date", fg='red')
            sys.exit()

        try:
            if command == ('consecutive-increase' or 'export'):
                today = datetime.date.today().strftime('%Y-%m-%d')
                assert start_date.strftime('%Y-%m-%d') <= today and end_date.strftime('%Y-%m-%d') <= today
            else:
                today = datetime.date.today().strftime('%Y-%m')
                assert start_date.strftime('%Y-%m') <= today and end_date.strftime('%Y-%m') <= today
        except AssertionError:
            click.secho(f"Start and end dates should not be later than today's date", fg='red')
            sys.exit()

    @staticmethod
    def format_validation(formats):
        try:
            assert formats == 'csv' or formats == 'json'
        except AssertionError:
            click.secho(f"Wrong format, please enter 'csv' or 'json", fg='red')
            sys.exit()

    @staticmethod
    def file_validation(formats, file):
        try:
            assert file.endswith(f'.{formats}')
        except AssertionError:
            click.secho(f"Wrong file format for writing", fg='red')
            sys.exit()
        try:
            chars = ['#', '%', '&', '*', ':', '?', '/', '|', '\\']
            for char in chars:
                assert char not in file
        except AssertionError:
            click.secho(f"The given name contains an illegal character from those given in the list:"
                        f" '#','%','&','*',':','?','/','|'"
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
            click.echo(click.style(f"Error while trying to connect to API or wrong cryptocurrency name", fg='red'))
            sys.exit()


# ==============================DATA, AVERAGE, INCREASE, EXPORT =================================

# The class responsible for calculating the monthly average values of the cryptocurrency
class AvgPrice(object):
    def __init__(self, start_point, end_point, coin):
        self.start_point = start_point
        self.end_point = end_point
        self.coin = coin

    # A method that gets data to be processed through an object of GetHistoricalOHLC class
    # and checking if the entered parameters are the same as those previously specified
    def get_data_to_calculate(self):
        get_data = GetHistoricalOHLC(str(self.start_point), str(self.end_point), self.coin, 'avg')
        get_data.check_params()
        return get_data.prepare_data()

    # The method calculating the average value of the currency for a given month
    def avg_per_month(self):

        # The function shortens the received date from the API to a year and a month
        def shorten_data(date):
            short_date = date[:7]
            return short_date

        # Assignment of data retrieved from api in the form of a dictionary to a variable
        prepared_data = self.get_data_to_calculate()

        # Use of pandas to improve calculation of mean values and display of results
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


class ConsecutiveIncrease(object):
    def __init__(self, start_point, end_point, coin):
        self.start_point = start_point
        self.end_point = end_point
        self.coin = coin

    def get_data_to_calculate(self):
        get_data = GetHistoricalOHLC(self.start_point, self.end_point, self.coin, 'inc')
        get_data.check_params()
        return get_data.prepare_data()

    def longest_increase(self):
        def shorten_data(data):
            short_data = data[:10]
            return short_data

        prepared_data = self.get_data_to_calculate()
        pairs_date_price = []
        temporary_data = []

        df = pd.DataFrame.from_dict(prepared_data, orient='index', columns=['time_close', 'close'])
        df['time_close'] = df['time_close'].apply(shorten_data)

        # row[0] - dates, row[1] - price
        for index, row in df.iterrows():

            if temporary_data:
                # If the value is greater than the last of the temporary data, it will add it to the temporary data
                if row[1] > temporary_data[-1][1]:
                    temporary_data.append((row[0], row[1]))

                else:
                    # If the value is less than or equal to the last of the provisional data, the
                    # worklist length and the correct one are checked.
                    if len(pairs_date_price) < len(temporary_data):
                        # If the correct list is shorter than the working list, its contents will be
                        # copied to the correct list and the working list will be cleared and completed with
                        # the new value
                        pairs_date_price = temporary_data.copy()
                        temporary_data.clear()
                        temporary_data.append((row[0], row[1]))

                    else:
                        # If the length of the valid list is greater than the working list, it does not copy the
                        # contents of the working list to the correct one
                        temporary_data.clear()
                        temporary_data.append((row[0], row[1]))

            # If the working list is mouth, it adds the first value
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
        return get_data.prepare_data()

    def export_to_file(self):
        def shorten_data(data):
            short_data = data[:10]
            return short_data

        prepared_data = self.get_data_to_calculate()
        df = pd.DataFrame.from_dict(prepared_data, orient='index', columns=['time_close', 'close'])
        df['time_close'] = df['time_close'].apply(shorten_data)
        df['close'] = df['close'].round(2)
        df = df.rename(columns={'time_close': 'Date', 'close': 'Price'})
        if self.formats == 'json':
            df.to_json(self.file, orient='records')
        elif self.formats == 'csv':
            df.to_csv(self.file, sep=',', index=False)
        click.echo(click.style(f'Data has been written to a file: {self.file}', fg='blue'))


class GetHistoricalOHLC(object):
    def __init__(self, start_point, end_point, coin, option):
        self.option = option
        # Adding to the short starting date of the first day of the month
        if len(start_point) == 7:
            self.start_point = start_point+"-01"
        elif len(start_point) == 10:
            self.start_point = start_point

        # Adding to the short end date of the last day of the month
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

    def get_data_from_api(self):
        try:
            url = f"https://api.coinpaprika.com/v1/coins/{self.coin}/ohlcv/" \
                  f"historical?start={self.start_point}&end={self.end_point}"
            res = requests.get(url)
            data = res.json()

        except Exception:
            click.echo(click.style(f"Error while trying to connect to the API", fg='red'))
            sys.exit()

        self.caching_mechanism(data)
        self.save_params()
        return data

    # Saving parameters to a file
    def save_params(self):
        with open(f'caching_mechanism/caching_mechanism_param_{self.option}', 'wb') as file:
            data = [self.start_point, self.end_point, self.coin]
            pickle.dump(data, file)

    # The method checks if the parameters match the previous data download
    def check_params(self):

        if os.path.isfile(f'caching_mechanism/caching_mechanism_param_{self.option}') and \
                os.path.isfile(f'caching_mechanism/caching_mechanism_data_{self.option}'):
            with open(f'caching_mechanism/caching_mechanism_param_{self.option}', 'rb') as file:
                data = pickle.load(file)
                param_line_1 = data[0]
                param_line_2 = data[1]
                param_line_3 = data[2]

            # IF THE GIVEN PARAMETERS COVER THE PREVIOUS STORES IN THE FILE, THE DATA WILL BE DOWNLOADED FROM THE FILE
                if not (param_line_1 == self.start_point and param_line_2 == self.end_point and
                        param_line_3 == self.coin):
                    self.get_data_from_api()

            # OTHERWISE, NEW PARAMETERS WILL BE SAVED AND THE DATA WILL BE DOWNLOADED FROM API

        # IF THERE IS NO SAVED PARAMETERS OR DATA FILE, NEW PARAMETERS WILL BE SAVED AND DATA DOWNLOADED FROM API
        else:
            self.get_data_from_api()

    # Reading data from a file and converting it into a dictionary for pandas
    def prepare_data(self):
        try:
            with open(f'caching_mechanism/caching_mechanism_data_{self.option}', 'rb') as file:
                data = pickle.load(file)

            data_dict = {}
            n = 1
            for i in data:
                data_dict.setdefault(n, i)
                n += 1
            return data_dict

        except Exception:
            click.echo(click.style("There is no file with the given name"), fg='red')
            sys.exit()

    # Writing data to a file for reuse with repeated parameters
    def caching_mechanism(self, data):
        if not os.path.exists('caching_mechanism'):
            os.makedirs('caching_mechanism')
        try:

            with open(f'caching_mechanism/caching_mechanism_data_{self.option}', 'wb') as file:
                pickle.dump(data, file)
        except IOError:
            click.echo(click.style(f"Error while creates caching mechanism", fg='red'))
