from flask import Flask, request, jsonify, send_file
from bs4 import BeautifulSoup
import requests
import os
import zipfile
import io

app = Flask(__name__)

def folder_create(images, folder_name):
    try:
        os.mkdir(folder_name)
    except:
        print("Folder Exist with that name!")
    return download_images(images, folder_name)

def download_images(images, folder_name):
    count = 0
    downloaded_images = []
    print(f"Total {len(images)} Image Found!")
    if len(images) != 0:
        for i, image in enumerate(images):
            try:
                image_link = image["data-srcset"]
            except:
                try:
                    image_link = image["data-src"]
                except:
                    try:
                        image_link = image["data-fallback-src"]
                    except:
                        try:
                            image_link = image["src"]
                        except:
                            pass
            try:
                r = requests.get(image_link).content
                try:
                    r = str(r, 'utf-8')
                except UnicodeDecodeError:
                    image_name = f"images{i+1}.jpg"
                    with open(f"{folder_name}/{image_name}", "wb+") as f:
                        f.write(r)
                    downloaded_images.append(image_name)
                    count += 1
            except:
                pass
    return downloaded_images, count

def create_zip_file(images, folder_name):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode='w') as zipf:
        for i, image in enumerate(images):
            if image.endswith('.jpg'):
                zipf.write(os.path.join(folder_name, image), arcname=f'image_{i+1}.jpg')
    return buffer

@app.route('/download-images', methods=['POST'])
def download_images_route():
    url = request.form.get('url')
    folder_name = request.form.get('folder_name', 'images')
    if url:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        images = soup.findAll('img')
        downloaded_images, count = folder_create(images, folder_name)
        
        # create zip file and add images to it
        buffer = create_zip_file(downloaded_images, folder_name)
        
        # check if zip file size is less than 250 MB
        if buffer.tell() > 250 * 1024 * 1024:
            return jsonify({'message': 'Zip file size limit exceeded!'}), 400
        
        # send zip file to client for download
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, attachment_filename=f'{folder_name}.zip')
    else:
        return jsonify({'message': 'Invalid URL!'}), 400

if __name__ == '__main__':
    app.run()
