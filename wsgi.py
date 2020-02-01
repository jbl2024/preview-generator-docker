#!/usr/bin/env python

import json
import logging
import tempfile
import os

from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import HTTPException

from preview_generator.manager import PreviewManager
from preview_generator.exception import InputExtensionNotFound
app = Flask('preview')

def handle_error(error):
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    return jsonify(error=error.description, code=code)


for cls in HTTPException.__subclasses__():
    app.register_error_handler(cls, handle_error)


@app.route('/health')
def index():
    return 'ok'

@app.route('/version')
def version_index():
    return weasyprint.__version__


@app.before_first_request
def setup_logging():
    logging.addLevelName(logging.DEBUG, "\033[1;36m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


@app.route('/')
def home():
    return '''
        <h1>Preview Generator</h1>
        <p>The following endpoints are available:</p>
        <ul>
            <li>POST to <code>/preview?filename=myfile.pdf</code>. The body should
                contain data</li>
        </ul>
    '''


@app.route('/preview', methods=['POST'])
def generate():
    name = request.args.get('filename', 'unnamed')
    app.logger.info('POST  /preview?filename=%s' % name)

    data = request.data
    with tempfile.TemporaryDirectory() as tmpdirname:
      input_path = os.path.join(tmpdirname, name)
      file = open(input_path, 'w+b')
      file.write(data)
      file.close() 

      cache_path = os.path.join(tmpdirname, 'cache')
      try:
          manager = PreviewManager(cache_path, create_folder= True)
          output_path = manager.get_jpeg_preview(input_path)

          file = open(output_path, 'r+b')
          output = file.read()
          response = make_response(output)
          response.headers['Content-Type'] = 'image/jpeg'
          response.headers['Content-Disposition'] = 'inline;filename=%s' % output_path
          app.logger.info(' ==> POST  /preview?filename=%s  ok' % output_path)
          return response
      except InputExtensionNotFound as error:
          return jsonify(error=repr(error), code=400), 400
      except Exception as error:
          return jsonify(error=repr(error), code=400), 400

if __name__ == '__main__':
    app.run()
