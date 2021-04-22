# Taxlio CarAPI

Hi,

I would like to show you my version of CarAPI app.


If you want to run the application locally you will need a few things:

First, docker and docker compose.

I will not describe here how to install it, there are great docs for


docker -> https://docs.docker.com/install/

and

docker-compose -> https://docs.docker.com/compose/install/


OK, hardest thing behind us.


Now clone the repo by:

SSH -> git clone git@github.com:TheVerin/talixo_cars.git

HTTPS -> https://github.com/TheVerin/talixo_cars.git


Great


Now you can choose to run app in dev environment.

At first you have to create .env file witch all variables from .env.example file (you just can
change its name). After that run terminal from project root and then execute command:

    make setup


Really easy, right?


To get docs of the app you should visit:
/docs/


Last point is testing.
It is as simple as running the app. You need to run terminal from project root and:

    make test


If you want to remove app containers run command:

    make remove


That's all

I hope you enjoy the app :)
