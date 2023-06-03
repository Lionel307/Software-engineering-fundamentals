import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS

from src.error import InputError
from src import config
from src import auth
from src import channels
from src import channel
from src import other
from src import message
from src import dm
from src import user


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


# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/clear/v1", methods=["DELETE"])
def clear_v1():
    
    return dumps(other.clear_v1())


@APP.route("/auth/register/v2", methods=["POST"])
def auth_register():
    payload = request.get_json()

    return dumps(auth.auth_register_v2(
        payload["email"], payload["password"], payload["name_first"], payload["name_last"]
    ))


@APP.route("/auth/login/v2", methods=["POST"])
def auth_login():
    payload = request.get_json()

    return dumps(
        auth.auth_login_v2(payload["email"], payload["password"])
    )


@APP.route("/auth/logout/v1", methods=["POST"])
def auth_logout():
    token = request.get_json()["token"]

    return dumps(
        auth.auth_logout_v1(token)
    )


@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def reset_request():
    payload = request.get_json()

    return dumps(
        auth.auth_passwordreset_request_v1(payload["email"])
    )


@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def reset_reset():
    payload = request.get_json()

    return dumps(
        auth.auth_passwordreset_reset_v1(payload["reset_code"], payload["new_password"])
    )


@APP.route("/channels/create/v2", methods=['POST'])
def create_channel():
    payload = request.get_json()
    
    return dumps(
        channels.channels_create_v2(payload["token"], payload["name"], payload["is_public"])
    )


@APP.route("/channels/listall/v2", methods=['GET'])
def list_all_channels():
    token = request.args.get("token")

    return dumps(channels.channels_listall_v2(token))


@APP.route("/channel/details/v2", methods=['GET'])
def provide_channel_details():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id", type=int)

    return dumps(channel.channel_details_v2(token, channel_id))


@APP.route("/channel/join/v2", methods=['POST'])
def join_channel():
    payload = request.get_json()

    return dumps(channel.channel_join_v2(payload["token"], payload["channel_id"]))


@APP.route("/channel/messages/v2", methods=["GET"])
def channel_messages():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id", type=int)
    start = request.args.get("start", type=int)

    return dumps(channel.channel_messages_v2(token, channel_id, start))


@APP.route("/channels/list/v2", methods=['GET'])
def list_joined_channels():
    token = request.args.get("token")

    return dumps(channels.channels_list_v2(token))


@APP.route("/channel/invite/v2", methods=["POST"])
def invite_to_channel():
    payload = request.get_json()

    return dumps(channel.channel_invite_v2(payload["token"], payload["channel_id"], payload["u_id"]))


@APP.route("/channel/addowner/v1", methods=["POST"])
def add_channel_owner():
    payload = request.get_json()

    return dumps(
        channel.channel_addowner_v1(payload["token"], payload["channel_id"], payload["u_id"]
    ))


@APP.route("/channel/removeowner/v1", methods=["POST"])
def remove_channel_owner():
    payload = request.get_json()

    return dumps(
        channel.channel_removeowner_v1(payload["token"], payload["channel_id"], payload["u_id"]
    ))


@APP.route("/channel/leave/v1", methods=["POST"])
def leave_channel():
    payload = request.get_json()

    return dumps(channel.channel_leave_v1(payload["token"], payload["channel_id"]))


@APP.route("/dm/create/v1", methods=["POST"])
def dm_create():
    payload = request.get_json()

    return dumps(dm.dm_create_v1(payload["token"], payload["u_ids"]))


@APP.route("/dm/list/v1", methods=["GET"])
def dm_list():
    token = request.args.get("token")

    return dumps(dm.dm_list_v1(token))


@APP.route("/dm/messages/v1", methods=["GET"])
def dm_messages():
    token = request.args.get("token")
    dm_id = request.args.get("dm_id", type=int)
    start = request.args.get("start", type=int)

    return dumps(dm.dm_messages_v1(token, dm_id, start))


@APP.route("/dm/details/v1", methods=['GET'])
def provide_dm_details():
    token = request.args.get("token")
    dm_id = request.args.get("dm_id", type=int)

    return dumps(dm.dm_details_v1(token, dm_id))


@APP.route("/message/send/v2", methods=["POST"])
def message_send():
    payload = request.get_json()

    return dumps(message.message_send_v2(payload["token"], payload["channel_id"], payload["message"]))


@APP.route("/message/senddm/v1", methods=["POST"])
def message_senddm():
    payload = request.get_json()

    return dumps(message.message_senddm_v1(payload["token"], payload["dm_id"], payload["message"]))


@APP.route("/message/remove/v1", methods=["DELETE"])
def message_remove():
    payload = request.get_json()

    return dumps(message.message_remove_v1(payload["token"], payload["message_id"]))


