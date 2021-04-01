from click.testing import CliRunner
from script import main

def test_avarage():
    runner = CliRunner()
    result = runner.invoke(main, ['average','--start-date=2020-01','--end-date=2020-05'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja AVG dla dat 2020-01 i 2020-05\n"

def test_increase():
    runner = CliRunner()
    result = runner.invoke(main, ['increase','--start-date=2020-01-01','--end-date=2020-05-02'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja INC dla dat 2020-01-01 i 2020-05-02\n"

def test_export():
    runner = CliRunner()
    result = runner.invoke(main, ['export','--start-date=2020-01','--end-date=2020-05', '--format=csv', '--file=myfile.csv'])
    assert result.exit_code == 0
    assert result.output == "TO jest opcja INC dla dat 2020-01 i 2020-05 oraz formatu csv i pliku myfile.csv\n"

