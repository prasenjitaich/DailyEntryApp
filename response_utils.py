from flask import jsonify

RESPONSE_STATUS_ERROR = 0
RESPONSE_STATUS_SUCCESS = 1


def send_error_response(message=None, missing_param_name=None):
    """
    Return error response with status RESPONSE_STATUS_ERROR
    :param missing_param_name: If provided then create message with @get_param_missing_msg here
    :param message: message to pass
    :return:
    """
    response = dict()
    response['status'] = RESPONSE_STATUS_ERROR

    if message:
        response['message'] = message

    elif not message and missing_param_name:
        response['message'] = __get_param_missing_msg(missing_param_name)

    return jsonify(response)


def send_success_response(message, data=None):
    """
    Return error response with status RESPONSE_STATUS_SUCCESS
    :param data: data to be sent to client
    :param message: message to pass
    :return:
    """
    if data:
        response = {'status': RESPONSE_STATUS_SUCCESS, 'message': message, 'data': data}
    else:
        response = {'status': RESPONSE_STATUS_SUCCESS, 'message': message}

    return jsonify(response)


def __get_param_missing_msg(parameter_name):
    """
    Return param require message
    :param parameter_name: Name of parameter
    :return: str: message
    """
    return parameter_name + " is required."
