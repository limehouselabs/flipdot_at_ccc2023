from flask import Flask, render_template, request, redirect
from pyflipdot.sign import HanoverSign
from drawtext import Text, parse_messages

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
        messages = parse_messages(raw_messages)
        previews = [render_message(item[0]) for item in messages]

    return render_template('index.html', messages=raw_messages, previews=previews, error=error)

@app.route('/images')
def images():
    return render_template('images.html')
