from sql import carworkinvSQL
from flask import Flask, render_template, request
from config.config import devConfig

isDev = True

app = Flask(__name__)
app.config.from_object(devConfig)
test = None
if app.config["DEV"]:
    pass
elif app.config["TEST"]:
    test = carworkinvSQL.testSQL()

@app.route('/')
def main_page():
    if app.config["DEV"]:
        test = carworkinvSQL.testSQL()
        result = test.executeAndCommitSQLStatement("SELECT * FROM test")
        return render_template('index.html', sqlTest=result.fetchall())
    else:
        return render_template('index.html')

@app.post('/')
def main_page_post():

    return render_template('index.html')