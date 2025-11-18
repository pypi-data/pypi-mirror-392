from vitrea_host.utils.enums import KeyTypes

PARAM_API_PREFIX = "5654483c"
SUPPORTED_VERSIONS = {
    7: 99,
    8: 67,
    9: 00,
    0: 00,
    10: 00,
}

UPGRADEABLE_VERSIONS = {
    7: 91,
    8: 0,
}

POLLABLE_KEY_TYPES = [
    KeyTypes.Toggle,
    KeyTypes.Boiler,
    KeyTypes.Heater,
    KeyTypes.Satellite,
    KeyTypes.RoomOn,
    KeyTypes.DND,
    KeyTypes.BlindUp,
    KeyTypes.BlindUpAndDown,
    KeyTypes.Dimmer,
    KeyTypes.Toggle,
    KeyTypes.PushButton,
    
]