@APP.route("/message/edit/v2", methods=["PUT"])
def message_edit():
    payload = request.get_json()

    return dumps(message.message_edit_v2(payload["token"], payload["message_id"], payload["message"]))


@APP.route("/message/share/v1", methods=["POST"])
def message_share():
    payload = request.get_json()

    return dumps(message.message_share_v1(
        payload["token"], payload["og_message_id"], payload["message"], payload["channel_id"], payload["dm_id"]))


@APP.route("/message/react/v1", methods=["POST"])
def message_react():
    payload = request.get_json()

    return dumps(message.message_react_v1(payload["token"], payload["message_id"], payload["react_id"]))


@APP.route("/message/unreact/v1", methods=["POST"])
def message_unreact():
    payload = request.get_json()

    return dumps(message.message_unreact_v1(payload["token"], payload["message_id"], payload["react_id"]))

@APP.route("/message/pin/v1", methods=["POST"])
def message_pin():
    payload = request.get_json()

    return dumps(message.message_pin_v1(payload["token"], payload["message_id"]))

@APP.route("/message/unpin/v1", methods=["POST"])
def message_unpin():
    payload = request.get_json()

    return dumps(message.message_unpin_v1(payload["token"], payload["message_id"]))

@APP.route("/message/sendlater/v1", methods=["POST"])
def message_sendlater():
    payload = request.get_json()

    return dumps(message.message_sendlater_v1(
        payload["token"], payload["channel_id"], payload["message"], payload["time_sent"]))

@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def message_sendlaterdm():
    payload = request.get_json()

    return dumps(message.message_sendlaterdm_v1(
        payload["token"], payload["dm_id"], payload["message"], payload["time_sent"]))

@APP.route("/users/all/v1", methods=['GET'])
def list_all_users():
    token = request.args.get("token")

    return dumps(user.users_all_v1(token))


@APP.route("/user/profile/v2", methods=["GET"])
def user_profiles():
    token = request.args.get("token")
    u_id = request.args.get("u_id", type=int)

    return dumps(user.user_profile_v2(token, u_id))


@APP.route("/user/profile/setname/v2", methods=["PUT"])
def user_profile_setname():
    payload = request.get_json()

    return dumps(user.user_profile_setname_v2(payload["token"], payload["name_first"], payload["name_last"]))


@APP.route("/user/profile/setemail/v2", methods=["PUT"])
def user_profile_setemail():
    payload = request.get_json()

    return dumps(user.user_profile_setemail_v2(payload["token"], payload["email"]))


@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def user_profile_sethandle():
    payload = request.get_json()

    return dumps(user.user_profile_sethandle_v1(payload["token"], payload["handle_str"]))


@APP.route("/dm/remove/v1", methods=["DELETE"])
def delete_dm():
    payload = request.get_json()

    return dumps(dm.dm_remove_v1(payload["token"], payload["dm_id"]))


@APP.route("/search/v2", methods=["GET"])
def search_query():
    token = request.args.get("token")
    query_str = request.args.get("query_str")

    return dumps(other.search_v2(token, query_str))


@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def remove_user():
    payload = request.get_json()

    return dumps(user.admin_user_remove_v1(payload["token"], payload["u_id"]))


@APP.route("/dm/leave/v1", methods=["POST"])
def leave_dm():
    payload = request.get_json()

    return dumps(dm.dm_leave_v1(payload["token"], payload["dm_id"]))


@APP.route("/dm/invite/v1", methods=["POST"])
def invite_to_dm():
    payload = request.get_json()

    return dumps(dm.dm_invite_v1(payload["token"], payload["dm_id"], payload["u_id"]))


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def change_user_permission():
    payload = request.get_json()

    return dumps(user.admin_userpermission_change_v1(
        payload["token"], payload["u_id"], payload["permission_id"]
    ))


@APP.route("/notifications/get/v1", methods=["GET"])
def notifications_get():
    token = request.args.get("token")

    return dumps(other.notifications_get_v1(token))


@APP.route("/standup/start/v1", methods=["POST"])
def start_standup():
    payload = request.get_json()

    return dumps(other.standup_start_v1(payload["token"], payload["channel_id"], payload["length"]))


@APP.route("/standup/active/v1", methods=["GET"])
def is_standup_active():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id", type=int)

    return dumps(other.standup_active_v1(token, channel_id))


@APP.route("/standup/send/v1", methods=["POST"])
def send_message_in_standup():
    payload = request.get_json()

    return dumps(other.standup_send_v1(payload["token"], payload["channel_id"], payload["message"]))


if __name__ == "__main__":
    other.update_data_read()
    APP.run(port=config.port) # Do not edit this port
