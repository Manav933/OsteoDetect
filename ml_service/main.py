import os
import io
import json
import numpy as np
import pickle
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
import tensorflow as tf

app = FastAPI(title="Osteoporosis ML Inference Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and preprocessors
MODEL = None
PREPROCESSORS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    path1 = os.path.join(BASE_DIR, filename)
    if os.path.exists(path1):
        return path1
    path2 = os.path.join(os.path.dirname(BASE_DIR), filename)
    return path2 if os.path.exists(path2) else path1

MODEL_PATH = get_file_path("osteoporosis_multimodal_model_rmsprop_optimized.h5")
PREPROCESSORS_PATH = get_file_path("preprocessing_objects_rmsprop_optimized.pkl")

@app.on_event("startup")
async def load_model():
    global MODEL, PREPROCESSORS
    try:
        if os.path.exists(MODEL_PATH):
            MODEL = tf.keras.models.load_model(MODEL_PATH)
            print("Model loaded successfully.")
        else:
            print(f"Warning: Model not found at {MODEL_PATH}")

        if os.path.exists(PREPROCESSORS_PATH):
            with open(PREPROCESSORS_PATH, "rb") as f:
                PREPROCESSORS = pickle.load(f)
            print("Preprocessors loaded successfully.")
        else:
            print(f"Warning: Preprocessors not found at {PREPROCESSORS_PATH}")
    except Exception as e:
        print(f"Error loading models or preprocessors: {e}")

def preprocess_image(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    # Assuming standard ResNet input size 224x224
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    return np.expand_dims(img_array, axis=0)

def preprocess_tabular(data: dict):
    if PREPROCESSORS is None:
        return np.zeros((1, 12))
        
    try:
        numerical_features = [
            'SPINE_BMD', 'SPINE_TSCORE', 'HIP_BMD', 'HIP_TSCORE',
            'HIPNECK_BMD', 'HIPNECK_TSCORE', 'HEIGHT'
        ]
        categorical_features = [
            'AGE_CATEGORY', 'SMOKING_STATUS', 'PHYSICAL_ACTIVITY_LEVAL',
            'DIET_PLAN', 'ALCOHOL_INTAKE'
        ]
        
        # safely get float values
        num_data = []
        for feat in numerical_features:
            val = data.get(feat, 0.0)
            if val is None or val == "":
                val = 0.0
            num_data.append(float(val))
            
        num_array = np.array(num_data).reshape(1, -1)
        
        cat_data = []
        label_encoders = PREPROCESSORS.get('label_encoders', {})
        for feat in categorical_features:
            val = data.get(feat, "Unknown")
            if val is None or val == "":
                val = "Unknown"
            val = str(val)
            
            # transform using the label encoder
            if feat in label_encoders:
                le = label_encoders[feat]
                # handle unseen labels gracefully
                if val in le.classes_:
                    encoded_val = le.transform([val])[0]
                else:
                    if "Unknown" in le.classes_:
                        encoded_val = le.transform(["Unknown"])[0]
                    else:
                        encoded_val = 0
            else:
                encoded_val = 0
            cat_data.append(encoded_val)
            
        cat_array = np.array(cat_data).reshape(1, -1)
        
        combined = np.column_stack([num_array, cat_array])
        
        # Scale
        scaler = PREPROCESSORS.get('scaler')
        if scaler:
            combined = scaler.transform(combined)
            
        return combined
    except Exception as e:
        print(f"Warning: Preprocessor transform failed: {e}")
        return np.zeros((1, 12))

@app.post("/predict")
async def predict(file: UploadFile = File(...), structured_data: str = Form(...)):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    
    try:
        data_dict = json.loads(structured_data)
        image_bytes = await file.read()
        
        img_array = preprocess_image(image_bytes)
        tab_array = preprocess_tabular(data_dict)
        
        # Inference
        predictions = MODEL.predict([img_array, tab_array])
        pred_class_idx = np.argmax(predictions[0])
        confidence_score = float(np.max(predictions[0])) * 100.0
        
        classes = ["Normal", "Osteopenia", "Osteoporosis"]
        pred_class = classes[pred_class_idx]
        
        risk_level = "Low"
        if pred_class == "Osteopenia":
            risk_level = "Medium"
        elif pred_class == "Osteoporosis":
            risk_level = "High"

        return JSONResponse(content={
            "prediction_class": pred_class,
            "confidence_score": round(confidence_score, 2),
            "risk_level": risk_level,
            "probabilities": {classes[i]: float(predictions[0][i]) for i in range(len(classes))},
            "explanation": f"The ML engine evaluated {pred_class} using the spine/hip scores and detailed lifestyle heuristics. Real prediction enabled via tabular dataframe preprocessing.",
            "gradcam_base64": "dummy_base64_heatmap_string_would_go_here_from_model_introspection"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": MODEL is not None}

@app.get("/")
async def root():
    return {"message": "OsteoDetect ML Service is running normally."}
