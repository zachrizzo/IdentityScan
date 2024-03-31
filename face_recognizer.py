import face_recognition
import os
from collections import defaultdict
import piexif
import json
import numpy as np
from PIL import Image
from PIL import PngImagePlugin

class ImageFolderPersonRecognizer:
    def __init__(self, folder_path, data_file='people_data.json'):
        self.folder_path = folder_path
        self.data_file = data_file  # Path to the JSON file where data will be stored
        self.people = self.load_people_data()  # Load people data from file

    def scan_and_recognize(self):
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if not filename.lower().endswith(('jpg', 'jpeg', 'png')):
                    continue

                image_path = os.path.join(root, filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                face_locations = face_recognition.face_locations(image)

                for encoding, face_location in zip(face_encodings, face_locations):
                    match_found = False
                    for name, data in self.people.items():
                        if face_recognition.compare_faces([data['encoding']], encoding)[0]:
                            match_found = True
                            if not any(img['path'] == image_path for img in data['imgs']):
                                data['imgs'].append({"path": image_path, "location": face_location})
                            break

                    if not match_found:
                        name = f"Person_{len(self.people) + 1}"
                        self.people[name] = {
                            'imgs': [{"path": image_path, "location": face_location}],
                            'encoding': encoding
                        }

        self.save_people_data()

    def save_people_data(self):
        serializable_data = {
            name: {
                'imgs': [{'path': img['path'], 'location': img['location']} for img in data['imgs']],
                'encoding': data['encoding'].tolist()
            } for name, data in self.people.items()
        }

        with open(self.data_file, 'w') as json_file:
            json.dump(serializable_data, json_file, indent=4)

    def load_people_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                json_load = json.load(file)
                self.people = {
                    k: {
                        'imgs': [{'path': img_data['path'], 'location': tuple(img_data['location'])} for img_data in v['imgs']],
                        'encoding': np.array(v['encoding'])
                    } for k, v in json_load.items()
                }
        else:
            self.people = {}

        return self.people



    def update_person_identifier(self, old_identifier, new_identifier):
        if old_identifier in self.people:
            self.people[new_identifier] = self.people.pop(old_identifier)
            self.save_people_data()  # Save changes to file

    def _convert_png_to_jpeg(self, image_path):
        img = Image.open(image_path)
        rgb_im = img.convert('RGB')
        jpeg_path = image_path.rsplit('.', 1)[0] + '.jpeg'
        rgb_im.save(jpeg_path, 'JPEG')
        os.remove(image_path)  # Optionally remove the original PNG file
        return jpeg_path

    def add_person_name_to_exif(self, person_name):
        if person_name in self.people:
            for img_data in self.people[person_name]['imgs']:
                img_path = img_data['path']
                self._edit_image_metadata(img_path, person_name)

    def _edit_image_metadata(self, img_path, person_name):
        try:
            img = Image.open(img_path)
            exif_dict = piexif.load(img.info['exif']) if 'exif' in img.info else {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}

            # Get the existing ImageDescription
            image_description = exif_dict['0th'].get(piexif.ImageIFD.ImageDescription, b'').decode('utf-8')

            # Check if the person_name already exists in the ImageDescription
            if person_name not in image_description:
                # Append the new person_name to the existing ImageDescription
                if image_description:
                    image_description += '; ' + person_name
                else:
                    image_description = person_name

                # Update the ImageDescription in the EXIF dictionary
                exif_dict['0th'][piexif.ImageIFD.ImageDescription] = image_description.encode('utf-8')
                exif_bytes = piexif.dump(exif_dict)
                img.save(img_path, 'JPEG', exif=exif_bytes)
                print(f"Updated metadata for {img_path} with {person_name}")
            else:
                print(f"{person_name} already exists in the metadata for {img_path}")
        except Exception as e:
            print(f"Could not update metadata for {img_path}: {e}")

    def get_image_exif_info(self, img_path):
        try:
            img = Image.open(img_path)
            exif_dict = piexif.load(img.info['exif']) if 'exif' in img.info else None
            if exif_dict:
                # Fetching the ImageDescription specifically
                image_description = exif_dict['0th'].get(piexif.ImageIFD.ImageDescription, b'').decode('utf-8')
                return {'ImageDescription': image_description, 'AllExif': exif_dict}
            else:
                return {'Error': 'No EXIF data found'}
        except Exception as e:
            print(f"Could not load EXIF data for {img_path}: {e}")
            return {'Error': str(e)}



