from typing import Callable
from vitrea_host.parameter_api.v2.responses.floors import FloorNumbersParser, FloorParamsParser
from vitrea_host.parameter_api.v2.responses.rooms import RoomNumbersParser, RoomParamsParser
from vitrea_host.parameter_api.v2.responses.keys import KeypadNumbersParser, KeyParamsParser
from vitrea_host.parameter_api.v2.responses.acs import ACNumbersParser, ACParamsParser
from vitrea_host.parameter_api.v2.responses.scenarios import ScenarioNumbersParser, ScenarioParamsParser
from vitrea_host.parameter_api.v2.responses.base import BaseParameterResponseParser

class DBResponseParserFactory:
    """
    Factory class for creating response parsers.
    """

    PARSERS = [FloorNumbersParser, FloorParamsParser, RoomNumbersParser, RoomParamsParser, KeypadNumbersParser, KeyParamsParser, ACNumbersParser, ACParamsParser, ScenarioNumbersParser, ScenarioParamsParser]

    @classmethod
    def create_parser(cls, raw_data:bytes, send_callback:Callable) -> BaseParameterResponseParser:
        """
        Creates a parser based on the command number.
        """
        command_number = int(raw_data.hex()[8:10], base=16)
        for parser in cls.PARSERS:
            if parser.COMMAND_NUMBER.value == command_number:
                return parser(raw_data, send_callback)
        return None