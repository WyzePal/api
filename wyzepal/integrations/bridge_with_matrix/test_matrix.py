from .matrix_bridge import (
    check_wyzepal_message_validity,
    wyzepal_to_matrix,
)

from unittest import TestCase, mock
from subprocess import Popen, PIPE
import os

import shutil

from contextlib import contextmanager
from tempfile import mkdtemp

script_file = "matrix_bridge.py"
script_dir = os.path.dirname(__file__)
script = os.path.join(script_dir, script_file)

from typing import List, Iterator

sample_config_path = "matrix_test.conf"

sample_config_text = """[matrix]
host = https://matrix.org
username = username
password = password
room_id = #wyzepal:matrix.org

[wyzepal]
email = glitch-bot@chat.wyzepal.org
api_key = aPiKeY
site = https://chat.wyzepal.org
stream = test here
topic = matrix

"""

@contextmanager
def new_temp_dir():
    # type: () -> Iterator[str]
    path = mkdtemp()
    yield path
    shutil.rmtree(path)

class MatrixBridgeScriptTests(TestCase):
    def output_from_script(self, options):
        # type: (List[str]) -> List[str]
        popen = Popen(["python", script] + options, stdin=PIPE, stdout=PIPE, universal_newlines=True)
        return popen.communicate()[0].strip().split("\n")

    def test_no_args(self):
        # type: () -> None
        output_lines = self.output_from_script([])
        expected_lines = [
            "Options required: -c or --config to run, OR --write-sample-config.",
            "usage: {} [-h]".format(script_file)
        ]
        for expected, output in zip(expected_lines, output_lines):
            self.assertIn(expected, output)

    def test_help_usage_and_description(self):
        # type: () -> None
        output_lines = self.output_from_script(["-h"])
        usage = "usage: {} [-h]".format(script_file)
        description = "Script to bridge"
        self.assertIn(usage, output_lines[0])
        blank_lines = [num for num, line in enumerate(output_lines) if line == '']
        # There should be blank lines in the output
        self.assertTrue(blank_lines)
        # There should be finite output
        self.assertTrue(len(output_lines) > blank_lines[0])
        # Minimal description should be in the first line of the 2nd "paragraph"
        self.assertIn(description, output_lines[blank_lines[0] + 1])

    def test_write_sample_config(self):
        # type: () -> None
        with new_temp_dir() as tempdir:
            path = os.path.join(tempdir, sample_config_path)
            output_lines = self.output_from_script(["--write-sample-config", path])
            self.assertEqual(output_lines, ["Wrote sample configuration to '{}'".format(path)])

            with open(path) as sample_file:
                self.assertEqual(sample_file.read(), sample_config_text)

    def test_write_sample_config_from_wyzepalrc(self):
        # type: () -> None
        wyzepalrc_template = ["[api]", "email={email}", "key={key}", "site={site}"]
        wyzepal_params = {'email': 'foo@bar',
                        'key': 'some_api_key',
                        'site': 'https://some.chat.serverplace'}
        with new_temp_dir() as tempdir:
            path = os.path.join(tempdir, sample_config_path)
            wyzepalrc_path = os.path.join(tempdir, "wyzepalrc")
            with open(wyzepalrc_path, "w") as wyzepalrc_file:
                wyzepalrc_file.write("\n".join(wyzepalrc_template).format(**wyzepal_params))
            output_lines = self.output_from_script(["--write-sample-config", path,
                                                    "--from-wyzepalrc", wyzepalrc_path])
            self.assertEqual(output_lines,
                             ["Wrote sample configuration to '{}' using wyzepalrc file '{}'"
                              .format(path, wyzepalrc_path)])

            with open(path) as sample_file:
                sample_lines = [line.strip() for line in sample_file.readlines()]
                expected_lines = sample_config_text.split("\n")
                expected_lines[7] = 'email = {}'.format(wyzepal_params['email'])
                expected_lines[8] = 'api_key = {}'.format(wyzepal_params['key'])
                expected_lines[9] = 'site = {}'.format(wyzepal_params['site'])
                self.assertEqual(sample_lines, expected_lines[:-1])

    def test_detect_wyzepalrc_does_not_exist(self):
        # type: () -> None
        with new_temp_dir() as tempdir:
            path = os.path.join(tempdir, sample_config_path)
            wyzepalrc_path = os.path.join(tempdir, "wyzepalrc")
            # No writing of wyzepalrc file here -> triggers check for wyzepalrc absence
            output_lines = self.output_from_script(["--write-sample-config", path,
                                                    "--from-wyzepalrc", wyzepalrc_path])
            self.assertEqual(output_lines,
                             ["Could not write sample config: WyzePalrc file '{}' does not exist."
                              .format(wyzepalrc_path)])

class MatrixBridgeWyzePalToMatrixTests(TestCase):
    valid_wyzepal_config = dict(
        stream="some stream",
        topic="some topic",
        email="some@email"
    )
    valid_msg = dict(
        sender_email="John@Smith.smith",  # must not be equal to config:email
        type="stream",  # Can only mirror WyzePal streams
        display_recipient=valid_wyzepal_config['stream'],
        subject=valid_wyzepal_config['topic']
    )

    def test_wyzepal_message_validity_success(self):
        # type: () -> None
        wyzepal_config = self.valid_wyzepal_config
        msg = self.valid_msg
        # Ensure the test inputs are valid for success
        assert msg['sender_email'] != wyzepal_config['email']

        self.assertTrue(check_wyzepal_message_validity(msg, wyzepal_config))

    def test_wyzepal_message_validity_failure(self):
        # type: () -> None
        wyzepal_config = self.valid_wyzepal_config

        msg_wrong_stream = dict(self.valid_msg, display_recipient='foo')
        self.assertFalse(check_wyzepal_message_validity(msg_wrong_stream, wyzepal_config))

        msg_wrong_topic = dict(self.valid_msg, subject='foo')
        self.assertFalse(check_wyzepal_message_validity(msg_wrong_topic, wyzepal_config))

        msg_not_stream = dict(self.valid_msg, type="private")
        self.assertFalse(check_wyzepal_message_validity(msg_not_stream, wyzepal_config))

        msg_from_bot = dict(self.valid_msg, sender_email=wyzepal_config['email'])
        self.assertFalse(check_wyzepal_message_validity(msg_from_bot, wyzepal_config))

    def test_wyzepal_to_matrix(self):
        # type: () -> None
        room = mock.MagicMock()
        wyzepal_config = self.valid_wyzepal_config
        send_msg = wyzepal_to_matrix(wyzepal_config, room)

        msg = dict(self.valid_msg, sender_full_name="John Smith")

        expected = {
            'hi': '{} hi',
            '*hi*': '{} *hi*',
            '**hi**': '{} **hi**',
        }

        for content in expected:
            send_msg(dict(msg, content=content))

        for (method, params, _), expect in zip(room.method_calls, expected.values()):
            self.assertEqual(method, 'send_text')
            self.assertEqual(params[0], expect.format('<JohnSmith>'))