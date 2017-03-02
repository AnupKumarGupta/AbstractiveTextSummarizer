from flask import Flask, render_template, request

app = Flask(__name__)


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
        return render_template('summ.html', abstract=article)
    else:
        return "Not done"

# def summarize():
#    if request.method == 'POST':
#       article = request.form['textarea_article']
#       return render_template('summarize.html', abstract = article)

if __name__ == '__main__':
   app.run(debug = True)


