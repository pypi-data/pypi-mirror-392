#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

import sys
import os
import argparse
import json
import re

import treerequests

from .api import Api


def pprint_json(data, pretty=True):
    if pretty:
        json.dump(data, sys.stdout, indent=2)
    else:
        json.dump(data, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


def valid_line(line):
    def err():
        raise argparse.ArgumentTypeError(f'Incorrect line number - "{line}"')

    if not line.isdigit():
        err()
    line = int(line)
    if line < 1 or line > 99:
        err()
    return str(line)


def valid_inbox_line(line):
    def err():
        raise argparse.ArgumentTypeError(f'Incorrect line number - "{line}"')

    left, mid, right = line.partition(".")
    try:
        line_num = valid_line(left)
        if len(right) == 0:
            return line_num
        pos = int(right)
        assert pos > 0
    except Exception:
        err
    return line_num + "." + right


def valid_number(number):
    assert re.fullmatch(r"+?[0-9]{3,30}", number)
    return number


def valid_command(command):
    assert len(command) > 0
    g = 0
    for i in command:
        if g == 0:
            assert i == "*" or i == "#"
        else:
            assert i == "*" or i == "#" or i.isdigit()
        g += 1

    return command


def valid_message(message):
    assert len(message) > 0
    return message


def cmd_status_summary(api, args):
    pprint_json(api.status_summary())


def cmd_status_general(api, args):
    pprint_json(api.status_general())


def cmd_status_sim(api, args):
    pprint_json(api.status_sim())


def cmd_status_callforward(api, args):
    pprint_json(api.status_callforward())


def get_all_lines(api):
    return list(api.status_summary().keys())


def cmd_send_sms(api, args):
    pprint_json(
        api.send_sms(
            args.number,
            args.message,
            (get_all_lines(api) if args.all else args.lines),
            ensure=(not args.no_ensure),
        )
    )


def cmd_send_ussd(api, args):
    pprint_json(
        api.send_sms(
            args.command,
            (get_all_lines(api) if args.all else args.lines),
            ensure=(not args.no_ensure),
        )
    )


def cmd_call_records(api, args):
    pprint_json(api.call_records())


def cmd_inbox(api, args):
    inbox = api.inbox()
    if len(args.lines) != 0:
        r = {}
        for i in args.lines:
            r[i] = inbox[i]
        inbox = r
    pprint_json(inbox)


def cmd_outbox(api, args):
    outbox = api.outbox()
    if len(args.lines) != 0:
        r = {}
        for i in args.lines:
            r[i] = outbox[i]
        outbox = r
    pprint_json(outbox)


def cmd_clean_inbox(api, args):
    if args.all:
        api.clean_inbox(-1, -1)
        return
    for i in args.lines:
        api.clean_inbox(*i.split("."))


def cmd_clean_outbox(api, args):
    if args.all:
        api.clean_outbox(-1, -1)
        return
    for i in args.lines:
        api.clean_outbox(*i.split("."))


def print_from_expect(obj, timeout):
    for line, val in obj.check(retries=timeout // 3, wait=3):
        val["line"] = line
        pprint_json(val, False)


def cmd_expect_inbox(api, args):
    print_from_expect(api.expect_inbox(), args.expect_timeout)


def cmd_expect_outbox(api, args):
    print_from_expect(api.expect_outbox(), args.expect_timeout)


def argparser():
    parser = argparse.ArgumentParser(
        description="A simple api for goip32",
        add_help=False,
    )

    general = parser.add_argument_group("General")
    general.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
    )
    general.add_argument(
        "-u",
        "--username",
        metavar="USERNAME",
        type=str,
        default=os.getenv("GOIP32_USER", ""),
        help="Specify username for authentication, defaults to $GOIP32_USER",
    )
    general.add_argument(
        "-p",
        "--password",
        metavar="PASSWORD",
        type=str,
        default=os.getenv("GOIP32_PASS", ""),
        help="Specify password for authentication, defaults to $GOIP32_PASS",
    )
    general.add_argument(
        "--host",
        metavar="HOST",
        type=str,
        default=os.getenv("GOIP32_HOST", ""),
        help="Specify host, defaults to $GOIP32_HOST",
    )

    subparsers = parser.add_subparsers(title="subcommands", required=True)

    status_summary_parser = subparsers.add_parser(
        "status-summary",
        help="get summary of lines",
        description="Gets summary of lines in json format",
    )
    status_summary_parser.set_defaults(func=cmd_status_summary)

    status_general_parser = subparsers.add_parser(
        "status-general",
        help="get general info about the system and call status",
        description="Gets general info about the system and call status in json format",
    )
    status_general_parser.set_defaults(func=cmd_status_general)

    status_sim_parser = subparsers.add_parser(
        "status-sim",
        help="get info about gsm in json format",
        description="Gets info about gsm in json format",
    )
    status_sim_parser.set_defaults(func=cmd_status_sim)

    status_callforward_parser = subparsers.add_parser(
        "status-callforward",
        help="get info about sim call forward for lines",
        description="Gets info about sim call forward for lines in json format",
    )
    status_callforward_parser.set_defaults(func=cmd_status_callforward)

    send_sms_parser = subparsers.add_parser(
        "send-sms",
        help="send sms",
        description="Sends sms message to number and returns it's status",
    )
    send_sms_parser.add_argument(
        "-a", "--all", action="store_true", help="affect all lines"
    )
    send_sms_parser.add_argument(
        "--no-ensure",
        action="store_true",
        help="don't ensure that message was sent successfully",
    )
    send_sms_parser.add_argument(
        "number", metavar="NUMBER", type=valid_number, help="recipient's number"
    )
    send_sms_parser.add_argument(
        "message", metavar="MESSAGE", type=valid_message, help="message to be sent"
    )
    send_sms_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="+",
        type=valid_line,
        help="affect only specified lines",
    )
    send_sms_parser.set_defaults(func=cmd_send_sms)

    send_ussd_parser = subparsers.add_parser(
        "send-ussd",
        help="send ussd code",
        description="Sends ussd code and returns it's output",
    )
    send_ussd_parser.add_argument(
        "-a", "--all", action="store_true", help="affect all lines"
    )
    send_ussd_parser.add_argument(
        "--no-ensure",
        action="store_true",
        help="don't ensure that command was sent successfully",
    )
    send_ussd_parser.add_argument(
        "command", metavar="COMMAND", type=valid_command, help="ussd command to be sent"
    )
    send_ussd_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="+",
        type=valid_line,
        help="affect only specified lines",
    )
    send_ussd_parser.set_defaults(func=cmd_send_ussd)

    inbox_parser = subparsers.add_parser(
        "inbox",
        help="get inbox",
        description="Gets inbox in json format",
    )
    inbox_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="*",
        type=valid_inbox_line,
        help="affect only specified lines",
    )
    inbox_parser.set_defaults(func=cmd_inbox)

    outbox_parser = subparsers.add_parser(
        "outbox",
        help="get outbox",
        description="Gets outbox in json format",
    )
    outbox_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="*",
        type=valid_inbox_line,
        help="affect only specified lines",
    )
    outbox_parser.set_defaults(func=cmd_outbox)

    call_records_parser = subparsers.add_parser(
        "call-records",
        help="get call records",
        description="Gets call records in json format",
    )
    call_records_parser.set_defaults(func=cmd_outbox)

    clean_inbox_parser = subparsers.add_parser(
        "clean-inbox",
        help="remove messages from inbox",
        description="Removes messages from inbox",
    )
    clean_inbox_parser.add_argument(
        "-a", "--all", action="store_true", help="affect all lines"
    )
    clean_inbox_parser.add_argument(
        "lines",
        metavar="LINE|LINE.POS",
        nargs="*",
        type=valid_inbox_line,
        help="affect specified lines or specific messages",
    )
    clean_inbox_parser.set_defaults(func=cmd_clean_inbox)

    clean_outbox_parser = subparsers.add_parser(
        "clean-outbox",
        help="remove messages from outbox",
        description="Remove messages from outbox",
    )
    clean_outbox_parser.add_argument(
        "-a", "--all", action="store_true", help="affect all lines"
    )
    clean_outbox_parser.add_argument(
        "lines",
        metavar="LINE|LINE.POS",
        nargs="*",
        type=valid_inbox_line,
        help="affect specified lines or specific messages",
    )
    clean_outbox_parser.set_defaults(func=cmd_clean_outbox)

    expect_inbox_parser = subparsers.add_parser(
        "expect-inbox",
        help="return newly received message",
        description="Returns newly received message, that was received since running this command",
    )
    expect_inbox_parser.add_argument(
        "--expect-timeout", type=int, help="timeout", default=120
    )
    expect_inbox_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="*",
        type=valid_line,
        help="affect only specified lines",
    )
    expect_inbox_parser.set_defaults(func=cmd_expect_inbox)

    expect_outbox_parser = subparsers.add_parser(
        "expect-outbox",
        help="return newly sent message",
        description="Returns newly sent message, that was sent since running this command",
    )
    expect_outbox_parser.add_argument(
        "--expect-timeout", type=int, help="timeout", default=120
    )
    expect_outbox_parser.add_argument(
        "lines",
        metavar="LINE",
        nargs="*",
        type=valid_line,
        help="affect only specified lines",
    )
    expect_outbox_parser.set_defaults(func=cmd_expect_outbox)

    treerequests.args_section(parser)

    return parser


def cli(argv: list[str]):
    args = argparser().parse_args(argv)
    if len(args.host) == 0 or len(args.username) == 0 or len(args.password) == 0:
        print("Specify credentials and host!", file=sys.stderr)
        return

    api = Api(args.host, args.username, args.password)
    treerequests.args_session(api.ses, args)
    # try:
    args.func(api, args)
    # except Exception as e:
    # print(repr(e), file=sys.stderr)
