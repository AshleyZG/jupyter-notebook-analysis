import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from nbconvert import PythonExporter


import json

# from ..jupyter - notebook - analysis.
from extract_func import process_file
from utils import is_decision_point
from config import data_path

UPLOAD_FOLDER = './myflask/uploaded_files'
DATA_ROOT = '/projects/bdata/jupyter/target'
ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ipynb', 'html'])

exporter = PythonExporter()


app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 *  1024 # set the maximize file size after which an upload is aborted
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


with open(os.path.join(data_path, 'alternatives.json'), 'r') as f:
    alt = json.load(f)


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
            return redirect(url_for('uploaded_file',
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
        source = exporter.from_file(os.path.join(
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
        source = exporter.from_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))[0]
        with open(os.path.join(
                app.config['UPLOAD_FOLDER'], filename.replace('.ipynb', '.py')), 'w') as fout:
            fout.write(source)
    elif filename.endswith('.py'):
        with open(os.path.join(
                DATA_ROOT, filename), 'r') as f:
            source = f.read()
    else:
        raise ValueError('file must be ipynb or py scripts')
    funcs, linenos = process_file('_', content=source)
    code_lines = source.split('\n')
    for f, l in zip(funcs, linenos):
        print(f)
        if is_decision_point(f):
            code_lines[l - 1] = '<span href="#" data-toggle="popover" data-html="true" style="color:red" title="Alternatives" data-content="{}">'.format(
                '<br/>'.join(alt[f.split('.')[0]]["similar_sets"][alt[f.split('.')[0]]["func2set"][f]])) + code_lines[l - 1].strip() + '</span>'

    source = '\n'.join(code_lines)
    with open('./templates/my.html', 'w') as fout:
        fout.write(source)
    return render_template('alt.html')


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
