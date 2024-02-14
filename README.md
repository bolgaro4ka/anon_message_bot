# Simple telegram bot on Python for anonymous messages.

**Must have Python installed**

## Database
In the users.json file - a list of users (name, username, to whom he sends messages), keys - Telegram ID

In the file sends.json - a list of messages sent by users, the key is the telegram ID

## Images
![image](https://github.com/bolgaro4ka/anon_message_bot/assets/123888141/27e5def4-d8c1-4a50-9941-3142ff3d6172)
![image](https://github.com/bolgaro4ka/anon_message_bot/assets/123888141/effc0490-3537-490b-bdd4-d01e77b18a87)

# Installation

## To activate venv use these commands:

``` python -m venv venv ```

### For Linux:

``` source venv/bin/activate ```

### For Windows:

``` venv/Scripts/activate ```

## Install this dependency for normal operation of the program:

``` pip install -r requirements.txt ```

Deployment .env: 

``` cp .env.template .env ```

 - ### .env.template HAS FAKE SECRET KEY VALUES! IT NEEDS TO BE CHANGED WITH YOURS!

## To start the server use the command:
``` python main.py ```

## Made by Bolgaro4ka