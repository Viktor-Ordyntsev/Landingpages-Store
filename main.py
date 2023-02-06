from flask import *
from moduls import logic_modul as lm


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/", methods=['GET', 'POST'])
def main_page():
    # Main page
    return render_template('index.html')


@app.route("/success", methods=['POST'])
def upload():
    if request.method == 'POST':
        # Getting data from an HTML form
        file = request.files['landing_zipped_file']
        domain_name = request.form['domain_name']
        name_file = file.filename.split(".")
        
        if (lm.Checking_domain_for_Cyrillic(domain_name)):
            domain_name = lm.Cyrillic_to_Punycode_conversion(domain_name)

        if (lm.Domain_check(domain_name)):
            if (name_file[1] == "zip"):  # We check the extension of the received file and the domain
                file.save(f'./{file.filename}')
                lm.Unzipping(file.filename)
                lm.Removing_service_directory(file.filename)
                # Checking for the existence of an index file
                if lm.Finding_and_changing_index_file(file.filename):
                    if (lm.upoload_to_gitlab(name_file[0], domain_name)):
                        if (lm.delet_local_directory(name_file[0])):
                            flash('File uploaded successfully!', category='info')
                            return redirect(url_for('main_page'))
                        else:
                            flash('Error: Unable to delete local directory', category='error')
                            return redirect(url_for('main_page'))
                    else:
                        flash('Error: Failed to upload to remote repository', category='error')
                        return redirect(url_for('main_page'))
                else:
                    flash('Error: Index file not found! Check if the file has the format "index.html" or "pageXXXXXXX.html"', category='error')
                    return redirect(url_for('main_page'))
            else:
                flash('Error: Invalid file format! Must be a zip archive', category='error')
                return redirect(url_for('main_page'))
        else:
            flash('Error: Invalid domain! Perhaps the DNS record was created incorrectly', category='error')
            return redirect(url_for('main_page'))


if __name__ == "__main__":
    app.run(port=8000, debug=True)