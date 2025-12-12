#!/usr/bin/env python3
"""
Simple script to test if model and scaler can be loaded
"""
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

print("\n" + "="*50)
print("Testing model loading...")
print("="*50)

# Test 1: Check if files exist
print("\n1. Checking if files exist...")
model_exists = os.path.exists("stock_trend_model.h5")
scaler_exists = os.path.exists("scaler.pkl")
print(f"   stock_trend_model.h5 exists: {model_exists}")
print(f"   scaler.pkl exists: {scaler_exists}")

if not model_exists or not scaler_exists:
    print("[ERROR] Files not found!")
    exit(1)

# Test 2: Load scaler (faster)
print("\n2. Loading scaler...")
try:
    import joblib
    scaler = joblib.load("scaler.pkl")
    print(f"   [OK] Scaler loaded successfully! Type: {type(scaler)}")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Load model
print("\n3. Loading model...")
try:
    from tensorflow.keras.models import load_model
    print("   Importing load_model... OK")
    print("   Loading model file...")
    model = load_model("stock_trend_model.h5")
    print(f"   [OK] Model loaded successfully! Type: {type(model)}")
    print(f"   Model summary:")
    model.summary()
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Test complete!")
print("="*50)
