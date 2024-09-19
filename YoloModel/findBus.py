import os
import cv2
from google.cloud import vision
from google.oauth2 import service_account
from ultralytics import YOLO
import re
from supabase import create_client
from dotenv import load_dotenv

# Load env
load_dotenv()

# Supabase config
DB_URL = os.getenv('DB_URL')
DB_KEY = os.getenv('DB_KEY')
supabase = create_client(DB_URL, DB_KEY)

CLIENT_IP = '192.168.1.3' # BUS STOP PC's IP

# Google Cloud Vision API client
credentials = service_account.Credentials.from_service_account_file('../google-vision-api.json') # My API
client = vision.ImageAnnotatorClient(credentials=credentials)

# Load YOLO model
model_path = 'last.pt'
model = YOLO(model_path)

# Thresholds and settings
threshold = 0.5
resize_width = 320  
resize_height = 180  
frame_skip = 2  

# Valid label pattern
valid_label_pattern = re.compile(r'^[0-9A-Z]{1,2}$')

# Check if the label is valid
def is_valid_label(label):
    return bool(valid_label_pattern.match(label))

def detect_text(image):
    # Extract text from label
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_content = vision.Image(content=cv2.imencode('.jpg', image_rgb)[1].tobytes())
    response = client.text_detection(image=image_content)
    
    texts = response.text_annotations
    if texts:
        return texts[0].description.strip()
    return ""

def process_frame(frame, current_bus_label, current_bus_disappeared, disappearance_threshold):
    resized_frame = cv2.resize(frame, (resize_width, resize_height))
    results = model(resized_frame)[0]

    new_bus_detected = False
    bus_in_frame = False

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        
        if score > threshold:
            x1 = int(x1 * frame.shape[1] / resize_width)
            y1 = int(y1 * frame.shape[0] / resize_height)
            x2 = int(x2 * frame.shape[1] / resize_width)
            y2 = int(y2 * frame.shape[0] / resize_height)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

            if int(class_id) == 1:  # Assuming class ID 1 is the label ID for the bus
                label_region = frame[y1:y2, x1:x2]
                label_text = detect_text(label_region)
                
                if is_valid_label(label_text):
                    bus_in_frame = True
                    if label_text != current_bus_label:
                        print(f"New bus detected: {label_text}")

                        # supabase.table('CapturedData').insert({'bus_number': label_text, 'bus_stop': CLIENT_IP}).execute()
                        # supabase.rpc('updateBusStop').execute()

                        stop_check = supabase.table('StopName').select('stop_name').eq('ip_address', CLIENT_IP).execute()
                        
                        if stop_check.data:
                            stop_name = stop_check.data[0]['stop_name']
                        else:
                            print(f"Error: IP address {CLIENT_IP} does not exist in StopName table.")
                            return

                        # Insert data into CapturedData table
                        try:
                            supabase.table('CapturedData').insert({
                                'bus_number': label_text,
                                'bus_stop': stop_name
                            }).execute()
                            
                            supabase.rpc('updateBusStop').execute()
                            
                        except Exception as e:
                            print(f"Error inserting data: {e}")

                        # client_socket.send(f"New bus detected: {label_text}".encode())
                        new_bus_detected = True
                        current_bus_label = label_text
                        current_bus_disappeared = 0  # Reset the disappearance counter
                        
                    # Display the label on the video
                    font_scale = 1
                    thickness = 2
                    cv2.putText(frame, f"Bus: {label_text}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
                else:
                    print(f"Invalid label detected: {label_text}")
    
    # Check if the bus has disappeared
    if not bus_in_frame and current_bus_label is not None:
        current_bus_disappeared += 1
        if current_bus_disappeared >= disappearance_threshold:
            print(f"Bus {current_bus_label} left the frame.")
            current_bus_label = None
            current_bus_disappeared = 0
    
    return frame, current_bus_label, current_bus_disappeared

def find_new_bus(video_path):
    # Main function to process video
    cap = cv2.VideoCapture(video_path)
    current_bus_disappeared = 0
    disappearance_threshold = 10 # Number of frames before confirming bus left

    global current_bus_label
    current_bus_label = None
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            processed_frame, current_bus_label, current_bus_disappeared = process_frame(frame, current_bus_label, current_bus_disappeared, disappearance_threshold)
            # cv2.imshow('Captured Video', processed_frame)

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return current_bus_label

if __name__ == "__main__":
    video_path = 'showcase.mp4'
    find_new_bus(video_path)
