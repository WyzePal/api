#!/usr/bin/env python
import os
import logging
import signal
import traceback
import wyzepal
import sys
import argparse
import re
from six.moves import configparser

from collections import OrderedDict

from types import FrameType
from typing import Any, Callable, Dict, Optional

from matrix_client.errors import MatrixRequestError
from matrix_client.client import MatrixClient
from requests.exceptions import MissingSchema

GENERAL_NETWORK_USERNAME_REGEX = '@_?[a-zA-Z0-9]+_([a-zA-Z0-9-_]+):[a-zA-Z0-9.]+'
MATRIX_USERNAME_REGEX = '@([a-zA-Z0-9-_]+):matrix.org'

# change these templates to change the format of displayed message
WYZEPAL_MESSAGE_TEMPLATE = "**{username}**: {message}"
MATRIX_MESSAGE_TEMPLATE = "<{username}> {message}"

class Bridge_ConfigException(Exception):
    pass

class Bridge_FatalMatrixException(Exception):
    pass

class Bridge_WyzePalFatalException(Exception):
    pass

def matrix_login(matrix_client, matrix_config):
    # type: (Any, Dict[str, Any]) -> None
    try:
        matrix_client.login_with_password(matrix_config["username"],
                                          matrix_config["password"])
    except MatrixRequestError as exception:
        if exception.code == 403:
            raise Bridge_FatalMatrixException("Bad username or password.")
        else:
            raise Bridge_FatalMatrixException("Check if your server details are correct.")
    except MissingSchema as exception:
        raise Bridge_FatalMatrixException("Bad URL format.")

def matrix_join_room(matrix_client, matrix_config):
    # type: (Any, Dict[str, Any]) -> Any
    try:
        room = matrix_client.join_room(matrix_config["room_id"])
        return room
    except MatrixRequestError as exception:
        if exception.code == 403:
            raise Bridge_FatalMatrixException("Room ID/Alias in the wrong format")
        else:
            raise Bridge_FatalMatrixException("Couldn't find room.")

def die(signal, frame):
    # type: (int, FrameType) -> None
    # We actually want to exit, so run os._exit (so as not to be caught and restarted)
    os._exit(1)

def matrix_to_wyzepal(wyzepal_client, wyzepal_config, matrix_config, no_noise):
    # type: (wyzepal.Client, Dict[str, Any], Dict[str, Any], bool) -> Callable[[Any, Dict[str, Any]], None]
    def _matrix_to_wyzepal(room, event):
        # type: (Any, Dict[str, Any]) -> None
        """
        Matrix -> WyzePal
        """
        content = get_message_content_from_event(event, no_noise)

        wyzepal_bot_user = ('@%s:matrix.org' % matrix_config['username'])
        # We do this to identify the messages generated from WyzePal -> Matrix
        # and we make sure we don't forward it again to the WyzePal stream.
        not_from_wyzepal_bot = ('body' not in event['content'] or
                              event['sender'] != wyzepal_bot_user)

        if not_from_wyzepal_bot and content:
            try:
                result = wyzepal_client.send_message({
                    "sender": wyzepal_client.email,
                    "type": "stream",
                    "to": wyzepal_config["stream"],
                    "subject": wyzepal_config["topic"],
                    "content": content,
                })
            except Exception as exception:  # XXX This should be more specific
                # Generally raised when user is forbidden
                raise Bridge_WyzePalFatalException(exception)
            if result['result'] != 'success':
                # Generally raised when API key is invalid
                raise Bridge_WyzePalFatalException(result['msg'])

    return _matrix_to_wyzepal

def get_message_content_from_event(event, no_noise):
    # type: (Dict[str, Any], bool) -> Optional[str]
    irc_nick = shorten_irc_nick(event['sender'])
    if event['type'] == "m.room.member":
        if no_noise:
            return None
        # Join and leave events can be noisy. They are ignored by default.
        # To enable these events pass `no_noise` as `False` as the script argument
        if event['membership'] == "join":
            content = WYZEPAL_MESSAGE_TEMPLATE.format(username=irc_nick,
                                                    message="joined")
        elif event['membership'] == "leave":
            content = WYZEPAL_MESSAGE_TEMPLATE.format(username=irc_nick,
                                                    message="quit")
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text" or event['content']['msgtype'] == "m.emote":
            content = WYZEPAL_MESSAGE_TEMPLATE.format(username=irc_nick,
                                                    message=event['content']['body'])
    else:
        content = event['type']
    return content

