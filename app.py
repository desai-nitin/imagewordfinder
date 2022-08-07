import os
from flask import Flask, flash, request, redirect, url_for, render_template, make_response,flash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_caching import Cache
from fuzzywuzzy import fuzz
import cv2

# import our OCR functions
from ocr_core import ocr_core,ocr_hocr

# define a folder to store and later serve the images
#UPLOAD_FOLDER = '/home/shrinivas/Nitin.Desai/ocr/app/static/uploads/'
UPLOAD_FOLDER = 'static//uploads//'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__,template_folder='template')

app.config["SECRET_KEY"] = "mysecretkey"
app.config["CACHE_TYPE"] = "SimpleCache" # better not use this type w. gunicorn
cache = Cache(app)

# Set Upload Folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# function to get the file extension
def get_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() 

# route and function to handle the home page
@app.route('/')
def home_page():
    return render_template('upload.html')

# route and function to handle the upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            flash('No file selected','warning')
            return render_template('upload.html')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            flash('No file selected','warning')
            return render_template('upload.html')

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            # call the OCR function on it
            extracted_data = ocr_hocr(file)
            filename=file.filename
            extracted_text = " ".join(extracted_data['text'])
            cache.set("filename",filename)
            cache.set("extracted_data", extracted_data)
            cache.set("extracted_text",extracted_text)
            flash('Successfully processed','success')
            return render_template('upload.html',
                                   extracted_text=extracted_text,
                                   img_src=UPLOAD_FOLDER + file.filename,
                                   img_name=filename)
            #return render_template('upload.html',msg='Successfully processed',extracted_text=extracted_text,filename=filename)
                
    elif request.method == 'GET':
        return render_template('upload.html')

@app.route('/display/<filename>')
def display_image(filename,msg="Default Msg",extracted_text="Default Text"):
    
    return redirect(url_for('static', filename='uploads/' + filename),msg=msg,extracted_text=extracted_text, code=301)

@app.route('/SearchText', methods=['GET'])
def search_image_text():
    args = request.args.to_dict()
    s_string = args["Search"]
    extracted_text = cache.get("extracted_text")
    print(extracted_text)
    
    extracted_data = cache.get("extracted_data")
    filename = cache.get("filename")
    d = extracted_data.copy()
    # Drawing box for search word
    n_boxes = len(d['level'])
    img = cv2.imread(UPLOAD_FOLDER+filename)
    overlay = img.copy()
    ext = get_file_extension(filename)
    alpha = 0.4
    
    for i in range(n_boxes):
        text = d['text'][i]
        
        if fuzz.partial_ratio(text.lower(),s_string.lower())>90:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), -1)            
            
#             (x1, y1, w1, h1) = (d['left'][i + 1], d['top'][i + 1], d['width'][i + 1], d['height'][i + 1])
#             (x2, y2, w2, h2) = (d['left'][i + 2], d['top'][i + 2], d['width'][i + 2], d['height'][i + 2])
#             # cv2.rectangle(img, (x, y), (x1 + w1, y1 + h1), (0, 255, 0), 2)
#             cv2.rectangle(overlay, (x, y), (x1 + w1, y1 + h1), (255, 0, 0), -1)
#             # cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
#             cv2.rectangle(overlay, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), -1)
#             print(text)
    
    # Following line overlays transparent rectangle over the image
    img_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    r = 1000.0 / img_new.shape[1]  # resizing image without loosing aspect ratio
    dim = (1000, int(img_new.shape[0] * r))
    # perform the actual resizing of the image and show it
    resized = cv2.resize(img_new, dim, interpolation=cv2.INTER_AREA)

    retval, buffer = cv2.imencode("."+ext, resized)
    response = make_response(buffer.tobytes())
    response.headers['Content-Type'] = 'image/'+ext
    
    #render_template('upload.html')
    return response
        

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)