from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from PIL import Image
from random import seed, choices
from string import ascii_letters, digits
import gunicorn

app = Flask(__name__)
CORS(app)
api = Api(app)
alowed = 'png jpg jpeg x-icon bmp'.split(' ')
seed('Dobar dan')
api_key = ''.join(choices(ascii_letters+digits,k=32))
def check_api_key(key):
    return key == api_key
def brojac(img_data):
    img = Image.open(img_data)
    w, h = img.size
    l = list(img.getdata())
    k = list(dict.fromkeys(l))
    k = {i:0 for i in k}
    for i in l:
        k[i] += 1
    sve = sorted([[i, j] for j, i in k.items()], reverse=True)
    boja = sve[0][1]
    if isinstance(boja, int):
        boja = [boja]*3
    if len(boja) == 4:
        boja = boja[:3]
    R,G,B = boja
    Y = 0.299*R+0.587*G+0.114*B
    text = 'white' if Y<128 else 'black'
    boja = '#'+''.join([f'{i:02x}' for i in boja])
    #print('OK')
    return text,w,h,boja
def check_filetype(x):
    x = x.split('/')[-1].split("'")[0]
    return True if x in alowed else False
class DominantColor(Resource):
    def post(self):
        if 'api_key' not in request.headers:
            return {'error': 'No API key provided'}, 401

        # Check if the API key is valid
        api_key = request.headers['api_key']
        if not check_api_key(api_key):
            return {'error': 'Invalid API key'}, 401
        check = check_filetype(str(request.files['image']))
        # Check if an proper image file was uploaded
        if not check: return {'error': 'No image file provided'}, 400

        # Open the image file and get the dominant color
        image = request.files['image']
        size = f'{len(image.read())/1024:.2f}'
        text,w,h,dominant_color = brojac(image)
        dc = jsonify({'hex_code': dominant_color,'size':size,'wh':f'{w}x{h}','text':text})
        return dc

api.add_resource(DominantColor, '/dominant-color')

if __name__ == '__main__':
    app.run()