def shorten_irc_nick(nick):
    # type: (str) -> str
    """
    Add nick shortner functions for specific IRC networks
    Eg: For freenode change '@freenode_user:matrix.org' to 'user'
    Check the list of IRC networks here:
    https://github.com/matrix-org/matrix-appservice-irc/wiki/Bridged-IRC-networks
    """
    match = re.match(GENERAL_NETWORK_USERNAME_REGEX, nick)
    if match:
        return match.group(1)
    # For matrix users
    match = re.match(MATRIX_USERNAME_REGEX, nick)
    if match:
        return match.group(1)
    return nick

def wyzepal_to_matrix(config, room):
    # type: (Dict[str, Any], Any) -> Callable[[Dict[str, Any]], None]

    def _wyzepal_to_matrix(msg):
        # type: (Dict[str, Any]) -> None
        """
        WyzePal -> Matrix
        """
        message_valid = check_wyzepal_message_validity(msg, config)
        if message_valid:
            matrix_username = msg["sender_full_name"].replace(' ', '')
            matrix_text = MATRIX_MESSAGE_TEMPLATE.format(username=matrix_username,
                                                         message=msg["content"])
            # Forward WyzePal message to Matrix
            room.send_text(matrix_text)
    return _wyzepal_to_matrix

def check_wyzepal_message_validity(msg, config):
    # type: (Dict[str, Any], Dict[str, Any]) -> bool
    is_a_stream = msg["type"] == "stream"
    in_the_specified_stream = msg["display_recipient"] == config["stream"]
    at_the_specified_subject = msg["subject"] == config["topic"]

    # We do this to identify the messages generated from Matrix -> WyzePal
    # and we make sure we don't forward it again to the Matrix.
    not_from_wyzepal_bot = msg["sender_email"] != config["email"]
    if is_a_stream and not_from_wyzepal_bot and in_the_specified_stream and at_the_specified_subject:
        return True
    return False

def generate_parser():
    # type: () -> argparse.ArgumentParser
    description = """
    Script to bridge between a topic in a WyzePal stream, and a Matrix channel.

    Tested connections:
        * WyzePal <-> Matrix channel
        * WyzePal <-> IRC channel (bridged via Matrix)

    Example matrix 'room_id' options might be, if via matrix.org:
        * #wyzepal:matrix.org (wyzepal channel on Matrix)
        * #freenode_#wyzepal:matrix.org (wyzepal channel on irc.freenode.net)"""

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--config', required=False,
                        help="Path to the config file for the bridge.")
    parser.add_argument('--write-sample-config', metavar='PATH', dest='sample_config',
                        help="Generate a configuration template at the specified location.")
    parser.add_argument('--from-wyzepalrc', metavar='WYZEPALRC', dest='wyzepalrc',
                        help="Optional path to wyzepalrc file for bot, when using --write-sample-config")
    parser.add_argument('--show-join-leave', dest='no_noise',
                        default=True, action='store_false',
                        help="Enable IRC join/leave events.")
    return parser

def read_configuration(config_file):
    # type: (str) -> Dict[str, Dict[str, str]]
    config = configparser.ConfigParser()

    try:
        config.read(config_file)
    except configparser.Error as exception:
        raise Bridge_ConfigException(str(exception))

    if set(config.sections()) != {'matrix', 'wyzepal'}:
        raise Bridge_ConfigException("Please ensure the configuration has wyzepal & matrix sections.")

    # TODO Could add more checks for configuration content here

    return {section: dict(config[section]) for section in config.sections()}

