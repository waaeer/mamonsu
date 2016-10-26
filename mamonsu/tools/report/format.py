# -*- coding: utf-8 -*-


class TermColor:
    BOLD = '\033[0;0m\033[1;1m'
    RED = '\033[1;31m'
    GRAY = '\033[1;30m'
    PURPLE = '\033[1;35m'
    BLUE = '\033[1;34m'
    END = '\033[1;m'


def header_h1(info):
    return "\n{0}{1}{2}{3}\n".format(
        TermColor.BOLD, TermColor.RED, info.upper(), TermColor.END)


def key_val_h1(key, val):
    return "  {0}{1}{2:12}{3}: {4}\n".format(
        TermColor.BOLD, TermColor.PURPLE, key, TermColor.END, val)


def header_h2(info):
    return "  {0}{1}{2}{3}\n".format(
        TermColor.BOLD, TermColor.PURPLE, info, TermColor.END)


def key_val_h2(key, val, delim=': '):
    return "    {0}{1}{2:4}{3}{4}{5}\n".format(
        TermColor.BOLD, TermColor.BLUE, key, TermColor.END, delim, val)


def topline_h1(arr=[]):
    result = "  {0}{1}".format(TermColor.BOLD, TermColor.BLUE)
    for x in arr:
        result = "{0}\t{1}".format(result, x)
    return "{0}{1}\n".format(result, TermColor.END)
