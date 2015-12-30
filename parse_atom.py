#!/usr/bin/env python3

import re, sys

class AtomParseException(Exception):
    pass

class atom:

    def __init__(self, line):

        if line.startswith('='):
            pattern = '={category}{package}{version}{slot}?{repository}?'
        else:
            pattern = '{category}?{package}{version}?{slot}?{repository}?'

        cat = '(([A-Za-z0-9_][A-Za-z0-9+_.-]*)/)'
        pn = '([A-Za-z0-9_][A-Za-z0-9+_]*((-[A-Za-z0-9+_]+)*-[A-Za-z+_]+)*)'
        pv = '(-([0-9]+([.][0-9]+)*[a-z]?((_alpha|_beta|_pre|_rc|_p)[0-9]*)?(-r[0-9]+)?))'
        b_slot = '([A-Za-z0-9_][A-Za-z0-9+_.-]*)'
        slot = '(:{0}(/{0})?)'.format(b_slot)
        repo = '(::([A-Za-z0-9_][A-Za-z0-9_-]*))'

        reg = pattern.format(
                category=cat, package=pn, version=pv, slot=slot, repository=repo
            )

        pkg_re = re.compile(reg)

        match = pkg_re.match(line)

        if not match:
            raise AtomParseException()

        self.category = match.group(2)
        self.package = match.group(3)
        self.version = match.group(7)
        self.slot = match.group(13)
        self.subslot = match.group(15)
        self.repository = match.group(17)

    def __str__(self):
        return self.to_str(self.__dict__.keys())

    def __eq__(self, other):
        return \
            self.category == other.category and \
            self.package == other.package and \
            self.version == other.version and \
            self.slot == other.slot and \
            self.subslot == other.subslot and \
            self.repository == other.repository

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return \
            hash(self.category) ^ \
            hash(self.package) ^ \
            hash(self.version) ^ \
            hash(self.slot) ^ \
            hash(self.subslot) ^ \
            hash(self.repository)

    def to_str(self, selector):

        elements = {}
        for k, v in self.__dict__.items():
            if v:
                s = str(v)
            else:
                s = ''
            elements[k] = s

        if len(selector) is 1:
            return elements[selector[0]]

        def __add_if(ident, sep):
            global res
            if ident in selector and elements[ident] is not '':
                return sep + elements[ident]
            return ''

        res = ''

        if 'package' in selector:
            res = elements['package']

        if 'category' in selector and elements['category'] is not '':
            res = elements['category'] + '/' + res

        res += __add_if('version', '-')
        res += __add_if('slot', ':')
        res += __add_if('subslot', '/')
        res += __add_if('repository', '::')

        if 'version' in selector:
            res = '=' + res

        return res
