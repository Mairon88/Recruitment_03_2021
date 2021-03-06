from click.testing import CliRunner
from script import main
from classes import AvgPrice


def test_avarage():
    runner = CliRunner()
    result = runner.invoke(main, ['average-price-by-month', '--start-date=2020-01', '--end-date=2020-05'])
    assert result.exit_code == 0


def test_increase():
    runner = CliRunner()
    result = runner.invoke(main, ['consecutive-increase', '--start-date=2020-04-01', '--end-date=2020-05-02'])
    assert result.exit_code == 0


def test_export_to_csv():
    runner = CliRunner()
    result = runner.invoke(main, ['export', '--start-date=2020-01-01', '--end-date=2020-05-01', '--format=csv',
                                  '--file=myfile.csv'])
    assert result.exit_code == 0


def test_export_to_json():
    runner = CliRunner()
    result = runner.invoke(main, ['export', '--start-date=2020-01-01', '--end-date=2020-05-01', '--format=json',
                                  '--file=test_file.json'])
    assert result.exit_code == 0


def test_format_is_not_json_or_csv():
    runner = CliRunner()
    result = runner.invoke(main, ['export', '--start-date=2020-01-01', '--end-date=2020-05-01', '--format=bin',
                                  '--file=test_file.csv'])
    assert result.exit_code == 0
    assert result.output == "Wrong format, please enter 'csv' or 'json\n"


def test_format_date():
    runner = CliRunner()
    result1 = runner.invoke(main, ['average-price-by-month', '--start-date=2020-005', '--end-date=2020-05'])
    result2 = runner.invoke(main, ['consecutive-increase', '--start-date=2020-06-0z', '--end-date=2020-05-01'])
    result3 = runner.invoke(main, ['export', '--start-date=2020', '--end-date=2020-05-01', '--format=csv',
                                   '--file=myfile.csv'])
    assert result1.exit_code == 2
    assert result2.exit_code == 2
    assert result3.exit_code == 2


def test_start_data_is_before_or_equal_end_data():
    runner = CliRunner()
    result1 = runner.invoke(main, ['average-price-by-month', '--start-date=2020-06', '--end-date=2020-05'])
    result2 = runner.invoke(main, ['consecutive-increase', '--start-date=2020-06-01', '--end-date=2020-05-01'])
    result3 = runner.invoke(main, ['export', '--start-date=2020-06-01', '--end-date=2020-05-01', '--format=csv',
                                   '--file=myfile.csv'])
    assert result1.exit_code == 0
    assert result1.output == "Start date should be equal or earlier than the end date\n"
    assert result2.exit_code == 0
    assert result2.output == "Start date should be equal or earlier than the end date\n"
    assert result3.exit_code == 0
    assert result3.output == "Start date should be equal or earlier than the end date\n"


def test_file_name_and_format():
    runner = CliRunner()
    result = runner.invoke(main, ['export', '--start-date=2020-01-01', '--end-date=2020-05-01', '--format=csv',
                                  '--file=myfi/le.csv'])
    assert result.exit_code == 0
    assert result.output == "The given name contains an illegal character from those given in the list: " \
                            "'#','%','&','*',':','?','/','|','\\'\n"


def test_avg_price_initialization():
    avg_price = AvgPrice('2020-01', '2020-05', 'btc-bitcoin')
    assert isinstance(avg_price, AvgPrice)
    assert avg_price.start_point == "2020-01"
    assert avg_price.end_point == "2020-05"
    assert avg_price.coin == 'btc-bitcoin'
