from flask import *
import logic_modul as lm

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/", methods=['GET', 'POST'])
def main_page():
    # Главная страница
    return render_template('index.html')


@app.route("/success", methods=['POST'])
def upload():
    if request.method == 'POST':
        # Получение данных из HTML-формы
        file = request.files['landing_zipped_file']
        domain_name = request.form['domain_name']
        name_file = file.filename.split(".")
        
        if (lm.Checking_domain_foк_Cyrillic(domain_name)): # Проверяем домен на кирилицу
            domain_name = lm.Cyrillic_to_Punycode_conversion(domain_name)

        if (lm.Domain_check(domain_name)):
            if (name_file[1] == "zip"):  # Проверяем расширение полученного файла и домен
                file.save(f"dist/{file.filename}")
                lm.Unzipping(file.filename)  # Разархивирование

                # Проверка на существование файла индексации
                if lm.Finding_and_changing_index_file(file.filename):
                    if (lm.upoload_to_gitlab(name_file[0])):
                        if (lm.delet_local_directory(name_file[0])):
                            flash('Файл успешно загружен!', category='info')
                            return redirect(url_for('main_page'))
                        else:
                            flash('Ошибка: Невозможно удалить локальную директорию', category='error')
                            return redirect(url_for('main_page'))
                    else:
                        flash('Ошибка: Не удалось загрузить в удаленный репозиторий', category='error')
                        return redirect(url_for('main_page'))

            else:
                flash('Ошибка: Не верный формат файла', category='error')
                return redirect(url_for('main_page'))
        else:
            flash('Ошибка: Не верный домен', category='error')
            return redirect(url_for('main_page'))


if __name__ == "__main__":
    app.run(port=8000, debug=True)
