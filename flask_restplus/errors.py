# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import flask

from werkzeug.exceptions import HTTPException

from ._http import HTTPStatus

__all__ = (
    'abort',
    'RestError',
    'ValidationError',
    'SpecsError',
)


def response_error_arg(message, code=None) -> dict:
    data =  {
    "ok": True,
    "data": {
        "result": code,
        "result_msg": message
    }}
    return data


def get_code(code=None):
    regex = r"\[(.*?)\]"
    matches = re.finditer(regex, code, re.MULTILINE)
    code_error = []
    for matchNum, match in enumerate(matches, start=1):
        code_error.append(match.group(1))
    if code_error:
        return code_error.pop()
    return code_error


def get_message(message):
    regex = r"\[(.*?)\]"
    test_str = message
    subst = ""
    result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
    return result


def parser_message(errors):
    try:
        str_error = list(errors.items())
        message = get_message(str_error[0][1])
        code = get_code(str_error[0][1])

        if code:
            response = response_error_arg(message=message, code=code)
        else:
            response = response_error_arg(message=message)
        return response
    except HTTPException as e:
        return response_error_arg(message="Error del validor", code="ERROR-ARG")


def abort(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=None, **kwargs):
    '''
    Properly abort the current request.

    Raise a `HTTPException` for the given status `code`.
    Attach any keyword arguments to the exception for later processing.

    :param int code: The associated HTTP status code
    :param str message: An optional details message
    :param kwargs: Any additional data to pass to the error payload
    :raise HTTPException:
    '''
    try:
        flask.abort(code)
    except HTTPException as e:
        if message:
            kwargs['message'] = str(message)
        if kwargs:
            message_parse = parser_message(errors=kwargs['errors'])
            e.data = message_parse
        raise


class RestError(Exception):
    '''Base class for all Flask-Restplus Errors'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ValidationError(RestError):
    '''A helper class for validation errors.'''
    pass


class SpecsError(RestError):
    '''A helper class for incoherent specifications.'''
    pass
