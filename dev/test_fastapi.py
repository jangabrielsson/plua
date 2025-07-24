#!/usr/bin/env python3

import sys
sys.path.insert(0, "/Users/jangabrielsson/Documents/dev/plua/src")

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any
import traceback

try:
    from plua.fibaro_api_models import CreateSceneRequest
    print("✓ Imported CreateSceneRequest")
    
    app = FastAPI()
    
    @app.post("/test")
    async def test_endpoint(request: CreateSceneRequest):
        return {"ok": True}
        
    print("✓ Created FastAPI app with endpoint")
    
    # Try to generate OpenAPI schema like FastAPI does
    try:
        openapi_schema = get_openapi(
            title="Test API",
            version="1.0.0",
            routes=app.routes,
        )
        print("✓ OpenAPI schema generation works")
        print(f"Found {len(openapi_schema.get('components', {}).get('schemas', {}))} schemas")
    except Exception as e:
        print(f"✗ OpenAPI schema generation failed: {e}")
        traceback.print_exc()
        
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
