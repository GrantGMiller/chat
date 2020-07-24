import datetime

from flask_tools import (
    GetApp,
    GetRandomID,
    SetupRegisterAndLoginPageWithPassword,
    VerifyLogin,
    GetUser,
    UserClass,
)
from flask import render_template, session, request, redirect
from flask_socketio import SocketIO, join_room, send, leave_room
from dictabase import New, FindAll, BaseTable, FindOne
import json


class Message(BaseTable):
    def ToDict(self):
        return {
            'text': self['text'],
            'timestamp': str(self['timestamp'].strftime('%Y-%m-%d %H:%M:%S')),
            'userID': self['userID']
        }

    def ToJSON(self):
        ownerUser = FindOne(UserClass, id=self.get('ownerID'))
        if ownerUser is None:
            userColor = f'#{GetRandomID(6)}'
        else:
            userColor = ownerUser.get('userColor', f'#{GetRandomID(6)}')

        return json.dumps({
            'text': self['text'],
            'timestamp': str(self['timestamp'].strftime('%Y-%m-%d %H:%M:%S')),
            'userID': self['userID'],
            'userColor': userColor,
            'id': self['id'],
            'channelName': self['channelName'],
        })


class Channel(BaseTable):
    pass


app = GetApp('Chat')


def NewUserCallback(user):
    user['userColor'] = f'#{GetRandomID(6)}'


SetupRegisterAndLoginPageWithPassword(
    app,
    mainTemplate='main.html',
    callbackNewUserRegistered=NewUserCallback,
    redirectSuccess='/',
)

socketio = SocketIO(app)


@app.route('/')
@VerifyLogin
def Index():
    user = GetUser()

    return redirect('/channel/general')


@app.route('/channel/<channelName>')
@VerifyLogin
def ViewChannel(channelName):
    channelName = channelName.lower()

    user = GetUser()

    if user.get('userID', None) is None:
        user['userID'] = f'{GetRandomID(5)}'

    channel = FindOne(Channel, name=channelName)
    if channel is None:
        channel = New(Channel, name=channelName)

    user['currentChannelName'] = channel['name']

    return render_template(
        'channel.html',
        user=user,
        channels=FindAll(Channel, _orderBy='name'),
        thisChannel=channel,
    )


@socketio.on('connect')
def SocketIOConnect():
    print('SocketIOConnect()')


@socketio.on('join channel')
def SocketIOJoinChannel(channelName):
    print('SocketIOJoinChannel(channelName=', channelName)

    if not channelName:
        channelName = 'general'

    channelName = channelName.lower()

    for channel in FindAll(Channel):
        leave_room(channel['name'])

    print('join_room(channelName=', channelName)
    join_room(channelName)

    user = GetUser()
    user['currentChannelName'] = channelName
    print('117 user=', user)

    for msg in FindAll(
            Message,
            channelName=user['currentChannelName'],
            _limit=100,
            _orderBy='timestamp'
    ):
        send(msg.ToJSON(), room=user['currentChannelName'])


@socketio.on('message')
def ReceiveMessage(message):
    print('ReceiveMessage(message=', message)
    print('session["userID"]=', session['userID'])

    user = GetUser()

    if len(message) == 0:
        print('message is blank, do nothing')
        return

    newMessage = New(
        Message,
        text=message,
        timestamp=datetime.datetime.now(),
        userID=session['userID'],
        ownerID=user['id'],
        channelName=user.get('currentChannelName'),
    )

    print('send(', newMessage.ToJSON(), ', room=', user.get('currentChannelName'))
    send(newMessage.ToJSON(), room=user.get('currentChannelName'))


@app.route('/update_userID')
def UpdateUserID():
    if request.args.get('userID'):
        user = GetUser()
        newUserID = request.args.get('userID')

        userWithID = FindOne(UserClass, userID=newUserID)
        if userWithID and userWithID != user:
            print('There is already another user with this userID')
        else:
            print('This userID is available.')
            session['userID'] = newUserID
            user['userID'] = newUserID

    return session['userID']


if __name__ == '__main__':
    socketio.run(app, host='192.168.68.105', debug=True)
