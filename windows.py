import webview

def main():
    webview.create_window(title="Streamlit App", url="http://localhost:8501")
    webview.start()

if __name__ == '__main__':
    main()
