from click.testing import CliRunner
from script import main

def test_avarage():
    runner = CliRunner()
    result = runner.invoke(main, ['average','--start-date=2020-01','--end-date=2020-05'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja AVG dla dat 2020-01 i 2020-05\n"

def test_increase():
    runner = CliRunner()
    result = runner.invoke(main, ['increase','--start-date=2020-04-01','--end-date=2020-05-02'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja INC dla dat 2020-04-01 i 2020-05-02\n"

def test_export_to_csv():
    runner = CliRunner()
    result = runner.invoke(main, ['export','--start-date=2020-01-01','--end-date=2020-05-01', '--format=csv', '--file=myfile.csv'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja INC dla dat 2020-01-01 i 2020-05-01 oraz formatu csv i pliku myfile.csv\n"
    assert result.output != "błędny format pliku do zapisu\n"

def test_export_to_json():
    runner = CliRunner()
    result = runner.invoke(main, ['export','--start-date=2020-01-01','--end-date=2020-05-01', '--format=json', '--file=myfile.json'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja INC dla dat 2020-01-01 i 2020-05-01 oraz formatu json i pliku myfile.json\n"
    assert result.output != "błędny format pliku do zapisu\n"

def test_format_is_not_json_or_csv():
    runner = CliRunner()
    result = runner.invoke(main, ['export','--start-date=2020-01-01','--end-date=2020-05-01', '--format=bin', '--file=myfile.csv'])
    assert result.exit_code == 0
    assert result.output == "błędny format, proszę wpisać 'csv' lub 'json\n"

def test_start_data_is_before_or_equal_end_data():
    runner = CliRunner()
    result1 = runner.invoke(main, ['average', '--start-date=2020-06', '--end-date=2020-05'])
    result2 = runner.invoke(main, ['increase', '--start-date=2020-06-01', '--end-date=2020-05-01'])
    result3 = runner.invoke(main, ['export', '--start-date=2020-06-01', '--end-date=2020-05-01', '--format=csv',
                                   '--file=myfile.csv'])
    assert result1.exit_code == 0
    assert result1.output == "Data początkowa powinna być równa lub wcześniejsza od końcowej\n"
    assert result2.exit_code == 0
    assert result2.output == "Data początkowa powinna być równa lub wcześniejsza od końcowej\n"
    assert result3.exit_code == 0
    assert result3.output == "Data początkowa powinna być równa lub wcześniejsza od końcowej\n"

def test_file_name_and_format():
    runner = CliRunner()
    result = runner.invoke(main, ['export','--start-date=2020-01-01','--end-date=2020-05-01', '--format=csv', '--file=myfi/le.csv'])
    assert result.exit_code == 0
    assert result.output != "błędny format, proszę wpisać 'csv' lub 'json\n"
    assert result.output != "TO jest opcja INC dla dat 2020-01-01 i 2020-05-01 oraz formatu csv i pliku myfile.csv\n"
    assert result.output == "Podana nazwa zawiera niedozwolony znak/i z podanych w liście: '<','>','#','%','&','*',':','?','/','|','\\'\n"

