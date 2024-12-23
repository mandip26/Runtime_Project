import streamlit as st
from videopluxtext.translate import TranslateMassage as Translator
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile
from io import BytesIO
import textwrap  # For wrapping long text into multiple lines


class FullProcess:
    def __init__(self):
        self.translator = Translator()
        self._pipeline_initialized = False  # Flag to check if pipeline is initialized

    def initialize_pipeline(self):
        if not self._pipeline_initialized:
            import asyncio
            asyncio.run(self.translator.load_pipline())  # Load pipeline asynchronously
            self._pipeline_initialized = True  # Set flag to True

    def main(self):
        st.title("Video Overlay App")
        st.write("Upload a video and add multiple text overlay in multiple languages!")

        # Video upload
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

        # Text and Caption Pair Selection
        st.write("Select Text Language Pairs")
        language_options = ["English", "Hindi", "Bengali", "Gujarati", "Marathi", "Maithili", "Malayalam", "Tamil", "Telugu"]

        # Initialize session state for text-caption pairs if not already done
        if "text_caption_pairs" not in st.session_state:
            st.session_state.text_caption_pairs = []

        # Columns for text and caption language selection
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            text_lang1 = st.selectbox("Select Text Language 1", language_options, key="text_lang1")
        with col2:
            text_lang2 = st.selectbox("Select Text Language 2", language_options, key="text_lang2")
        with col3:
            text_lang3 = st.selectbox("Select Text Language 3", language_options, key="text_lang3")
        with col4:
            text_lang4 = st.selectbox("Select Text Language 4", language_options, key="text_lang4")

        # Button to add the selected pair
        if st.button("Add Pair"):
            if text_lang1 and text_lang2 and text_lang3 and text_lang4:
                st.session_state.text_caption_pairs.append((text_lang1, text_lang2, text_lang3, text_lang4))
                st.success("Pair added successfully!")
                st.session_state.refresh = True  # Flag to trigger page refresh

        # Display existing pairs
        st.subheader("Existing Text Language Pairs")
        for i, pair in enumerate(st.session_state.text_caption_pairs):
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            with col1:
                st.write(f"Language 1: {pair[0]}")
            with col2:
                st.write(f"Language 2: {pair[1]}")
            with col3:
                st.write(f"Language 3: {pair[2]}")
            with col4:
                st.write(f"Language 4: {pair[3]}")
            with col5:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.text_caption_pairs.pop(i)
                    st.session_state.refresh = True  # Flag to trigger page refresh

        # Refresh logic based on the flag
        if st.session_state.get("refresh"):
            del st.session_state.refresh  # Clean up the flag

        # Text Overlay Inputs for each text
        def get_text_overlay_input(num):
            st.subheader(f"Text Overlay {num}")
            # Font size and color selection for text
            col1, col2 = st.columns(2)
            with col1:
                font_size = st.selectbox(f"Select Font Size for Text {num}", [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120], index=4, key=f"font_size{num}")
            with col2:
                color = st.color_picker(f"Pick a Color for Text {num}", "#FFFFFF", key=f"color{num}")

            # Text position sliders
            col1, col2 = st.columns(2)
            with col1:
                relative_x = st.slider(f"Text Overlay X Position {num} (0-1)", 0.0, 1.0, 0.5, step=0.05, key=f"relative_x{num}")
            with col2:
                relative_y = st.slider(f"Text Overlay Y Position {num} (0-1)", 0.0, 1.0, 0.3, step=0.05, key=f"relative_y{num}")

            col1, col2 = st.columns(2)
            with col1:
                text_start_time = st.slider(f"Text start time {num} (0-10)", 0.0, 10.0, 2.0 , step=1.0, key=f"text_start_time{num}")
            with col2:
                text_duration = st.slider(f"Text duration {num} (0-10)", 0.0, 10.0, 2.0 , step=1.0, key=f"text_duration{num}")
                
            # Text Input
            text_input = st.text_area(f"Enter Text to Overlay {num}", key=f"text_input{num}")
            return text_input, font_size, color, relative_x, relative_y, text_start_time, text_duration

        text_input1, font_size1, color1, relative_x1, relative_y1, text_start_time1, text_duration1 = get_text_overlay_input(1)
        text_input2, font_size2, color2, relative_x2, relative_y2, text_start_time2, text_duration2 = get_text_overlay_input(2)
        text_input3, font_size3, color3, relative_x3, relative_y3, text_start_time3, text_duration3 = get_text_overlay_input(3)
        text_input4, font_size4, color4, relative_x4, relative_y4, text_start_time4, text_duration4 = get_text_overlay_input(4)

        # Process Video Button
        if st.button("Process Video"):
            if uploaded_file and text_input1 and text_input2 and text_input3 and text_input4 and st.session_state.text_caption_pairs:
                try:
                    # Ensure translator is initialized
                    self.initialize_pipeline()

                    # Process the video using MoviePy
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_file_path = temp_file.name

                    video = VideoFileClip(temp_file_path)

                    # Font paths
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

                    for text_lang1, text_lang2, text_lang3, text_lang4 in st.session_state.text_caption_pairs:
                        # Translate Text and Caption
                        translated_text1 = self.translator.translate_input(text_input1, text_lang1)[0].get("translation_text")
                        translated_text2 = self.translator.translate_input(text_input2, text_lang2)[0].get("translation_text")
                        translated_text3 = self.translator.translate_input(text_input3, text_lang3)[0].get("translation_text")
                        translated_text4 = self.translator.translate_input(text_input4, text_lang4)[0].get("translation_text")

                        # Wrap Text and Caption
                        wrapped_text1 = "\n".join(textwrap.wrap(translated_text1, width=70))
                        wrapped_text2 = "\n".join(textwrap.wrap(translated_text2, width=70))
                        wrapped_text3 = "\n".join(textwrap.wrap(translated_text3, width=70))
                        wrapped_text4 = "\n".join(textwrap.wrap(translated_text4, width=70))

                        # Create Text and Caption Clips
                        text_overlay1 = (
                            TextClip(wrapped_text1, font_size=font_size1, color=color1, font=font_map.get(text_lang1))
                            .with_position((relative_x1, relative_y1), relative=True)
                            .with_start(text_start_time1)
                            .with_duration(text_duration1)
                        )
                        text_overlay2 = (
                            TextClip(wrapped_text2, font_size=font_size2, color=color2, font=font_map.get(text_lang2))
                            .with_position((relative_x2, relative_y2), relative=True)
                            .with_start(text_start_time2)
                            .with_duration(text_duration2)
                        )
                        text_overlay3 = (
                            TextClip(wrapped_text3, font_size=font_size3, color=color3, font=font_map.get(text_lang3))
                            .with_position((relative_x3, relative_y3), relative=True)
                            .with_start(text_start_time3)
                            .with_duration(text_duration3)
                        )
                        text_overlay4 = (
                            TextClip(wrapped_text4, font_size=font_size4, color=color4, font=font_map.get(text_lang4))
                            .with_position((relative_x4, relative_y4), relative=True)
                            .with_start(text_start_time4)
                            .with_duration(text_duration4)
                        )

                        # Combine the video with overlays
                        final_video = CompositeVideoClip([video, text_overlay1, text_overlay2, text_overlay3, text_overlay4])
                        
                        # Save processed video
                        output_buffer = BytesIO()
                        processed_video_path = temp_file_path.replace(
                           ".mp4", f"_{text_lang1}_text_{text_lang2}_text_{text_lang3}_text_{text_lang4}.mp4"
                        )
                        final_video.write_videofile(processed_video_path, codec="libx264", audio_codec="aac", fps=24)

                        with open(processed_video_path, "rb") as f:
                            output_buffer.write(f.read())
                        output_buffer.seek(0)

                        st.success(f"Video processed: Text in {text_lang1}, Text in {text_lang2},  Text in {text_lang3},  Text in {text_lang4}")
                        st.video(output_buffer, format="video/mp4")

                        # Offer download
                        with open(processed_video_path, "rb") as f:
                            st.download_button(
                                label="Download Processed Video",
                                data=f,
                                file_name=f"processed_video_{text_lang1}_{text_lang2}_{text_lang3}_{text_lang4}.mp4",
                                mime="video/mp4",
                                key=f"download_{text_lang1}_{text_lang2}_{text_lang3}_{text_lang4}"
                            )


                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please ensure all fields are filled out.")

if __name__ == "__main__":
    app = FullProcess()
    app.main()

