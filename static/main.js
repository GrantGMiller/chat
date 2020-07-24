var lastNotificationTime = Date.now()-100;

function notifyMe(message) {
    // dont send notifications too often
    if (Date.now() - lastNotificationTime < 10){

          // dont send too many notifications
          lastNotificationTime = Date.now();
          console.log('Dont send this message=', message);
        return
    }

  // Let's check if the browser supports notifications
  if (!("Notification" in window)) {
    alert("This browser does not support desktop notification");
  }

  // Let's check whether notification permissions have already been granted
  else if (Notification.permission === "granted") {
    // If it's okay let's create a notification
    var notification = new Notification(message);
  }

  // Otherwise, we need to ask the user for permission
  else if (Notification.permission !== "denied") {
    Notification.requestPermission().then(function (permission) {
      // If the user accepts, let's create a notification
      if (permission === "granted") {
        var notification = new Notification(message);
      }
    });
  }

  // At last, if the user has denied notifications, and you
  // want to be respectful there is no need to bother them any more.

  // dont send too many notifications
  lastNotificationTime = Date.now();
};

//socket = io('ws://localhost:5000');
console.log('window.location=', window.location.host)
socket = io('ws://' + window.location.host);

socket.on('connect', () => {
    console.log('socket io connected');

    // either with send()
    //  socket.send('Hello!');

    // or with emit() and custom event names
    //  socket.emit('salutations', 'Hello!', { 'mr': 'john' }, Uint8Array.from([1, 2, 3, 4]));


    $('#userMessage').keypress(function(event){
        console.log('keypress event=', event);
        if ($('#userMessage').val() && (event.code == "NumpadEnter" || event.code == 'Enter')){
            SubmitMessage($('#userMessage'));
        }
    })

    console.log('thisChannelName=',$('#thisChannelName')[0].innerText )
    socket.emit('join channel', $('#thisChannelName')[0].innerText);

});

var allMessages = [];

function GenerateMessage(data){
    console.log('GenerateMessage(data=', data);
    console.log('allMessages=', allMessages);

    if ($.inArray(data.id, allMessages) > -1){
        console.log('This message has already been displayed on screen');
        return ''
    } else {
        allMessages.push(data.id);
    }
    return `<div class="container">
                <div class="row">
                    <div class="col" style="color:` + data.userColor + `">
                        <b>` + data.userID + `</b>
                    </div>
                    <div class="col">
                        <i>` + data.timestamp + `</i>
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        <p>` + data.text + `</p>
                    </div>
                </div>
            </div>`
}

// handle the event sent with socket.send()
function HandleNewMessage(data){
    data = JSON.parse(data);
    console.log('on message(data=', data);
    console.log('data.userID=', data.userID);
    //add the new message to the message box
    $('#messages').append(GenerateMessage(data));
    ScrollToBottom();
    if (data.userID != $('#userID').val()){
        notifyMe(data.userID + ': ' + data.text);
    }
}
socket.on('message', data => HandleNewMessage(data));

// handle the event sent with socket.emit()
//socket.on('greetings', (elem1, elem2, elem3) => {
//  console.log(elem1, elem2, elem3);
//});

function ScrollToBottom(){
    $('html, body').animate({
                    scrollTop: $('#messages').offset().top + $('#messages').height(),
                }, 100);
}
function SubmitMessage(el){
    console.log('SubmitMessage(el=', el);
    console.log('el.val()=', el.val());
    socket.emit('message', el.val());
    el.val('');
}
function UpdateUserID(){
    console.log('UpdateUserID()');
    let userID = $('#userID').val();
    console.log('userID=', userID);
    $.ajax('/update_userID?userID=' + userID);
}
function CreateNewChannel(){
    let entry = prompt('Enter a name for your new channel:');
    console.log('entry=', entry);
    if (entry){
        window.location.href = '/channel/' + entry;
    };
}