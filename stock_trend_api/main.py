# main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import cv2
from tensorflow.keras.models import load_model
import joblib

# ------------ App Setup ------------

app = FastAPI(
    title="Stock Trend Prediction API",
    description="Predict trend (Down / Sideways / Up) from chart screenshot using LSTM model + simple chatbot suggestions",
    version="1.1.0"
)

# (Optional) CORS, if you'll call from frontend (React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Load Model & Scaler at Startup ------------

MODEL_PATH = "stock_trend_model.h5"
SCALER_PATH = "scaler.pkl"
WINDOW_SIZE = 100
LABEL_MAP = {0: "Down", 1: "Sideways", 2: "Up"}

print("="*50)
print("STARTING MODEL LOADING...")
print("="*50)

try:
    print(f"Loading model from: {MODEL_PATH}")
    model = load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model from {MODEL_PATH}: {e}")
    import traceback
    traceback.print_exc()
    model = None

try:
    print(f"Loading scaler from: {SCALER_PATH}")
    scaler = joblib.load(SCALER_PATH)
    print("✅ Scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading scaler from {SCALER_PATH}: {e}")
    import traceback
    traceback.print_exc()
    scaler = None

print("="*50)
print(f"Model status: {'Loaded' if model is not None else 'NOT LOADED'}")
print(f"Scaler status: {'Loaded' if scaler is not None else 'NOT LOADED'}")
print("="*50)


# ------------ Startup Event ------------

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 STOCK TREND API STARTUP")
    print("="*60)
    print(f"Model loaded: {model is not None}")
    print(f"Scaler loaded: {scaler is not None}")
    if model is None:
        print("⚠️  WARNING: Model failed to load!")
    if scaler is None:
        print("⚠️  WARNING: Scaler failed to load!")
    print("="*60 + "\n")

# ------------ Helper: Extract Series from Image Bytes ------------

