# -*- coding: utf-8 -*-
"""
entipy
-------

A python ecs pattern

:copyright: (c) 2026 by Martin Walchshofer

"""

# compatibility
from __future__ import absolute_import, division, print_function

# get version
from .__version__ import __version__

# allow lazy loading
from .pattern import component, entity, scene, system
from .components import component_name, component_counter
from .systems import system_inctement_ui
from .utilities import utilities