from flask import Flask, redirect, request, render_template, url_for, send_file, make_response
import secrets
import os
import time
import qrcode


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
user_list = []


@app.get("/")
def home():
    # If there is no cookies need to get them
    if not request.cookies.get('cookie_user'):
        return render_template("home-post.html")
    # If there is already cookies on the browser return the home-get.html
    else:
        return render_template("home-get.html")




@app.post("/")
def home_post():
    # If user has been requested
    if request.form['user']:
        # If user is not elected already
        if request.form['user'] not in user_list:
            # Create a cookie for the user
            resp = make_response(render_template("home-get.html"))
            # Cookie for 20 minutes
            tok = secrets.token_urlsafe(16)
            resp.set_cookie("cookie_user", tok, max_age=60*20)
            
            # add user to session
            user_list.append(request.form['user'])
            print(user_list)
            # redirect to the home-get page 
            return resp
        # user in user_list
        else:
            return "error"
    # user not requested
    else:
        return render_template("home-post.html")
            

# Create a room
@app.route("/create/", methods=['GET'])
def create():
    number = secrets.token_urlsafe(128)
    new_file_room = open(f"{os.getcwd()}/chats/room.{number}.txt", "w")
    new_file_room.write("")
    new_file_room.close()
    return redirect(f"/room/{number}")




@app.route("/join/", methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template("join-get.html")
    if request.method == 'POST':
        return redirect(f"/room/{request.form.get('room_key')}")


# Die Nachricht
@app.get("/room/<string:number>/")
def room_get(number):
    if os.path.isfile(f"{os.getcwd()}/chats/room.{number}.txt"):
        content_mes = open(f"{os.getcwd()}/chats/room.{number}.txt", "r", encoding='utf-8').read()
        title = f"{number[:6]}...{number[-6:]}"
        msg_list = content_mes.split('\n') if content_mes else None
        return render_template("Pizza Chat.html", title=title, msg_list=msg_list, room_key=number)
    else:
        return "Couldnt connect to Pizza Chat"


# Poste eine Nachricht
@app.post("/room/<string:number>/")
def room_post(number):
    content_room = open(f"{os.getcwd()}/chats/room.{number}.txt", "a", encoding='utf-8')
    if request.form['message']:
        time_msg = f"[{time.localtime().tm_hour}:{time.localtime().tm_min}.{time.localtime().tm_sec}]"
        content_room.write(f"{time_msg} - *{request.cookies.get('cookie_user')}*: {request.form['message']}\n")
    return redirect(url_for("room_get", number=number))


# QR Code
@app.get("/room/<string:number>/qr/")
def room_get_qr(number):

    if os.path.isfile(f"{os.getcwd()}/qrs/{number}.png"):
        return send_file(f"{os.getcwd()}/qrs/{number}.png")

    else:
        qr_img = qrcode.make(f"localhost/room/{number}/")
        qr_img.save(f"{os.getcwd()}/qrs/{number}.png")
        return send_file(f"{os.getcwd()}/qrs/{number}.png")




if __name__ == "__main__":
    os.chdir(os.getcwd())
    app.run(host="0.0.0.0", port=80, debug=True)
