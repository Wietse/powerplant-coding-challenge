# Powerplant coding challenge

This is my submission for the [powerplant-coding-challenge](https://github.com/gem-spaas/powerplant-coding-challenge).
The original README was moved to [doc/README.md](doc/README.md).

## Getting started

### Prerequisites

* Docker

If you wish to install and run on your local machine - i.e. without Docker - you will need:

* Python: I'm using Python 3.9.1, and I use [pyenv](https://github.com/pyenv/pyenv) to manage my Python versions.

I'm working on Ubuntu 20.04.1 LTS. There's no reason why this code shouldn't work on other systems and with older
versions of Python, but I haven't tested other configurations.

My preferred development environment is Vim in a terminal.


### Setting up

#### With Docker

This is the quickest way to get started. Open a terminal and from the root of this repository execute:

```
docker build -t pcc:dev .
```

This should build a docker image called `pcc:dev`

Now start the service with:

```
docker run -it --rm -p 8000:8000 pcc:dev
```

Note the `-it` options: I like to keep the terminal attached to the container so that I can see the logs.

If you now point your browser at http://localhost:8000/ you should see "Hello from pcd!".
If you open another terminal you can test using `curl` by executing:

```
curl -X POST -H "Content-Type: application/json" -d @doc/example_payloads/payload1.json http://localhost:8000/productionplan
```

Which should give a sensible response.

To test from the command line I prefer using the tool [httpie](https://httpie.io/) which is less verbose:

```
http -j POST :8000/productionplan < doc/example_payloads/payload1.json
```

For actual development, you can map the repository into the container. If you then set the `PCC_ENV` environment
variable in the container to `development`, the service will monitor changes to the code and reload the service so that
you can see the effects without doing a manual restart:

```
docker run -it --rm -p 8000:8000 -e PCC_ENV=development -v ${PWD}:/app pcc:dev
```

(This probably works in PowerShell on Windows as well, but if you use `cmd` on Windows the `${PWD}` incantation should
probably be changed to `%cd%`).


### On your local machine

To install locally I would advise to work in a python virtual environment. I simply execute the following command in the
root of the repository:

```
python -m venv .venv
```

And then to activate the virtual environment:

```
. ./.venv/bin/activate
```

I like updating the packaging libraries:

```
pip install -U pip setuptools wheel
```

Next install the necessary libraries with:

```
pip install -r requirements.txt -r requirements-dev.txt
```

And finally install this repository - in development mode - with:

```
pip install -e .
```
