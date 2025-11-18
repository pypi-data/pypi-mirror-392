#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

import re
from datetime import datetime
from typing import List
import time
import json
import io
import csv
from functools import partial

import treerequests
from reliq import RQ
import requests

from .exceptions import Error, RequestError, TimeoutError

reliq = RQ(cached="True")


def get_epoch():
    return datetime.now().strftime("%s")


class NewMsg:
    def __init__(self, func):
        self.state = {}
        self.func = func
        self.add_state(self.func())

    def to_hashable_dict(self, el):
        return tuple(sorted(el.items()))

    def to_hashable(self, el):
        return tuple(self.to_hashable_dict(i) for i in el)

    def add_state(self, news):
        for i, j in news.items():
            if i not in self.state:
                self.state[i] = ()

            self.state[i] = self.to_hashable(j)

    def check_r(self):
        news = self.func()
        for i, j in news.items():
            if i not in self.state:
                for k in j:
                    yield i, k
            else:
                for k in j:
                    if self.to_hashable_dict(k) not in self.state[i]:
                        yield i, k

        self.add_state(news)

    def check(self, retries=40, wait=3):
        g = 0
        x = []
        while g < retries:
            x = list(self.check_r())
            if len(x) != 0:
                yield from x
                break

            g += 1
            time.sleep(wait)

        if len(x) == 0:
            raise TimeoutError


