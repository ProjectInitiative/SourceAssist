#!/usr/bin/env bash

# bump version first

# build python package
pipenv run python setup.py sdist bdist_whell

# build containers
pipenv run python ./sa/source_assist.py docker build ./docker-info.json

# upload to test.pypi and pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
twine upload dist/*

docker push --all-tags projectinitiative/source-assist
docker push --all-tags ghcr.io/projectinitiative/source-assist