import json
from lib2to3.pgen2 import token
import sys
# import json
import signal
import os

from json import dumps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
from threading import Thread, Timer
import time

from src.echo import echo
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.auth import auth_login_v1, auth_logout_v1, auth_register_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.user import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, user_stats_v1, users_stats_v1, user_profile_uploadphoto_v1
from src.channel import channel_messages_v1, channel_join_v1, channel_details_v1, channel_invite_v1, channel_addowner_v1, channel_leave_v1, channel_removeowner_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_react_v1, message_sendlater_v1, message_queue, message_pin_v1, message_unpin_v1, message_sendlaterdm_v1, message_share_v1, message_unreact_v1
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.other import clear_v1
from src.decorators import token_required
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, dm_remove_v1, dm_messages_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.notifications import get_notifications_v1
from src.search import search_v1


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)
APP.debug = False

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.before_first_request
def queue():
    Thread(target=message_queue).start()
    Timer(0.2, queue).start()

# Example
@APP.route("/echo", methods=['GET'])
def echo_handler():
    data = request.args.get('data')
    resp = echo(data)
    return dumps ({
        'data': resp
    })

# Wrappers
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    resp = clear_v1()
    return jsonify(resp)

@APP.route("/auth/login/v2", methods=['POST'])
# @json_body_required
def auth_login():
    data = request.get_json()
    resp = auth_login_v1(data['email'],data['password'])
    return jsonify(resp)

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    data = request.get_json()
    resp = auth_register_v1(data['email'],data['password'],data['name_first'],data['name_last'])
    return jsonify(resp)

@APP.route("/auth/logout/v1", methods=['POST'])
@token_required
def auth_logout(auth_user_id):
    data = request.get_json()
    resp = auth_logout_v1(auth_user_id, data['token'])
    return jsonify(resp)


@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request():
    data = request.get_json()
    resp = auth_passwordreset_request_v1(data['email'])
    return jsonify(resp)


@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_passwordreset_reset():
    data = request.get_json()
    resp = auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return jsonify(resp)


@APP.route("/users/all/v1", methods=['GET'])
@token_required
def users_all(auth_user_id):
    resp = users_all_v1()
    return jsonify(resp)


@APP.route("/user/profile/v1", methods=['GET'])
@token_required
def user_profile(auth_user_id):
    u_id = request.args.get('u_id', type=int)
    resp = user_profile_v1(u_id)
    return jsonify(resp)


@APP.route("/user/profile/setname/v1", methods=['PUT'])
@token_required
def user_profile_setname(auth_user_id):
    data = request.get_json()
    resp = user_profile_setname_v1(auth_user_id, data['name_first'], data['name_last'])
    return jsonify(resp)


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
@token_required
def user_profile_setemail(auth_user_id):
    data = request.get_json()
    resp = user_profile_setemail_v1(auth_user_id, data['email'])
    return jsonify(resp)


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
@token_required
def user_profile_sethandle(auth_user_id):
    data = request.get_json()
    resp = user_profile_sethandle_v1(auth_user_id, data['handle_str'])
    return jsonify(resp)

@APP.route("/user/stats/v1", methods=['GET'])
@token_required
def user_stats(auth_user_id):
    resp = user_stats_v1(auth_user_id)
    return jsonify(resp)

@APP.route("/users/stats/v1", methods=['GET'])
@token_required
def users_stats(auth_user_id):
    resp = users_stats_v1(auth_user_id)
    return jsonify(resp)


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
@token_required
def user_profile_uploadphoto(auth_user_id):
    data = request.get_json()
    resp = user_profile_uploadphoto_v1(auth_user_id, data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    return jsonify(resp)


@APP.route("/user/profile/image/<image_name>", methods=['GET'])
def user_profile_getimage(image_name):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, 'user_profile_images'), image_name)
    

@APP.route("/channels/create/v2", methods=['POST'])
@token_required
def channel_create(auth_user_id):
    data = request.get_json()
    ret = channels_create_v1(auth_user_id,data['name'],data['is_public'])
    return jsonify (ret)

