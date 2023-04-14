
from flask import Flask, request, jsonify
from bs4 import *
import requests
import os

app = Flask(__name__)
def folder_create(images, folder_name):
    try:
        os.mkdir(folder_name)
    except:
        print("Folder Exist with that name!")
        folder_create()
    download_images(images, folder_name)
def download_images(images, folder_name):
    count = 0
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
                    with open(f"{folder_name}/images{i+1}.jpg", "wb+") as f:
                        f.write(r)
                    count += 1
            except:
                pass
        if count == len(images):
            print("All Images Downloaded!")
        else:
            print(f"Total {count} Images Downloaded Out of {len(images)}")

@app.route('/download-images', methods=['POST'])
def download_images_route():
    url = request.form.get('url')
    folder_name = request.form.get('folder_name', 'images')
    if url:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        images = soup.findAll('img')
        folder_create(images, folder_name)
        return jsonify({'message': 'Images downloaded successfully!'})
    else:
        return jsonify({'message': 'Invalid URL!'}), 400

if __name__ == '__main__':
    app.run()