import streamlit as st
from face_recognizer import ImageFolderPersonRecognizer  # Ensure this matches your class name
from PIL import Image, ImageDraw
import os

st.title('Facial Recognition System')

# Initialize or get the existing session state for people
if 'people_identifiers' not in st.session_state:
    st.session_state.people_identifiers = []

# Input for the folder path
folder_path = st.text_input('Enter the path to your images folder:', '')

def refresh_ui():
    # Increment or update a version/timestamp in session_state
    if 'data_last_updated' not in st.session_state:
        st.session_state.data_last_updated = 0
    st.session_state.data_last_updated += 1

if folder_path:
    recognizer = ImageFolderPersonRecognizer(folder_path)
    recognizer.scan_and_recognize()
    # Update session state with the latest people identifiers
    st.session_state.people_identifiers = list(recognizer.people.keys())

    if st.button('Show Recognized Persons'):
        for person, data in recognizer.people.items():
            st.write(f"{person}: {len(data['imgs'])} images")

    selected_person = st.selectbox(
        'Select a person to view or edit:',
        st.session_state.people_identifiers,
        index=0,
        key='person_selector'  # Adding a key to help with re-rendering
    )

    if selected_person and recognizer.people[selected_person]:
        # Display a selectbox with image paths as options
        image_paths = [img_data["path"] for img_data in recognizer.people[selected_person]['imgs']]
        selected_image_path = st.selectbox(
            f"Select an image for {selected_person}:",
            options=image_paths,
            index=0,  # Default to the first image
            format_func=lambda x: os.path.basename(x)  # Optionally, format the displayed options to just show filenames
        )

        # Find the image data for the selected image path
        img_data = next((img for img in recognizer.people[selected_person]['imgs'] if img["path"] == selected_image_path), None)
        if img_data:
            face_location = tuple(img_data["location"])
            image = Image.open(selected_image_path)
            if face_location:
                top, right, bottom, left = face_location
                draw = ImageDraw.Draw(image)
                draw.rectangle(((left, top), (right, bottom)), outline="red", width=3)
            st.image(image, caption=f"Selected image of {selected_person}", use_column_width=True)

        old_identifier = st.text_input(
            'Enter the identifier to change (e.g., Person_1):',
            value=selected_person,
            key='old_identifier'
        )
        new_name = st.text_input('Enter the new name:', key='new_name')

        if st.button('Update Identifier'):
            recognizer.update_person_identifier(old_identifier, new_name)
            refresh_ui()  # Signal that the UI needs to refresh
            st.success(f'Updated {old_identifier} to {new_name}')
            # Refresh UI components that depend on people_identifiers
            st.rerun()

        if st.button('Add Person Name to EXIF'):
            recognizer.add_person_name_to_exif(selected_person)
            st.success(f'Added person name to EXIF for {selected_person}')
            st.write(recognizer.get_image_exif_info(selected_image_path))