@APP.route("/channels/list/v2", methods=['GET'])
@token_required
def channels_list(auth_user_id):
    ret = channels_list_v1(auth_user_id)
    return jsonify (ret)

@APP.route("/channel/details/v2", methods=['GET'])
@token_required
def channel_details(auth_user_id):
    channel_id = request.args.get('channel_id', type=int)
    ret = channel_details_v1(auth_user_id, channel_id)
    return jsonify (ret)

@APP.route("/channels/listall/v2", methods=['GET'])
@token_required
def channels_listall(auth_user_id):
    ret = channels_listall_v1(auth_user_id)
    return jsonify (ret)

@APP.route("/channel/join/v2", methods=['POST'])
@token_required
def channel_join(auth_user_id):
    data = request.get_json()
    ret = channel_join_v1(auth_user_id, data['channel_id'])
    return jsonify (ret)

@APP.route("/channel/invite/v2", methods=['POST'])
@token_required
def channel_invite_v2(auth_user_id):
    data = request.get_json()
    ret = channel_invite_v1(auth_user_id, data['channel_id'], data['u_id'])
    return jsonify(ret)

@APP.route("/channel/messages/v2", methods=['GET'])
@token_required
def channel_messages(auth_user_id):
    channel_id = request.args.get('channel_id', type=int)
    start = request.args.get('start', type=int)
    ret = channel_messages_v1(auth_user_id, channel_id, start)
    return jsonify (ret)

@APP.route("/channel/addowner/v1", methods=['POST'])
@token_required
def channel_addowner(auth_user_id):
    data = request.get_json()
    ret = channel_addowner_v1(auth_user_id, data['channel_id'], data['u_id'])
    return jsonify(ret)

@APP.route("/channel/removeowner/v1", methods=['POST'])
@token_required
def channel_removeowner(auth_user_id):
    data = request.get_json()
    ret = channel_removeowner_v1(auth_user_id, data['channel_id'], data['u_id'])
    return jsonify(ret)

@APP.route("/channel/leave/v1", methods=['POST'])
@token_required
def channel_leave(auth_user_id):
    data = request.get_json()
    ret = channel_leave_v1(auth_user_id, data['channel_id'])
    return jsonify(ret)

@APP.route("/message/send/v1", methods=['POST'])
@token_required
def message_send(auth_user_id):
    data = request.get_json()
    ret = message_send_v1(auth_user_id, data['channel_id'], data['message'])
    return jsonify (ret)

@APP.route("/message/edit/v1", methods=['PUT'])
@token_required
def message_edit(auth_user_id):
    data = request.get_json()
    ret = message_edit_v1(auth_user_id, data['message_id'], data['message'])
    return jsonify (ret)

@APP.route("/message/remove/v1", methods=['DELETE'])
@token_required
def message_remove(auth_user_id):
    data = request.get_json()
    ret = message_remove_v1(auth_user_id, data['message_id'])
    return jsonify (ret)

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
@token_required
def admin_user_remove(auth_user_id):
    data = request.get_json()
    resp = admin_user_remove_v1(auth_user_id, data['u_id'])
    return jsonify(resp)

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
@token_required
def admin_userpermission_change(auth_user_id):
    data = request.get_json()
    resp = admin_userpermission_change_v1(auth_user_id, data['u_id'], data['permission_id'])
    return jsonify(resp)

@APP.route("/dm/create/v1", methods=['POST'])
@token_required
def dm_create(auth_user_id):
    data = request.get_json()
    resp = dm_create_v1(auth_user_id, data['u_ids'])
    return jsonify(resp)

@APP.route("/dm/list/v1", methods=['GET'])
@token_required
def dm_list(auth_user_id):
    resp = dm_list_v1(auth_user_id)
    return jsonify(resp)

@APP.route("/dm/remove/v1", methods=['DELETE'])
@token_required
def dm_remove(auth_user_id):
    data = request.get_json()
    resp = dm_remove_v1(auth_user_id, data['dm_id'])
    return jsonify(resp)

