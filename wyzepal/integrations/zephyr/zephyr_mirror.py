#!/usr/bin/env python
# Copyright (C) 2012 WyzePal, Inc.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import print_function
import sys
import subprocess
import os
import traceback
import signal

sys.path[:0] = [os.path.dirname(__file__)]
from zephyr_mirror_backend import parse_args

(options, args) = parse_args()

from types import FrameType
from typing import Any

def die(signal, frame):
    # type: (int, FrameType) -> None

    # We actually want to exit, so run os._exit (so as not to be caught and restarted)
    os._exit(1)

signal.signal(signal.SIGINT, die)

from wyzepal import RandomExponentialBackoff

args = [os.path.join(os.path.dirname(os.path.realpath(__file__)), "zephyr_mirror_backend.py")]
args.extend(sys.argv[1:])

if options.sync_subscriptions:
    subprocess.call(args)
    sys.exit(0)

if options.forward_class_messages and not options.noshard:
    # Needed to get access to zephyr.lib.parallel
    sys.path.append("/home/wyzepal/wyzepal")
    if options.on_startup_command is not None:
        subprocess.call([options.on_startup_command])
    from zerver.lib.parallel import run_parallel
    print("Starting parallel zephyr class mirroring bot")
    jobs = list("0123456789abcdef")

    def run_job(shard):
        # type: (str) -> int
        subprocess.call(args + ["--shard=%s" % (shard,)])
        return 0
    for (status, job) in run_parallel(run_job, jobs, threads=16):
        print("A mirroring shard died!")
        pass
    sys.exit(0)

backoff = RandomExponentialBackoff(timeout_success_equivalent=300)
while backoff.keep_going():
    print("Starting zephyr mirroring bot")
    try:
        subprocess.call(args)
    except Exception:
        traceback.print_exc()
    backoff.fail()


error_message = """
ERROR: The Zephyr mirroring bot is unable to continue mirroring Zephyrs.
This is often caused by failing to maintain unexpired Kerberos tickets
or AFS tokens.  See https://wyzepal.com/zephyr for documentation on how to
maintain unexpired Kerberos tickets and AFS tokens.
"""
print(error_message)
sys.exit(1)
