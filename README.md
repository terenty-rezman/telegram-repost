# telegram repost

- do reposts from one chat to another automatically !
- do reposts from multiple chats to multiple chats ! watch out for __loops__

## usage
1) get your own __Telegram API key__ from https://my.telegram.org/apps
2) specify __api_key__, __api_hash__ and __reposts__ in __config.py__ <br />
   examples are given inside the __config.py__

## run without docker
1) install dependencies with ```$ pip install -r requirements.txt```
2) run the app ```$ python repost.py```
3) login with your phone number

### run using docker
1) the first run has to be with ```docker-compose run telegram-repost``` to allow you to enter your phone number
2) login with your phone number
3) you only have to login once, or when session is terminated by telegram,
   so on subsequent runs you can run with ```docker-compose up -d``` to run container in the background

> powered by [pyrogram](https://docs.pyrogram.org/)