@APP.route("/dm/details/v1", methods=['GET'])
@token_required
def dm_details(auth_user_id):
    dm_id = request.args.get('dm_id', type=int)
    resp = dm_details_v1(auth_user_id, dm_id)
    return jsonify(resp)

@APP.route("/dm/leave/v1", methods=['POST'])
@token_required
def dm_leave(auth_user_id):
    data = request.get_json()
    resp = dm_leave_v1(auth_user_id, data['dm_id'])
    return jsonify(resp)

@APP.route("/dm/messages/v1", methods=['GET'])
@token_required
def dm_messages(auth_user_id):
    dm_id = request.args.get('dm_id', type=int)
    start = request.args.get('start', type=int)
    resp = dm_messages_v1(auth_user_id, dm_id, start)
    return jsonify(resp)

@APP.route("/message/senddm/v1", methods=['POST'])
@token_required
def message_senddm(auth_user_id):
    data = request.get_json()
    ret = message_senddm_v1(auth_user_id, data['dm_id'], data['message'])
    return jsonify(ret)

@APP.route("/standup/start/v1", methods=['POST'])
@token_required
def standup_start(auth_user_id):
    data = request.get_json()
    resp = standup_start_v1(auth_user_id, data['channel_id'], data['length'])
    return jsonify(resp)

@APP.route("/standup/active/v1", methods=['GET'])
@token_required
def standup_active(auth_user_id):
    channel_id = request.args.get('channel_id', type=int)
    resp = standup_active_v1(auth_user_id, channel_id)
    return jsonify(resp)

@APP.route("/standup/send/v1", methods=['POST'])
@token_required
def standup_send(auth_user_id):
    data = request.get_json()
    resp = standup_send_v1(auth_user_id, data['channel_id'], data['message'])
    return jsonify(resp)
    

@APP.route("/notifications/get/v1", methods=['GET'])
@token_required
def get_notifications(auth_user_id):
    resp = get_notifications_v1(auth_user_id)
    return jsonify(resp)
@APP.route("/message/react/v1", methods=['POST'])
@token_required
def message_react(auth_user_id):
    data = request.get_json()
    ret = message_react_v1(auth_user_id, data['message_id'], data['react_id'])
    return jsonify (ret)

@APP.route("/message/unreact/v1", methods=['POST'])
@token_required
def message_unreact(auth_user_id):
    data = request.get_json()
    ret = message_unreact_v1(auth_user_id, data['message_id'], data['react_id'])
    return jsonify (ret)

@APP.route("/message/sendlater/v1", methods=['POST'])
@token_required
def message_sendlater(auth_user_id):
    data = request.get_json()
    ret = message_sendlater_v1(auth_user_id, data['channel_id'], data['message'], data['time_sent'])
    return jsonify (ret)

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
@token_required
def message_sendlaterdm(auth_user_id):
    data = request.get_json()
    ret = message_sendlaterdm_v1(auth_user_id, data['dm_id'], data['message'], data['time_sent'])
    return jsonify (ret)

@APP.route("/message/pin/v1", methods=['POST'])
@token_required
def message_pin(auth_user_id):
    data = request.get_json()
    ret = message_pin_v1(auth_user_id, data['message_id'])
    return jsonify (ret)

@APP.route("/message/unpin/v1", methods=['POST'])
@token_required
def message_unpin(auth_user_id):
    data = request.get_json()
    ret = message_unpin_v1(auth_user_id, data['message_id'])
    return jsonify (ret)

@APP.route("/search/v1", methods=['GET'])
@token_required
def search(auth_user_id):
    resp = search_v1(auth_user_id, request.args.get('query_str'))
    return jsonify(resp)

@APP.route("/message/share/v1", methods=['POST'])
@token_required
def message_share(auth_user_id):
    data = request.get_json()
    ret = message_share_v1(auth_user_id,data['og_message_id'],data['message'],data['channel_id'],data['dm_id'])
    return jsonify (ret)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

