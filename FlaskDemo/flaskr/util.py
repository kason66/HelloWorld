import os
import uuid

from flask import request, current_app, flash
from werkzeug.utils import redirect


def print_url():
    """
    print the referrer , the url , the base_url , the script_root of request.
    :return: Null
    """
    print('request.referrer:{}\nrequest.url:{}\nrequest.base_url:{}\nrequest.url_root:{}\nrequest.full_path:{}\n'
          'request.path:{}\nrequest.script_root:{}\nrequest.accept_mimetypes:{}'.format
          (request.referrer, request.url, request.base_url, request.url_root, request.full_path, request.path,
           request.script_root, request.accept_mimetypes))


def print_request_data():
    print('request.get_json():{};request.args:{};request.form:{};request.values:{}'.format(
        request.get_json(), request.args, request.form, request.values))
    print('request.data:{}'.format(request.data))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXT']


def upload_save(files=None, url=None):
    if 'file' not in files:
        flash('No file part.')
        return redirect(url)

    file = files['file']
    if file.filename == '':
        flash('No file selected.')
        return redirect(url)

    if file and '.' in file.filename:
        file_ext = file.filename.rsplit('.', 1)[1].lower()
    else:
        flash('No file extends.')
        return redirect(url)

    if file_ext in current_app.config['ALLOWED_EXT']:
        filename = ''.join(str(uuid.uuid1()).split('-')) + '.' + file_ext
        file_url = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_url)
        return file.filename, file_url
    else:
        flash('The type of file should be in {}'.format(current_app.config['ALLOWED_EXT']))
        return redirect(url)
