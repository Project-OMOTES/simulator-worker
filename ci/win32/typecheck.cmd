REM script to run mypy type checker on this source tree.
pushd .
cd /D "%~dp0"
cd ..\..\
call .\venv\Scripts\activate
set PYTHONPATH=.\src\simulator_worker;%$PYTHONPATH%
python -m mypy ./src/simulator_worker ./unit_test/
popd