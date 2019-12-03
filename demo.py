import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from nbconvert import PythonExporter, HTMLExporter
import shutil
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed

from wtforms.validators import DataRequired
from flask_mail import Message, Mail

import json
from bs4 import BeautifulSoup, Tag
import html2text
from flask import send_from_directory
import pdb

# from ..jupyter - notebook - analysis.
from extract_func import process_file
from utils import is_decision_point, download_from_url
from config import data_path
from constants import bootstrap_script, popover_script

UPLOAD_FOLDER = './uploaded_files'
DATA_ROOT = '/projects/bdata/jupyter/target'
ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ipynb', 'html'])

py_exporter = PythonExporter()
html_exporter = HTMLExporter()
html_text_exporter = html2text.HTML2Text()

app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 *  1024 # set the maximize file size after which an upload is aborted
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='gsarazh@gmail.com',
    MAIL_PASSWORD='zg245678',
    MAIL_DEFAULT_SENDER='Ge Zhang <gsarazh@gmail.com>'
))

mail = Mail(app)

with open(os.path.join(data_path, 'alternatives.json'), 'r') as f:
    alt = json.load(f)


class MyForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    feedback = TextAreaField('feedback', validators=[DataRequired()])
    file = FileField('file', validators=[
                     FileRequired(), FileAllowed(["py", "ipynb", "pdf"])])
    # submit = SubmitField('Sign In')


def is_target_element(element, target_line):
    pre_string = ''
    post_string = ''
    cur_element = element.previous_sibling
    while cur_element.string is not None and '\n' not in cur_element.string:
        pre_string = cur_element.string + pre_string
        cur_element = cur_element.previous_sibling
    cur_element = element.next_sibling
    while '\n' not in cur_element.string and cur_element.string is not None:
        post_string = post_string + cur_element.string
        cur_element = cur_element.next_sibling
    code_line = pre_string + element.string + post_string
    return code_line.strip() == target_line.strip()


def remove_script(content):
    """
    remove unwanted scripts from jupyter notebooks html
    Parameters:
    content: html string (content of original notebook html)
    Returns:
    new_content: html string without output jquery 2.xx scripts
    """
    soup = BeautifulSoup(content)
    for t in soup.find_all('script'):
        if t.get("src", "") in ["https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js", "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"]:
            t.decompose()
    return soup.prettify()


def remove_output_from_html(content):
    """
    remove all output blocks from jupyter notebooks html
    Parameters:
    content: html string (content of original notebook html)
    Returns:
    new_content: html string without output blocks
    """
    soup = BeautifulSoup(content)

    for tag in soup.find_all('div', class_='output_wrapper'):
        tag.decompose()

    new_content = soup.prettify()
    return new_content


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.form)
        if 'text' in request.form:
            # raise NotImplementedError
            print(request.form["text"])
            url = request.form["text"]
            filename = download_from_url(url, app.config['UPLOAD_FOLDER'])
            return redirect(url_for('remove_output', filename=filename))
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('remove_output',
                                    filename=filename))
    return '''
    <html lang="en">
    <title>Upload new File</title>
    <a href="../static/README.pdf">README</a>
    <a href="/feedback">Feedback</a>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file >
      <input type=submit value="Upload">
    </form>
    or
    <form method=post>
    <input name=text>
    <input type=submit>
</form>
</html>
    '''


@app.route('/feedback', methods=["POST", "GET"])
def feedback():
    form = MyForm()
    if form.validate_on_submit():
        if '@' not in form.data['email']:
            return redirect('/feedback')
        else:
            print(form.file.data)
            filename = form.file.data.filename
            msg = Message("feedback of jupyter notebook analyses",
                          recipients=["gezhang@cs.washington.edu"])
            msg.body = '''[From] {}\n\n[Feedback] {}'''.format(
                form.email.data, form.feedback.data)
            form.file.data.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            with open(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename), 'r') as f:
                msg.attach(filename, 'application/x-ipynb+json', data=f.read())
            mail.send(msg)
            return '<h3>Sended  email to U! ^^</h3>'
    return render_template('submit.html', form=form)


@app.route('/local/<filename>')
def load_local_file(filename):
    shutil.copyfile(os.path.join(
        '/projects/bdata/jupyter/filtered_notebook', filename), os.path.join(
            app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('remove_output',
                            filename=filename))


@app.route('/remove_output/<filename>')
def remove_output(filename):
    if filename.endswith('.ipynb'):
        # convert ipynb to html
        html_source = html_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        # remove cell output
        html_source = remove_output_from_html(html_source)
        # remove some html codes so that we can add our own elements
        # I'm not sure about why but it works
        html_source = remove_script(html_source)
        # manually import "boostrap" things
        html_source = bootstrap_script + html_source
        # modify opacity so that our own elements are visible
        html_source = html_source.replace('.fade {\n  opacity: 0;',
                                          '.fade {\n  opacity: 90;')
        html_source = html_source.replace('.popover {\n  position: absolute;\n  top: 0;\n  left: 0;\n  z-index: 1060;\n  display: none;',
                                          '.popover {\n  position: absolute;\n  top: 0;\n  left: 0;\n  z-index: 1060;\n  display: block;')
        # add popover function at the bottom of html
        html_source = html_source.replace(
            '</html>', popover_script + '</html>')
        # convert ipynb to py
        py_source = py_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]

        soup = BeautifulSoup(html_source)
        # find decision points and their line numbers
        funcs, linenos = process_file('_', content=py_source)
        code_lines = py_source.split('\n')
        index = 0
        # highlight decision points and add popover windows
        for f, l in zip(funcs, linenos):
            if is_decision_point(f):
                print(f)
                target_line = code_lines[l - 1]
                for i, tag in enumerate(soup.find_all('div', class_='input_area')[index:]):
                    input_content = html_text_exporter.handle(tag.prettify())
                    input_lines = input_content.strip().split('\n')
                    match = False
                    for il in input_lines:
                        if il.strip() == target_line.strip():
                            elements = tag.find_all(
                                'span', text=f.split('.')[-1])
                            for e in elements:
                                if is_target_element(e, target_line):
                                    element = e
                                    break
                            new_element = soup.new_tag('button')
                            new_element.string = f.split('.')[-1]
                            new_element["data-toggle"] = "popover"
                            new_element["data-html"] = "true"
                            new_element["style"] = "background-color:#BEC23F;"
                            new_element["title"] = "Alternatives"
                            new_element["data-content"] = "{}".format(
                                '<br/>'.join(alt[f.split('.')[0]]["similar_sets"][alt[f.split('.')[0]]["func2set"][f]]))
                            element.replaceWith(new_element)
                            match = True
                            break
                    if match:
                        index = i
                        break

        html_source = soup.prettify()

        # dump new html
        with open('./templates/{}'.format(filename.replace('.ipynb', '.html')), 'w') as fout:
            fout.write(html_source)
    else:
        # file not ends with ".ipynb"
        pass
    return render_template(filename.replace('.ipynb', '.html'))


# ======== Unimportant functions ===========


@app.route('/render/<filename>')
def render_html(filename):
    return render_template(filename)


@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')


@app.route('/readme')
def temp():
    return render_template('readme.html')
# ==========================================


if __name__ == '__main__':
    host = '0.0.0.0'
    app.secret_key = 'super secret key'

    debug = True
    app.run(host=host, debug=debug)
