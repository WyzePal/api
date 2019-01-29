# IRC <--> WyzePal bridge

## Usage

```
./irc-mirror.py --irc-server=IRC_SERVER --channel=<CHANNEL> --nick-prefix=<NICK> --stream=<STREAM> [optional args]
```

`--stream` is a WyzePal stream.
`--topic` is a WyzePal topic, is optionally specified, defaults to "IRC".

IMPORTANT: Make sure the bot is subscribed to the relevant WyzePal stream!!

Specify your WyzePal API credentials and server in a ~/.wyzepalrc file or using the options.

Note that "_wyzepal" will be automatically appended to the IRC nick provided

## Example

```
./irc-mirror.py --irc-server=irc.freenode.net --channel='#python-mypy' --nick-prefix=irc_mirror \
--stream='test here' --topic='#mypy' \
--site="https://chat.wyzepal.org" --user=<bot-email> \
--api-key=<bot-api-key>
```
