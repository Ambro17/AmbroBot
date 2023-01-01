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
