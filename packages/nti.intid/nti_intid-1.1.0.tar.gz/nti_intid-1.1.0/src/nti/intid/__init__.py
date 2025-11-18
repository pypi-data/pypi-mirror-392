#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Root of nti.intid.
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

__all__ = [
    'INTIIntIdAddedEvent',
    'INTIIntIdRemovedEvent',
    'NTIIntIdAddedEvent',
    'NTIIntIdRemovedEvent',

]

from zc.intid.interfaces import IAfterIdAddedEvent as INTIIntIdAddedEvent
from zc.intid.interfaces import IBeforeIdRemovedEvent as INTIIntIdRemovedEvent

from zc.intid.interfaces import AfterIdAddedEvent as NTIIntIdAddedEvent
from zc.intid.interfaces import BeforeIdRemovedEvent as NTIIntIdRemovedEvent
