from ultralytics import YOLO
import cv2
import math

URL_right = "http://192.168.158.163:81/stream"  # Assuming the video stream is accessible at port 81
URL_left = "http://192.168.158.214:81/stream"   # Assuming the video stream is accessible at port 81

# Video capture objects
cap_left = cv2.VideoCapture(URL_left)
cap_right = cv2.VideoCapture(URL_right)

# Model
model = YOLO("yolo-Weights/yolov8n.pt")

# Object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

# Dictionary to store detected objects and their coordinates
objects_left = {}
objects_right = {}

# Calculate sz1 for the given video resolution (width of the object in the left image)
# Change this value based on the actual width of the object in the left image

# Calculate tantheta and fl
tantheta = 0.5039251366698837
fl = -0.5747405179939804

while True:
    # Read frames from both video streams
    ret_left, img_left = cap_left.read()
    ret_right, img_right = cap_right.read()

    # Break the loop if either video stream ends
    if not ret_left or not ret_right:
        break

    # Perform object detection on the left frame
    results_left = model(img_left)

    # Perform object detection on the right frame
    results_right = model(img_right)

    # Extract information from the left frame
    for r in results_left:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            label = classNames[cls]

            # Assign unique label if an object of the same class already exists
            if label in objects_left:
                label = f"{label}{len(objects_left[label]) + 1}"

            objects_left[label] = (x1, y1, x2, y2)

    # Extract information from the right frame
    for r in results_right:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            label = classNames[cls]

            # Assign unique label if an object of the same class already exists
            if label in objects_right:
                label = f"{label}{len(objects_right[label]) + 1}"

            objects_right[label] = (x1, y1, x2, y2)

    # Calculate fd and dist_away for each object present in both images
    for label, coords_left in objects_left.items():
        if label in objects_right:
            coords_right = objects_right[label]

            # Calculate fd (difference in x-coordinates)
            fd = abs(coords_left[0] - coords_right[0])

            sz1 = 1133.1322 * (0.9906) ** fd

            # Calculate dist_away using the provided formula
            if fd == 0:
                dist_away = 0
            else:
                dist_away = (14.5 / 2) * sz1 * (1 / tantheta) / fd + fl

            # Draw bounding boxes and put distance text on the left frame
            cv2.rectangle(img_left, (coords_left[0], coords_left[1]), (coords_left[2], coords_left[3]), (255, 0, 255), 3)

            if dist_away > 100:
                dist_meters = dist_away / 100
                cv2.putText(img_left, f"{label} - {dist_meters:.2f} m", (coords_left[0], coords_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            else:
                cv2.putText(img_left, f"{label} - {dist_away:.2f} cm", (coords_left[0], coords_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

            # Draw bounding boxes and put distance text on the right frame
            cv2.rectangle(img_right, (coords_right[0], coords_right[1]), (coords_right[2], coords_right[3]), (255, 0, 255), 3)

            if dist_away > 100:
                dist_meters = dist_away / 100
                cv2.putText(img_right, f"{label} - {dist_meters:.2f} m", (coords_right[0], coords_right[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            else:
                cv2.putText(img_right, f"{label} - {dist_away:.2f} cm", (coords_right[0], coords_right[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

    # Display both frames with annotations
    cv2.imshow('Left Stream', img_left)
    cv2.imshow('Right Stream', img_right)

    # Clear dictionaries for the next frame
    objects_left.clear()
    objects_right.clear()

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release video capture objects
cap_left.release()
cap_right.release()
cv2.destroyAllWindows()
