from flask import jsonify
from .daytime import EXE_ID

# a service to create http response faster

def bad_request(error='Bad Request'):
    return error_resp(400, error)

def not_found(error='Not Found'):
    return error_resp(404, error)

def unauthorized(error='UnAuthorized'):
    return error_resp(403, error)

def internal_error(error: Exception):
    return error_resp(500, str(error))

def success_resp(data = {}):
    return jsonify({
        'exe_id': EXE_ID,
        'data': data
    }), 200

def error_resp(code: int, error='error'):
    return jsonify({
        'exe_id': EXE_ID,
        'error': error
    }), code