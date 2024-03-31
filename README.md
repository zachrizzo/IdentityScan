# Facial Recognition System

A simple facial recognition system built with Streamlit, `face_recognition`, and `PIL`, designed to recognize and manage faces in images.

## Features

- Scans a specified folder for images and recognizes faces.
- Stores recognized face data in a JSON file for persistence.
- Allows updating person identifiers and adding names to image EXIF data.
- Visualizes recognized faces and their information through a Streamlit interface.

## Installation

Ensure you have Python installed on your system. This application was developed and tested with Python 3.8.

Clone this repository:

git clone https://yourrepositoryurl.com

csharp
Copy code

Navigate into the project directory:

cd facial_recognition_system

mathematica
Copy code

Install the required dependencies:

pip install -r requirements.txt

shell
Copy code

## Running the Application

To run the application, execute:

streamlit run app.py

vbnet
Copy code

Replace `app.py` with the main,py to run your application script

## Usage

1. Enter the path to your images folder when prompted.
2. The application will scan the folder, recognize faces, and display recognized persons.
3. You can view, update identifiers, and add person names to the EXIF data of the images.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-sourced under the MIT License.
