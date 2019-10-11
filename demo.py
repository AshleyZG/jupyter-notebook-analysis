import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from nbconvert import PythonExporter, HTMLExporter


import json
from bs4 import BeautifulSoup


# from ..jupyter - notebook - analysis.
from extract_func import process_file
from utils import is_decision_point
from config import data_path

UPLOAD_FOLDER = './uploaded_files'
DATA_ROOT = '/projects/bdata/jupyter/target'
ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ipynb', 'html'])

py_exporter = PythonExporter()
html_exporter = HTMLExporter()

app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 *  1024 # set the maximize file size after which an upload is aborted
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


with open(os.path.join(data_path, 'alternatives.json'), 'r') as f:
    alt = json.load(f)


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
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


from flask import send_from_directory


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if filename.endswith('.ipynb'):
        source = py_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        with open(os.path.join(
                app.config['UPLOAD_FOLDER'], filename.replace('.ipynb', '.py')), 'w') as fout:
            fout.write(source)
    elif filename.endswith('.py'):
        with open(os.path.join(
                app.config['UPLOAD_FOLDER'], filename), 'r') as f:
            source = f.read()
    else:
        raise ValueError('file must be ipynb or py scripts')
    funcs, linenos = process_file('_', content=source)
    code_lines = source.split('\n')
    for f, l in zip(funcs, linenos):
        print(f)
        if is_decision_point(f):
            code_lines[l - 1] = '<span style="color:red">' + \
                code_lines[l - 1].strip() + '</span>'
    source = '\n'.join(code_lines)
    with open('./templates/my.html', 'w') as fout:
        fout.write(source)
    return render_template('content.html')


@app.route('/alt/<filename>')
def open_alt_file(filename):
    if filename.endswith('.ipynb'):
        py_source = py_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        html_source = html_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        html_source = remove_output_from_html(html_source)
        with open(os.path.join(
                app.config['UPLOAD_FOLDER'], filename.replace('.ipynb', '.py')), 'w') as fout:
            fout.write(py_source)
    elif filename.endswith('.py'):
        with open(os.path.join(
                DATA_ROOT, filename), 'r') as f:
            py_source = f.read()
    else:
        raise ValueError('file must be ipynb or py scripts')
    funcs, linenos = process_file('_', content=py_source)
    code_lines = py_source.split('\n')
    for f, l in zip(funcs, linenos):
        print(f)
        if is_decision_point(f):
            code_lines[l - 1] = '<span href="#" data-toggle="popover" data-html="true" style="color:red" title="Alternatives" data-content="{}">'.format(
                '<br/>'.join(alt[f.split('.')[0]]["similar_sets"][alt[f.split('.')[0]]["func2set"][f]])) + code_lines[l - 1].strip() + '</span>'

    py_source = '\n'.join(code_lines)
    with open('./templates/my.html', 'w') as fout:
        fout.write(html_source)
    return render_template('content.html')


@app.route('/remove_output/<filename>', methods=['GET'])
def remove_output(filename):

    if filename.endswith('.ipynb'):
        html_source = html_exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        html_source = remove_output_from_html(html_source)
        print(filename)
        with open('./templates/{}'.format(filename.replace('.ipynb', 'html')), 'w') as fout:
            fout.write(html_source)
    else:
        pass
    return render_template(filename.replace('.ipynb', 'html'))


@app.route('/render/<filename>')
def render_html(filename):
    return render_template(filename)


@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')


if __name__ == '__main__':
    host = '0.0.0.0'
    debug = True
    app.run(host=host, debug=debug)
