from flask import *
import logic_modul as lm

app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/success", methods = ['POST'])
def upload():
    if request.method == 'POST': 
        f = request.files['landing_zipped_file'] 
        tp = f.filename.split(".")
        if tp[1] == "zip":
            f.save(f"pages/{f.filename}")
            lm.Unzipping(f.filename)
            if lm.index_file_search(f.filename):
                return render_template("index.html", name = f.filename)
        else:
            return render_template("index.html", name = "Файл не правильного формата")

    

if __name__ == "__main__":
    app.run(port=8566)