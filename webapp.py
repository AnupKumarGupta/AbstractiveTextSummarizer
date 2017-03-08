from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def default():
    return render_template('index.html')


@app.route('/home')
def home():
   return render_template('index.html')


@app.route('/summ')
def summ():
   return render_template('summ.html')


@app.route('/summarize', methods=['POST', 'GET'])
def func():
    #article = request.form['textarea_article']
    return render_template('summ.html')


@app.route('/result', methods=['POST', 'GET'])
def functio():
    if request.method == 'POST':
        article = request.form['textarea_article']
        #
        # INSERT LOGIC HERE
        #
        return render_template('summ.html', abstract=article)
    else:
        return "Not done"

if __name__ == '__main__':
   app.run(debug = True)


