# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Device description schema
"""
template = {
    'DeviceID': {'type': 'integer', 'required': True},
    'Name': {'type': 'string', 'required': True},
    'Series': {'type': 'string', 'required': True},
    'CPU': {'type': 'string', 'required': True},
    'Description': {'type': 'string', 'required': True},
    'FlashSize': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'number'}
        }
    },
    'UniversalID': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'number'}
        }
    },
    'Flash': {
        'type': 'dict',
        'schema': {
            'PageSize': {'type': 'number', 'required': True}
        }
    },
    'Bootloader': {
        'type': 'dict',
        'schema': {
            'ID': {'type': 'number', 'required': True},
            'RAM': {
                'type': 'dict',
                'schema': {
                    'min': {'type': 'number'},
                    'max': {'type': 'number'}
                },
            },
            'SYS': {
                'type': 'dict',
                'schema': {
                    'min': {'type': 'number'},
                    'max': {'type': 'number'}
                },
            }
        }
    }
}
