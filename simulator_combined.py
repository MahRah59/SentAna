import threading
import time

def simulate_emotion_detection():
    while True:
        print("Running Emotion Detection Simulator...")
        # Your actual logic here
        time.sleep(10)

def simulate_youtube_mock():
    while True:
        print("Running YouTube Mock Channel Simulator...")
        # Your actual logic here
        time.sleep(15)

if __name__ == "__main__":
    t1 = threading.Thread(target=simulate_emotion_detection)
    t2 = threading.Thread(target=simulate_youtube_mock)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