def write_sample_config(target_path, wyzepalrc):
    # type: (str, Optional[str]) -> None
    if os.path.exists(target_path):
        raise Bridge_ConfigException("Path '{}' exists; not overwriting existing file.".format(target_path))

    sample_dict = OrderedDict((
        ('matrix', OrderedDict((
            ('host', 'https://matrix.org'),
            ('username', 'username'),
            ('password', 'password'),
            ('room_id', '#wyzepal:matrix.org'),
        ))),
        ('wyzepal', OrderedDict((
            ('email', 'glitch-bot@chat.wyzepal.org'),
            ('api_key', 'aPiKeY'),
            ('site', 'https://chat.wyzepal.org'),
            ('stream', 'test here'),
            ('topic', 'matrix'),
        ))),
    ))

    if wyzepalrc is not None:
        if not os.path.exists(wyzepalrc):
            raise Bridge_ConfigException("WyzePalrc file '{}' does not exist.".format(wyzepalrc))

        wyzepalrc_config = configparser.ConfigParser()
        try:
            wyzepalrc_config.read(wyzepalrc)
        except configparser.Error as exception:
            raise Bridge_ConfigException(str(exception))

        # Can add more checks for validity of wyzepalrc file here

        sample_dict['wyzepal']['email'] = wyzepalrc_config['api']['email']
        sample_dict['wyzepal']['site'] = wyzepalrc_config['api']['site']
        sample_dict['wyzepal']['api_key'] = wyzepalrc_config['api']['key']

    sample = configparser.ConfigParser()
    sample.read_dict(sample_dict)
    with open(target_path, 'w') as target:
        sample.write(target)

def main():
    # type: () -> None
    signal.signal(signal.SIGINT, die)
    logging.basicConfig(level=logging.WARNING)

    parser = generate_parser()
    options = parser.parse_args()

    if options.sample_config:
        try:
            write_sample_config(options.sample_config, options.wyzepalrc)
        except Bridge_ConfigException as exception:
            print("Could not write sample config: {}".format(exception))
            sys.exit(1)
        if options.wyzepalrc is None:
            print("Wrote sample configuration to '{}'".format(options.sample_config))
        else:
            print("Wrote sample configuration to '{}' using wyzepalrc file '{}'"
                  .format(options.sample_config, options.wyzepalrc))
        sys.exit(0)
    elif not options.config:
        print("Options required: -c or --config to run, OR --write-sample-config.")
        parser.print_usage()
        sys.exit(1)

    try:
        config = read_configuration(options.config)
    except Bridge_ConfigException as exception:
        print("Could not parse config file: {}".format(exception))
        sys.exit(1)

    # Get config for each client
    wyzepal_config = config["wyzepal"]
    matrix_config = config["matrix"]

    # Initiate clients
    backoff = wyzepal.RandomExponentialBackoff(timeout_success_equivalent=300)
    while backoff.keep_going():
        print("Starting matrix mirroring bot")
        try:
            wyzepal_client = wyzepal.Client(email=wyzepal_config["email"],
                                        api_key=wyzepal_config["api_key"],
                                        site=wyzepal_config["site"])
            matrix_client = MatrixClient(matrix_config["host"])

            # Login to Matrix
            matrix_login(matrix_client, matrix_config)
            # Join a room in Matrix
            room = matrix_join_room(matrix_client, matrix_config)

            room.add_listener(matrix_to_wyzepal(wyzepal_client, wyzepal_config, matrix_config,
                                              options.no_noise))

            print("Starting listener thread on Matrix client")
            matrix_client.start_listener_thread()

            print("Starting message handler on WyzePal client")
            wyzepal_client.call_on_each_message(wyzepal_to_matrix(wyzepal_config, room))

        except Bridge_FatalMatrixException as exception:
            sys.exit("Matrix bridge error: {}".format(exception))
        except Bridge_WyzePalFatalException as exception:
            sys.exit("WyzePal bridge error: {}".format(exception))
        except wyzepal.WyzePalError as exception:
            sys.exit("WyzePal error: {}".format(exception))
        except Exception as e:
            traceback.print_exc()
        backoff.fail()

if __name__ == '__main__':
    main()
