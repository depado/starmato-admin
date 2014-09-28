# -*- coding: utf-8 -*-
################################################################################
# Project: argamato
# Filename: base/admin.py
################################################################################
# Authors: A. BAILLARD (ab@outofpluto.com)
# Dates: mercurial
################################################################################
# Comments:
# 04/07/14      Add header and comments
################################################################################
#
from starmato.admin.models import StarmatoOption, Country, Currency, Language
from starmato.admin.sites import site

site.register(StarmatoOption, None, main=True)

site.register(Country)
site.register(Currency)
site.register(Language)
