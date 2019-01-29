# Matrix <--> WyzePal bridge

This acts as a bridge between Matrix and WyzePal. It also enables a
WyzePal topic to be federated between two WyzePal servers.

## Usage

### For IRC bridges

Matrix has been bridged to the listed
[IRC networks](https://github.com/matrix-org/matrix-appservice-irc/wiki/Bridged-IRC-networks),
where the 'Room alias format' refers to the `room_id` for the corresponding IRC channel.

For example, for the freenode channel `#wyzepal-test`, the `room_id` would be
`#freenode_#wyzepal-test:matrix.org`.

Hence, this can also be used as a IRC <--> WyzePal bridge.

## Steps to configure the Matrix bridge

To obtain a configuration file template, run the script with the
`--write-sample-config` option to obtain a configuration file to fill in the
details mentioned below. For example:

* If you installed the `wyzepal` package: `wyzepal-matrix-bridge --write-sample-config matrix_bridge.conf`

* If you are running from the WyzePal GitHub repo: `python matrix_bridge.py --write-sample-config matrix_bridge.conf`

### 1. WyzePal endpoint
1. Create a generic WyzePal bot, with a full name like `IRC Bot` or `Matrix Bot`.
2. Subscribe the bot user to the stream you'd like to bridge your IRC or Matrix
   channel into.
3. In the `wyzepal` section of the configuration file, enter the bot's `wyzepalrc`
   details (`email`, `api_key`, and `site`).
4. In the same section, also enter the WyzePal `stream` and `topic`.

### 2. Matrix endpoint
1. Create a user on [matrix.org](https://matrix.org/), preferably with
   a formal name like to `wyzepal-bot`.
2. In the `matrix` section of the configuration file, enter the user's username
   and password.
3. Also enter the `host` and `room_id` into the same section.

## Running the bridge

After the steps above have been completed, assuming you have the configuration
in a file called `matrix_bridge.conf`:

* If you installed the `wyzepal` package: run `wyzepal-matrix-bridge -c matrix_bridge.conf`

* If you are running from the WyzePal GitHub repo: run `python matrix_bridge.py -c matrix_bridge.conf`

## Caveats for IRC mirroring

There are certain
[IRC channels](https://github.com/matrix-org/matrix-appservice-irc/wiki/Channels-from-which-the-IRC-bridge-is-banned)
where the Matrix.org IRC bridge has been banned for technical reasons.
You can't mirror those IRC channels using this integration.
