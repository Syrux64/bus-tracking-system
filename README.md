# Bus Tracking System 🚌 📍
Using camera, bus images are captured and the label on the windshield is processed and sent to web-app, along with the bus stop name.

## Demo
![image](https://github.com/user-attachments/assets/e3cf37dc-ef82-435d-914a-006985ddb46d)
The bus number 85 is detected.

## Required dependencises
```
pip install fastapi uvicorn supabase python-dotenv google-cloud-vision ultralytics
cd vehicle-tracker-app && npm install
npm install @supabase/supabase-js
```
Supabase is required inorder to store and retrieve the data.

### Note
You need Google-cloud-vision API inorder to extract the text from the label.
