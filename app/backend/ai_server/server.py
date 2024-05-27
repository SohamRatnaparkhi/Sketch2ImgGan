import json
import os
import shutil

import matplotlib.pyplot as plt
from esrgan import normal_to_esr
from flask import Flask, jsonify, request
from s3 import upload_file_to_s3

from gans import make_prediction

app = Flask(__name__)


@app.route('/')
def index():
    return json.dumps({
        'name': 'alice',
        'email': 'alice@outlook.com'
    })


@app.route('/process', methods=['POST'])
def getGanResult():
    body = json.loads(request.data)
    imagePath = body['imagePath']
    print('imagePath:', imagePath)

    generated_image = make_prediction(imagePath, 'pix2pix')

    fig = plt.imshow(generated_image[0] * 0.5 + 0.5)

    output_file_location = './tmp/output/{}'.format(imagePath.split('/')[-1])
    # plt.imshow(generated_image[0] * 0.5 + 0.5)

    # hide axes and then save image
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig(output_file_location,
                bbox_inches='tight')
    plt.close()

    esr_loc = normal_to_esr(output_file_location)

    s3_link = upload_file_to_s3(esr_loc)

    # final image size
    size = os.path.getsize(esr_loc)

    return json.dumps({
        'outputImagePath': output_file_location,
        'esrImagePath': esr_loc,
        's3Link': s3_link,
        'size': size
    })

@app.route('/clean-server', methods=['DELETE'])
def clean_server():

    shutil.rmtree('./tmp')
    os.makedirs('./tmp/output')
    # os.makedirs('./tmp/esr')

    return json.dumps({
        'message': 'Server cleaned!'
    })

if __name__ == '__main__':
    app.run()
