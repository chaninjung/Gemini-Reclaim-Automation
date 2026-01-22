#!/usr/bin/env python3
"""Gemini API 사용 가능한 모델 목록 확인"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('.env')
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("GEMINI_API_KEY가 설정되지 않았습니다.")
    exit(1)

genai.configure(api_key=api_key)

print("사용 가능한 Gemini 모델 목록:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")
        print()
