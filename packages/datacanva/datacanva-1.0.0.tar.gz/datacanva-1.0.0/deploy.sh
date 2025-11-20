#! /bin/sh

rm -rf ./dist

python -m build

echo "Deploying to ${1:-testpypi}"
python -m twine upload --repository ${1:-testpypi} dist/*