class Api:
    def __init__(self, host, username="admin", password="admin", **kwargs):
        self.host = host
        self.username = username
        self.password = password

        self.ses = treerequests.Session(
            requests,
            requests.Session,
            lambda x, y: treerequests.reliq(x, y, obj=reliq),
            requesterror=RequestError,
            **kwargs,
        )

    def call_api_request(self, path, method, type, **kwargs):
        url = self.host + "/default/en_US/" + path
        # print(kwargs.get("params"), file=sys.stderr)
        func = None
        if type == "html":
            func = partial(self.ses.html, method=method)
        elif type == "json":
            func = partial(self.ses.json, method=method)
        else:
            func = partial(self.ses.request, method)

        r = func(
            url,
            auth=(self.username, self.password),
            **kwargs,
        )
        return r

    def call_api(self, path, method="get", type="html", **kwargs):
        r = self.call_api_request(path, method, type, **kwargs)
        return r

    def _tag_to_dict(
        self,
        tag,
        name=lambda x: x.name,
        value=lambda x: reliq(reliq.decode(x.insides)).text_recursive,
    ):
        return {name(i): value(i) for i in tag.children(True)}

    def _lines_from_dict(self, r):
        return set(x[1] for i in r.keys() if (x := re.fullmatch(r"l([0-9]+)_.*", i)))

    def _status(self, type):
        rq = self.call_api(f"status.xml?type={type}&ajaxcachebust=" + get_epoch())
        status = rq.filter("[0] status")
        assert status is not reliq.Type.empty

        return self._tag_to_dict(status)

    def _create_struct(
        self, r, keys, fields, name=lambda x, y: x, value=lambda x, y: y
    ):
        ret = {}
        for i in keys:
            rec = {}
            for j in fields:
                n = name(i, j)
                if n not in r:
                    rec[j] = ""
                else:
                    rec[j] = value(j, r[n])
            ret[i] = rec
        return ret

    def _create_lines_struct(self, r, fields):
        return self._create_struct(
            r,
            self._lines_from_dict(r),
            fields,
            name=lambda x, y: "l" + str(x) + "_" + y,
        )

    def status_summary(self):
        return self._create_lines_struct(
            self._status("list"),
            {
                "module_status_gsm",
                "module_title_gsm",
                "module_status",
                "module_title",
                "gsm_sim",
                "gsm_status",
                "status_line",
                "line_state",
                "sms_login",
                "smb_login",
                "gsm_signal",
                "gsm_cur_oper",
                "gsm_cur_bst",
                "volte",
                "lac",
                "sim_remain",
                "nocall_t",
                "acd",
                "asr",
                "callt",
                "callc",
                "rct",
                "sms_count",
                "call_count",
            },
        )

    def status_general(self):
        r = self._status("base")

        cstat = self._create_lines_struct(
            r,
            {
                "status_line",
                "gsm_status",
                "sim_remain",
                "config_mode",
                "digits",
                "proxy",
                "server",
                "sip_prefix",
                "fw_to_voip",
                "fw_to_pstn",
            },
        )

        ret = {
            "hardware": {
                "s/n": r["sn"],
                "firmware": r["version"],
                "model": r["model"],
                "time": r["time"],
            },
            "network": {
                "ip": r["ech0_ip"],
                "mac": r["eth0_hwaddr"],
                "pc port": r["eth1_ip"],
                "pppoe": r["ppp0_ip"],
                "gateway": r["default_route"],
                "dns": r["dns"],
            },
            "call status": cstat,
        }
        return ret

    def status_sim(self):
        r = self._status("gsm")

        gsm = self._create_lines_struct(
            r,
            {
                "module_status_gsm",
                "module_status_gsm2",
                "gsm_sim",
                "gsm_status",
                "gsm_signal",
                "gsm_gprs_login",
                "gsm_gprs_attach",
                "gsm_cur_oper",
                "gsm_bst",
                "gsm_cur_bst",
                "lac",
                "gsm_module",
                "gsm_module_ver",
                "gsm_number",
                "gsm_imei",
                "sim_imsi",
                "sim_iccid",
            },
        )
        ret = {
            "sim_enable": r["remote_sim_enable"],
            "gsm": gsm,
        }
        return ret

    def status_callforward(self):
        return self._create_lines_struct(
            self._status("callforward"),
            {
                "module_status_ccfc",
                "cf_uncnd_status",
                "cf_busy_status",
                "cf_noreply_status",
                "cf_notreachable_status",
            },
        )

    def _get_sms_key(self, rq):
        return rq.search(r'[0] input type=hIdden name=smskey value | "%(value)"')

    def _sms_status(self, lines, iferror):
        def status():
            st = self.call_api(
                r"send_sms_status.xml?line=&ajaxcachebust=" + get_epoch()
            ).filter(r"[0] send-sms-status")
            assert st is not reliq.Type.empty

            return self._create_struct(
                self._tag_to_dict(st),
                lines,
                {"smskey", "status", "error"},
                name=lambda x, y: y + str(x),
            )

        def check_status():
            st = status()
            for i in lines:
                if st[i]["status"] == "STARTED":
                    return None
            return st

        while True:
            time.sleep(3)
            if (st := check_status()) is not None:
                return {
                    i: st[i]["error"]
                    for i in lines
                    if (not iferror) or st[i]["error"] != ""
                }

    def send_sms(self, number, msg, lines: List[int | str] = [], ensure=True):
        if len(lines) == 0:
            return {}

        smskey = self._get_sms_key(self.call_api("tools.html?type=sms"))

        data = {
            "smscontent": msg,
            "send": "Send",
            "smskey": smskey,
            "action": "SMS",
            "telnum": number,
        }
        for i in set(lines):
            data[f"line{i}"] = 1

        self.call_api("sms_info.html?type=sms", method="POST", data=data)

        if not ensure:
            return {}
        return self._sms_status(lines, True)

    def send_ussd(self, msg, lines: List[int | str] = [], ensure=True):
        if len(lines) == 0:
            return {}

        smskey = self._get_sms_key(self.call_api("tools.html?type=ussd"))

        data = {
            "send": "Send",
            "smskey": smskey,
            "action": "USSD",
            "telnum": msg,
        }
        for i in set(lines):
            data[f"line{i}"] = 1

        self.call_api("ussd_info.html?type=ussd", method="POST", data=data)

        if not ensure:
            return {}
        return self._sms_status(lines, False)

    def _get_inbox(self, type):
        rq = self.call_api(f"tools.html?type={type}")
        ret = {}
        inbox = rq.search(
            r"""
            [0] script language="javascript" | "%i" / sed "
                /^sms=/{
                    s/^sms= //
                    s/;\r?$//
                    N
                    s/\n.*, ([0-9]+)\);\r$/\t\1/
                    p
                }
            " "nE"
        """
        ).split("\n")

        for i in inbox:
            i = i.split("\t")
            if len(i) == 1:
                continue
            values, line = i
            values = json.loads(values)
            messages = []
            for j in values:
                date, mid, j = j.partition(",")
                num, mid, msg = j.partition(",")
                if mid != ",":
                    continue

                messages.append({"date": date, "number": num, "msg": msg})

            ret[line] = messages

        return ret

    def inbox(self):
        return self._get_inbox("sms_inbox")

    def outbox(self):
        return self._get_inbox("sms_outbox")

    def call_records(self):
        r = self.call_api("callrecord_1", type="resp").text
        r = list(
            csv.DictReader(
                io.StringIO(r),
                fieldnames=[
                    "id",
                    "Recv Time",
                    "Caller No.",
                    "Callee No.",
                    "Line ID",
                    "Outbound No.",
                    "Duration",
                    "Outbound Time",
                    "Answer Time",
                    "End Time",
                    "Hangup Side",
                    "Hangup Reason",
                ],
            )
        )

        for i in r:
            if i["Hangup Side"] == "b":
                i["Hangup Side"] = "Network"
            elif i["Hangup Side"] == "a":
                i["Hangup Side"] = "GoIP"
        return r

    def _clean_box(self, type, line, pos):
        self.call_api(f"tools.html?type={type}&action=del&line={line}&pos={pos}")

    def clean_inbox(self, line=-1, pos=-1):
        return self._clean_box("sms_inbox", line, pos)

    def clean_outbox(self, line=-1, pos=-1):
        return self._clean_box("sms_outbox", line, pos)

    def expect_inbox(self):
        return NewMsg(self.inbox)

    def expect_outbox(self):
        return NewMsg(self.outbox)