def extract_series_from_chart_bytes(image_bytes: bytes, y_min: float, y_max: float, n_points: int = 300) -> np.ndarray:
    """
    Convert chart screenshot to an approximate numeric series.
    image_bytes: raw image bytes from upload
    y_min, y_max: values on Y-axis (bottom and top)
    n_points: how many points to sample horizontally
    """

    # Decode image bytes to OpenCV image
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Unsupported format or corrupted file.")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert so line becomes bright
    gray_inv = 255 - gray

    # Threshold to binary
    _, thresh = cv2.threshold(gray_inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    h, w = thresh.shape

    # Sample across X-axis
    xs = np.linspace(0, w - 1, n_points).astype(int)
    ys = []

    for x in xs:
        col = thresh[:, x]
        ys_idx = np.where(col > 0)[0]  # white pixels
        if len(ys_idx) == 0:
            ys.append(np.nan)
        else:
            ys.append(np.median(ys_idx))

    ys = np.array(ys, dtype=float)

    # Interpolate missing values (NaNs)
    nan_mask = np.isnan(ys)
    if np.any(~nan_mask):
        ys[nan_mask] = np.interp(
            np.flatnonzero(nan_mask),
            np.flatnonzero(~nan_mask),
            ys[~nan_mask]
        )
    else:
        raise ValueError("No line detected anywhere in the image.")

    # Map y-pixel -> value (top pixel = y_max, bottom pixel = y_min)
    top = np.min(ys)
    bottom = np.max(ys)

    if bottom == top:
        raise ValueError("Invalid vertical range detected in image.")

    values = y_max - (ys - top) / (bottom - top) * (y_max - y_min)

    return values


# ------------ Helper: Simple Chatbot Logic ------------

def generate_chatbot_response(
    trend_label: str,
    probs: dict,
    risk_profile: str = "medium",
    horizon: str = "short"
) -> str:
    """
    Very simple rule-based chatbot that explains the trend
    and gives some generic, non-financial-advice suggestions.
    """

    risk_profile = risk_profile.lower().strip()
    horizon = horizon.lower().strip()

    if risk_profile not in ["low", "medium", "high"]:
        risk_profile = "medium"
    if horizon not in ["short", "medium", "long"]:
        horizon = "short"

    down_p = probs.get("Down", 0.0)
    side_p = probs.get("Sideways", 0.0)
    up_p = probs.get("Up", 0.0)

    msg_parts = []

    # 1) Basic explanation of trend
    msg_parts.append(f"Model view: The current chart pattern looks **{trend_label}** to the model.")

    # 2) Confidence description
    max_p = max(down_p, side_p, up_p)
    if max_p >= 0.75:
        confidence_text = "The model is fairly confident in this view."
    elif max_p >= 0.55:
        confidence_text = "The model has moderate confidence in this view."
    else:
        confidence_text = "The model is not very confident; signals are mixed."
    msg_parts.append(confidence_text)

    # 3) Trend-specific commentary
    if trend_label == "Up":
        msg_parts.append(
            "The price has been making higher levels recently. This often suggests positive momentum, "
            "but it does not guarantee that the price will keep going up."
        )
    elif trend_label == "Down":
        msg_parts.append(
            "The price has been moving lower. This can indicate selling pressure or weakness in the short term, "
            "but bounces can still happen."
        )
    elif trend_label == "Sideways":
        msg_parts.append(
            "The price looks range-bound, without a strong upward or downward direction. "
            "This often happens before a larger move, but the direction is uncertain."
        )

    # 4) Very high-level suggestions based on risk profile & horizon
    if risk_profile == "low":
        msg_parts.append(
            "Since you mentioned a **low risk profile**, it may make sense to focus more on capital protection, "
            "diversification, and avoiding emotional decisions based purely on short-term moves."
        )
    elif risk_profile == "medium":
        msg_parts.append(
            "With a **medium risk profile**, balancing risk and reward is important. You might want to combine "
            "trend analysis with fundamentals, news, and proper risk management."
        )
    else:  # high
        msg_parts.append(
            "With a **high risk profile**, you might be more comfortable with volatility, but it’s still important "
            "to define clear entry/exit rules and position sizes."
        )

    if horizon == "short":
        msg_parts.append(
            "For a **short-term horizon**, trends can change quickly. Short-term traders often pay attention to "
            "support/resistance levels, volume, and intraday volatility."
        )
    elif horizon == "medium":
        msg_parts.append(
            "For a **medium-term horizon**, combining this trend with weekly charts and broader market direction "
            "can give additional context."
        )
    else:  # long
        msg_parts.append(
            "For a **long-term horizon**, single chart patterns are less important than the overall business "
            "strength, earnings, and macroeconomic environment."
        )

    # 5) Safety disclaimer
    msg_parts.append(
        "Note: This is not financial advice. Please do your own research (DYOR) and consider consulting a "
        "qualified financial advisor before making any investment decisions."
    )

    return " ".join(msg_parts)


# ------------ API Endpoints ------------

@app.get("/")
def read_root():
    return {"message": "Stock Trend Prediction API with chatbot is running"}


@app.post("/predict_trend_from_image")
async def predict_trend_from_image(
    file: UploadFile = File(..., description="Chart screenshot image (png/jpg)"),
    y_min: float = Form(..., description="Bottom value of chart Y-axis"),
    y_max: float = Form(..., description="Top value of chart Y-axis"),
    n_points: int = Form(300, description="Number of points to sample from chart (optional)"),
    risk_profile: str = Form("medium", description="Risk profile: low / medium / high (optional)"),
    horizon: str = Form("short", description="Investment horizon: short / medium / long (optional)")
):
    """
    Upload a chart screenshot and get:
    - predicted trend (Down / Sideways / Up)
    - probabilities
    - chatbot-style explanation & suggestions
    """

    # Basic checks
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or scaler not loaded on server.")

    if y_max <= y_min:
        raise HTTPException(status_code=400, detail="y_max must be greater than y_min.")

    # Read file bytes
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise ValueError("Empty file uploaded.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    # Extract numeric series from image
    try:
        series = extract_series_from_chart_bytes(image_bytes, y_min=y_min, y_max=y_max, n_points=n_points)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {e}")

    series_len = len(series)
    if series_len < WINDOW_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough points extracted from image. "
                   f"Need at least {WINDOW_SIZE}, got {series_len}."
        )

    # Take last WINDOW_SIZE points
    last_seq = series[-WINDOW_SIZE:].reshape(-1, 1)

    # Scale using same scaler as training
    try:
        last_seq_scaled = scaler.transform(last_seq)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scaling data: {e}")

    # Reshape for LSTM: (1, time_steps, features)
    x_input = last_seq_scaled.reshape(1, WINDOW_SIZE, 1)

    # Predict
    try:
        raw_probs = model.predict(x_input)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

    pred_class = int(np.argmax(raw_probs))
    pred_label = LABEL_MAP.get(pred_class, "Unknown")

    probs = {
        "Down": float(raw_probs[0]),
        "Sideways": float(raw_probs[1]),
        "Up": float(raw_probs[2]),
    }

    # Generate chatbot-style message
    chatbot_msg = generate_chatbot_response(
        trend_label=pred_label,
        probs=probs,
        risk_profile=risk_profile,
        horizon=horizon
    )

    response = {
        "trend": pred_label,
        "class_index": pred_class,
        "probabilities": probs,
        "meta": {
            "series_length": series_len,
            "used_window_size": WINDOW_SIZE,
            "risk_profile": risk_profile,
            "horizon": horizon,
            "file_name": file.filename
        },
        "chatbot_message": chatbot_msg
    }

    return JSONResponse(content=response)
