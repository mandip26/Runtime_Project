import threading
import os

from time import sleep


def run_streamlit():
    python_path = os.path.join(os.getcwd(), "bin", "Scripts", "python.exe")
    os.system(f"{python_path} -m streamlit run app.py --server.headless true")
def run_windows():
    os.system("StreamlitApp.exe")

if __name__ == "__main__":
    try:
        streamlit_thread = threading.Thread(target=run_streamlit)
        windows_thread = threading.Thread(target=run_windows)

        # Start threads
        streamlit_thread.start()
        sleep(5)
        windows_thread.start()

        # Join threads to wait for their completion
        streamlit_thread.join()
        windows_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")