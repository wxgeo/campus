#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 17:08:23 2021

@author: nicolas
"""

from pathlib import Path

from param import OUTPUTDIR_NAME, STYLES_PATH, STYLE_NAME

OUTPUT_PATH = Path(OUTPUTDIR_NAME).resolve()
# Replace '{CAMPUS}' in STYLE_PATH with campus library path.
STYLE_PATH = Path(
                 STYLES_PATH.format(CAMPUS=str(Path(__file__).parent.resolve()))
                 ) / STYLE_NAME

del OUTPUTDIR_NAME, STYLES_PATH, STYLE_NAME