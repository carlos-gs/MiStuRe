#!/usr/bin/env python3
# encoding: utf-8

import re

M_REGEX_PATH = re.compile('^/$|(^(?=/)|^\.|^\.\.)(/(?=[^/\0])[^/\0]+)*/?$')

