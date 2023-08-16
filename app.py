from flask import Flask, render_template, request, redirect, Response
from pyflipdot.sign import HanoverSign
from drawtext import Text, parse_messages
import os

app = Flask(__name__)

sign = HanoverSign(address=1, width=84, height=7)

def render_message(text):
    rendered = ""
    for row in Text(text).render(sign):
        for col in row:
            rendered += "█" if col else " "
        rendered += "\n"
    return rendered

def write_messages(messages):
    with open("messages.txt", "w") as f:
        for message in messages:
            f.write("%s;%s\n" % (message[0], message[1]))

@app.route('/flipdot', methods=('GET', 'POST'))
def index():
    error = ""
    if request.method == 'POST':
        raw_messages = request.form['messages']
        previews = []
        try:
            parsed_messages = parse_messages(raw_messages)
        except Exception as e:
            print(e)
            error = "NO. Bad format. Use good format."
            pass

        try:
            previews = [render_message(item[0]) for item in parsed_messages]
        except Exception as e:
            print(e)
            error = "NO. Messages too long. Use less characters."
            pass

        if not error:
            write_messages(parsed_messages)
            return redirect("/flipdot", code=302)

    else:
        raw_messages = open("messages.txt").read()
        try:
            messages = parse_messages(raw_messages)
            previews = [render_message(item[0]) for item in messages]
        except Exception as e:
            print(e)
            return Response(
                response='messages.txt is invalid', status=200,  mimetype="text/plain"
            )

    return render_template('index.html', messages=raw_messages, previews=previews, error=error)

@app.route('/images')
def images():
    return render_template('images.html')


@app.route('/images/list')
def list_images():
    images = []
    for name in os.listdir('images'):
        image = {"name": name.split('.')[0]}
        with open("images/%s" % name) as f:
            image['content'] = f.read()
        images.append(image)
    return {"images": images}

@app.route('/images/image/<name>', methods=('DELETE', 'PUT'))
def modify_image(name):
    if request.method == 'PUT':
        with open("images/%s.txt" % name, 'w') as f:
            content = "\n".join([
                "".join(["░" for _ in range(84)])
                for _ in range(7)
            ])
            if 'content' in request.form:
                content = request.form['content']
            f.write(content)
    if request.method == 'DELETE':
        os.remove("images/%s.txt" % name)
    return list_images()
