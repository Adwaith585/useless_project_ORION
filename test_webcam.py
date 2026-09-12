import cv2

def main():
    print("Testing Webcam Capture via OpenCV...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not open the webcam.")
        return
    else:
        print("Webcam successfully opened!")
        for i in range(5):
            ret, frame = cap.read()
            print(f"Frame {i}: Success? {ret}, Shape: {frame.shape if ret else 'N/A'}")
        
    cap.release()
    print("Done. If shape is valid (e.g. 480, 640, 3) it's working fine.")

if __name__ == "__main__":
    main()