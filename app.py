# Imports
import streamlit as st
from videopluxtext.translate import TranslateMassage as Translator
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile
from io import BytesIO
import textwrap
import asyncio

# Class Definition
class FullProcess:
    def __init__(self):
        self.translator = Translator()
        self._pipeline_initialized = False

    def initialize_pipeline(self):
        if not self._pipeline_initialized:
            asyncio.run(self.translator.load_pipline())
            self._pipeline_initialized = True

    def main(self):
        st.title("Video Overlay App")
        st.write("Upload a video and add multiple text overlays in multiple languages!")

        # Function to get video duration
        def get_video_duration(uploaded_file):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Write the uploaded file to the temporary file
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name
            
            # Load video and get duration
            video = VideoFileClip(temp_file_path)
            duration = video.duration  # Duration in seconds
            return duration

        # File uploader for video
        uploaded_file = st.file_uploader("Choose a video", type=["mp4", "mov", "avi"])

        if uploaded_file is not None:
            # Get video duration
            duration = get_video_duration(uploaded_file)
            st.write(f"Video Duration: {duration} seconds")

            # Initialize session state for text-caption pairs
            if "text_caption_pairs" not in st.session_state:
                st.session_state.text_caption_pairs = []

            # Section 1: Language Selection
            st.subheader("Number of Text want on video")
            num_combo = st.number_input(
                "How many languages do you want to select for each entry?", min_value=1, max_value=50, value=1, step=1
            )

            st.subheader("Select Text Language Pairs")
            language_options = ["English", "Hindi", "Bengali", "Gujarati", "Marathi", "Maithili", "Malayalam", "Tamil", "Telugu"]

            langs = []
            cols = st.columns(num_combo)
            for i, col in enumerate(cols, start=1):
                with col:
                    lang = st.selectbox(
                        f"Select Language {i}", language_options, key=f"lang_{i}"
                    )
                    langs.append(lang)

            if st.button("Add Languages"):
                st.session_state.text_caption_pairs.append(tuple(langs))
                st.success("Languages added successfully!")
                st.session_state.refresh = True

            # Display existing pairs dynamically
            st.subheader("Existing Text Language Pairs")
            for i, pair in enumerate(st.session_state.text_caption_pairs):
                num_languages = len(pair)  # Get the number of languages in the current pair
                language_labels = [f"Language {j+1}: {lang}" for j, lang in enumerate(pair)]
                
                # Display dynamically based on number of languages
                cols = st.columns(num_languages + 1)  # Add an extra column for the remove button
                for idx, (col, label) in enumerate(zip(cols[:-1], language_labels)):
                    with col:
                        st.write(label)
                
                # Remove button in the last column
                with cols[-1]:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.text_caption_pairs.pop(i)
                        st.session_state.refresh = True  # Flag to trigger page refresh

            # Refresh logic based on the flag
            if st.session_state.get("refresh"):
                del st.session_state.refresh  # Clean up the flag

            # Section 3: Text Overlay Configuration
            st.header("Text Overlay Configuration")

            def get_text_overlay_input(num, duration):  # Add 'duration' as a parameter
                st.subheader(f"Text Overlay {num}")

                col1, col2 = st.columns(2)
                with col1:
                    font_size = st.selectbox(
                        f"Select Font Size for Text {num}", 
                        [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120], 
                        index=4, 
                        key=f"font_size{num}"
                    )
                with col2:
                    color = st.color_picker(f"Pick a Color for Text {num}", "#FFFFFF", key=f"color{num}")

                col1, col2 = st.columns(2)
                with col1:
                    relative_x = st.slider(f"Text Overlay X Position {num} (0-1)", 0.0, 1.0, 0.5, step=0.05, key=f"relative_x{num}")
                with col2:
                    relative_y = st.slider(f"Text Overlay Y Position {num} (0-1)", 0.0, 1.0, 0.5, step=0.05, key=f"relative_y{num}")

                col1, col2 = st.columns(2)
                with col1:
                    text_start_time = st.slider(f"Text Start Time {num} (0-{duration})", 0.0, duration, 2.0, step=1.0, key=f"text_start_time{num}")
                with col2:
                    text_duration = st.slider(f"Text Duration {num} (0-{duration})", 0.0, duration, 2.0, step=1.0, key=f"text_duration{num}")

                text_input = st.text_area(f"Enter Text to Overlay {num}", key=f"text_input{num}")

                return {
                    "text": text_input,
                    "font_size": font_size,
                    "color": color,
                    "relative_x": relative_x,
                    "relative_y": relative_y,
                    "start_time": text_start_time,
                    "duration": text_duration,
                }

            # Pass the 'duration' to the function when calling it
            overlay_data = [get_text_overlay_input(i, duration) for i in range(1, num_combo + 1)]

            # Section 4: Process Video
            if st.button("Process Video"):
                if uploaded_file and overlay_data and st.session_state.text_caption_pairs:
                    try:
                        self.initialize_pipeline()

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                            temp_file.write(uploaded_file.read())
                            temp_file_path = temp_file.name

                        video = VideoFileClip(temp_file_path)

                        font_map = {
                            "Hindi": r"fonts\\DevanagariSangamMN.ttc",
                            "Bengali": r"fonts\\NotoSerifBengali-VariableFont_wdth,wght.ttf",
                            "Tamil": r"fonts\\NotoSansTamil-VariableFont_wdth,wght.ttf",
                            "Telugu": r"fonts\\NotoSansTelugu-VariableFont_wdth,wght.ttf",
                            "Gujarati": r"fonts\\NotoSansGujarati-VariableFont_wdth,wght.ttf",
                            "Marathi": r"fonts\\TiroDevanagariMarathi-Regular.ttf",
                            "Maithili": r"fonts\\DevanagariSangamMN.ttc",
                            "Malayalam": r"fonts\\NotoSansMalayalam-VariableFont_wdth,wght.ttf",
                            "English": r"fonts\\NotoSans-VariableFont_wdth,wght.ttf"
                        }

                        for langs in st.session_state.text_caption_pairs:
                            overlays = []
                            for idx, lang in enumerate(langs):
                                overlay = overlay_data[idx]
                                translated_text = self.translator.translate_input(overlay["text"], lang)[0].get("translation_text")
                                wrapped_text = "\n".join(textwrap.wrap(translated_text, width=70))
                                text_clip = (
                                    TextClip(wrapped_text, font_size=overlay["font_size"], color=overlay["color"], font=font_map.get(lang))
                                    .with_position((overlay["relative_x"], overlay["relative_y"]), relative=True)
                                    .with_start(overlay["start_time"])
                                    .with_duration(overlay["duration"])
                                )
                                overlays.append(text_clip)

                            final_video = CompositeVideoClip([video, *overlays])

                            output_buffer = BytesIO()
                            processed_video_path = temp_file_path.replace(
                                ".mp4", f"_processed_{'_'.join(langs)}.mp4"
                            )
                            final_video.write_videofile(processed_video_path, codec="libx264", audio_codec="aac", fps=24)

                            with open(processed_video_path, "rb") as f:
                                output_buffer.write(f.read())
                            output_buffer.seek(0)

                            st.success(f"Video processed for languages: {langs}")
                            st.video(output_buffer, format="video/mp4")

                            with open(processed_video_path, "rb") as f:
                                st.download_button(
                                    label="Download Processed Video",
                                    data=f,
                                    file_name=f"processed_video_{'_'.join(langs)}.mp4",
                                    mime="video/mp4"
                                )
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please ensure all fields are filled out.")

if __name__ == "__main__":
    app = FullProcess()
    app.main()
