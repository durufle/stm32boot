# Device description schema
template = {
    'DeviceID': {'type': 'integer', 'required': True},
    'Name': {'type': 'string', 'required': True},
    'Series': {'type': 'string', 'required': True},
    'CPU': {'type': 'string', 'required': True},
    'Description': {'type': 'string', 'required': True},
    'FlashSize': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'number',}
        }
    },
    'UniversalID': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'number',}
        }
    },
    'Peripherals': {
        'type': 'dict',
        'schema': {
            'Flash': {
                'type': 'dict',
                'schema': {
                    'PageSize': {'type': 'number'}
                }
            }
        }
    }
}
