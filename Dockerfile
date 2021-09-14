# build package for distribution
FROM python:3.8 AS build-stage

# update packages
RUN pip install pipenv

COPY . /devops

WORKDIR /devops

RUN pipenv install --dev
RUN pipenv run python -m build
RUN cp -r ./dist /dist


# copy and install to lightweight container
FROM python:alpine AS app-container

RUN apk add git
COPY --from=build-stage /dist /dist
WORKDIR /dist
RUN pip install "$(ls *.tar.gz)"

ENTRYPOINT ["devops"]
CMD ["--help"]
