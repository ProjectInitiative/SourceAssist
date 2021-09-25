# SourceAssist

[GitHub Repo](https://github.com/ProjectInitiative/SourceAssist)

## Purpose 

There is a lack of "smart" ways to deal with automated semantic versioning across various coding languages as well Docker and OCI containers. Microsoft's stack has a couple of tools that are able to extract git tags during compile time, completely. Not all languages support this defaultly, or is very disjointed. SourceAssit aims to solve 2 major problems: automatic sematic versioning increments, and building/repository management aid for DevOps pipelines. Some built in features include: building, tagging and version managament of docker containers with a configuation file that watches changes to dockerfiles. Automatic version increments given a list of files, commiting changes and pushing back to a remote.

## Installation

### Pip

[pypi](https://pypi.org/project/source-assist/)

```bash
pip install source-assist
```

### Docker/OCI

[ghcr](https://github.com/ProjectInitiative/SourceAssist/pkgs/container/source-assist)

[Docker-hub](https://hub.docker.com/repository/docker/projectinitiative/source-assist)

```bash
docker pull projectinitiative/source-assist:latest
# OR
docker pull ghcr.io/projectinitiative/source-assist:latest
```

## Usage

SourceAssist is mapped to `sa` once installed. 
`sa --help` will display all of the current subcommands present. Below is a brief overview of the included subcommands:

### `git`

`push`: Push and changes and commits back to the remote the repo was originally pulled from. Typically used by a CI/CD agent such as Jenkins or GH actions.

### `version`

`get`: Given a list of files, pull and print all the version numbers found. Possible use-case would be for build scripts or commit messages/tags that need to get the version numbers of one or multiple files.

`bump`: Given a list of files, search through and bump all of the version numbers by 1. Use the `--docker` flag to parse an json specific docker data files. 


### `docker`

`build`: Give a list of Docker JSON data files, build all containers and tag accordingly

>NOTE: Future features include printing the template Docker data file, and pushing all images to the respective repositories with credentials.

## Future Work

* Robust credential management (cred stores, and password/ssh key/API token read in from STDIN)
    * More flexible Docker builds/versioning
* Other container buildkits such as buildah and podman
* Checking previous commit messages for specifc tags/strings to indicate if a commit was a build
* Ability to provide custom version python parsing scripts
* Add docker install and mounting instructions for building docker containers from within the docker container
* Open to suggestions (Open an [issue](https://github.com/ProjectInitiative/SourceAssist/issues/new/choose)!)