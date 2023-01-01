build flags="":
    docker build -t cuervot . {{flags}}

setup:
    pip install pip-tools

run: build
    docker run -it --rm --env-file .env cuervot

bash: build
    docker run -it --rm --env-file .env cuervot bash

lockdeps:
    pip-compile requirements.in -o requirements.txt --resolver=backtracking

deploy:
    git push dokku master:master

envs:
    ssh dokku@157.230.228.39 config:show cuervot

ssh:
    ssh root@157.230.228.39