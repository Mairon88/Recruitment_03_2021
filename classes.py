import requests
import pandas as pd
from calendar import monthrange
import os.path
import sys
import datetime
import pickle
import click

class Validations():
    @staticmethod
    def date_validation(command, start_date, end_date):
        try:
            if command == ('increase' or 'export'):
                assert start_date.strftime('%Y-%m-%d') <= end_date.strftime('%Y-%m-%d')
            else:
                assert start_date.strftime('%Y-%m') <= end_date.strftime('%Y-%m')
        except:
            click.secho(
                (f"Data początkowa powinna być równa lub wcześniejsza od końcowej"),
                fg='red')
            sys.exit()
        try:
            if command == ('increase' or 'export'):
                today = datetime.date.today().strftime('%Y-%m-%d')
                assert start_date.strftime('%Y-%m-%d') <= today and end_date.strftime('%Y-%m-%d') <= today
            else:
                today = datetime.date.today().strftime('%Y-%m')
                assert start_date.strftime('%Y-%m') <= today and end_date.strftime('%Y-%m') <= today
        except:
            click.secho(
                (f"Data początkowa i końcowa nie powinny być późniejsze od dzisiejszej daty"),
                fg='red')
            sys.exit()

    @staticmethod
    def format_validation(format):
            try:
                assert format == 'csv' or format == 'json'
            except BaseException:
                click.secho((f"błędny format, proszę wpisać 'csv' lub 'json"), fg='red')
                sys.exit()

    @staticmethod
    def validation_file(format, file):
        try:
            assert file.endswith(f'.{format}')
        except BaseException:
            click.secho((f"błędny format pliku do zapisu"), fg='red')
            sys.exit()
        try:
            chars = ['#','%','&','*',':','?','/','|','\\']
            for char in chars:
                assert char not in file
        except:
            click.secho((f"Podana nazwa zawiera niedozwolony znak/i z podanych w liście: '<','>','#','%','&','*',':','?','/','|','\\'"), fg='red')
            sys.exit()
