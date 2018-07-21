# Link Shortener Bot

Link Shortener Bot is a WyzePal bot that will shorten URLs ("links") in a
conversation. It uses the [bitly URL shortener API] to shorten its links.

Use [this](https://dev.bitly.com/get_started.html) to get your API Key.

Links can be anywhere in the message, for example,

 > @**Link Shortener Bot** @**Joe Smith** See
 > https://github.com/wyzepal/python-wyzepal-api/tree/master/wyzepal_bots/wyzepal_bots/bots
 > for a list of all WyzePal bots.

and LS Bot would respond

 > https://github.com/wyzepal/python-wyzepal-api/tree/master/wyzepal_bots/wyzepal_bots/bots:
 > **https://bit.ly/2FF3QHu**

[bitly URL shortener API]: https://bitly.com/
