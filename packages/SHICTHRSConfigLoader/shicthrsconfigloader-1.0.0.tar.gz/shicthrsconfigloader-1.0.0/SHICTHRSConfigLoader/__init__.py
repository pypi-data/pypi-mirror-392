# *-* coding: utf-8 *-*
# src\__init__.py
# SHICTHRS CONFIG LOADER
# AUTHOR : SHICTHRS-JNTMTMTM
# Copyright : © 2025-2026 SHICTHRS, Std. All rights reserved.
# lICENSE : GPL-3.0

import os
from .utils.SHRConfigLoader_readConfigFile import read_ini_file
from .utils.SHRConfigLoader_writeConfigFile import write_ini_file

__all__ = [
    'SHRConfigLoader_read_ini_file',
    'SHRConfigLoader_write_ini_file'
]

class SHRConfigLoaderException(BaseException):
    def __init__(self , message: str) -> None:
        self.message = message
    
    def __str__(self):
        return self.message

def SHRConfigLoader_read_ini_file(path : str) -> dict:
    try:
        if os.path.exists(path):
            return read_ini_file(path)
        else:
            raise Exception(f"SHRConfigLoader [ERROR.1000] unable to find config file. File Path : {path} NOT FOUND")
    except Exception as e:
        raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1001] unable to read config file. File Path : {path} | {e}")

def SHRConfigLoader_write_ini_file(config_dict : dict , path : str) -> None:
    try:
        write_ini_file(config_dict , path)
    except Exception as e:
        raise SHRConfigLoaderException(f"SHRConfigLoader [ERROR.1003] unable to write config file. File Path : {path} | {e}")