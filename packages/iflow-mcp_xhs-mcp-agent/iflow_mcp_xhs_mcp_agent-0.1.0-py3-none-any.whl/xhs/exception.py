from enum import Enum
from typing import Optional

import requests


class ErrorCode:
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


class ErrorEnum(Enum):
    IP_BLOCK = ErrorCode(429, "IP blocked by Xiaohongshu")
    SIGN_FAULT = ErrorCode(430, "Sign error")
    NOTE_ABNORMAL = ErrorCode(431, "Note is abnormal")
    NOTE_SECRETE_FAULT = ErrorCode(432, "Note is secret")


class XhsException(Exception):
    """Base exception for XHS API"""
    def __init__(self, message: str, response: Optional[requests.Response] = None):
        self.message = message
        self.response = response
        super().__init__(self.message)


class DataFetchError(XhsException):
    """Exception raised when data fetch fails"""
    pass


class IPBlockError(XhsException):
    """Exception raised when IP is blocked"""
    pass


class NeedVerifyError(XhsException):
    """Exception raised when verification is needed"""
    def __init__(self, message: str, response: Optional[requests.Response] = None, 
                 verify_type: str = None, verify_uuid: str = None):
        super().__init__(message, response)
        self.verify_type = verify_type
        self.verify_uuid = verify_uuid


class SignError(XhsException):
    """Exception raised when sign is invalid"""
    pass
