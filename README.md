# Heart Rates Queries

This is a service which is able to store and query heart rate data for different categories of users (operating on randomly generated fixtures at this point).

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Heart Rates Queries](#heart-rates-queries)
    - [Python version](#python-version)
    - [Running locally](#running-locally)
    - [Running with Docker Compose](#running-with-docker-compose)

<!-- markdown-toc end -->

## Python version

Please make sure that you are using Python 3.12+ for virtualenv and running the application (refer to the version used in `Dockerfile`).

## Running locally

1. Install dependencies:

``` sh
# It is advised to create a virtualenv first
$ virtualenv -p python3.12 ./.venv
$ source .venv/bin/activate

$ pip install -r requirements.txt
```

2. Provide a .env configuration & modify values if needed:

``` sh
# Use .env.local to use DB available on `localhost`
$ cp .env.localhost .env
$ . ./.env
```

3. Provide Postgres (skip if already running on the host):

``` sh
$ docker compose up db -d
```

4. Run the application:

``` sh
$ fastapi prod main.py --port $APP_PORT
```


## Running with Docker Compose

1. Provide a .env configuration & modify values if needed:

``` sh
$ cp .env.compose .env
$ . ./.env
```

2. Build the Docker image and start Compose services in detached mode:

``` sh
$ docker compose up --build -d
```

3. Observe logs with:

``` sh
$ docker compose logs app -f
```


Explore the API in a browser (APP_PORT is set to 8000 by default):

`https://localhost:8000/docs`

