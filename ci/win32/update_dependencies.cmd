
pushd .
cd /D "%~dp0"
pip-compile --verbose --output-file=..\..\requirements.txt ..\..\pyproject.toml
pip-compile --extra=dev --output-file=..\..\dev-requirements.txt -c ..\..\requirements.txt  ..\..\pyproject.toml
popd