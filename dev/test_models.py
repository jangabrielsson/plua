#!/usr/bin/env python3

import sys
sys.path.insert(0, "/Users/jangabrielsson/Documents/dev/plua2/src")

try:
    from plua2.fibaro_api_models import *
    print("✓ Models imported successfully")
    
    # Try to create a simple model instance
    try:
        scene = CreateSceneRequest(name="test", content="test content", restart=True)
        print("✓ CreateSceneRequest works")
    except Exception as e:
        print(f"✗ CreateSceneRequest failed: {e}")
        
    # Try to get the schema which is what FastAPI does
    try:
        schema_dict = CreateSceneRequest.model_json_schema()
        print("✓ Schema generation works")
    except Exception as e:
        print(f"✗ Schema generation failed: {e}")
        import traceback
        traceback.print_exc()
        
    # Test the problematic models we know about
    print("\nTesting specific models...")
    
    try:
        test_model = ClimateZonesActionDto(id=1, mode="ClimateZonesActionMode")
        print("✓ ClimateZonesActionDto works")
    except Exception as e:
        print(f"✗ ClimateZonesActionDto failed: {e}")
        
    try:
        schema_dict = ClimateZonesActionDto.model_json_schema()
        print("✓ ClimateZonesActionDto schema works")
    except Exception as e:
        print(f"✗ ClimateZonesActionDto schema failed: {e}")
        import traceback
        traceback.print_exc()
        
    # Try to test what FastAPI does - get schemas for all models
    print("\nTesting all model schemas...")
    import inspect
    import plua2.fibaro_api_models as models_module
    
    failed_models = []
    for name, obj in inspect.getmembers(models_module):
        if inspect.isclass(obj) and hasattr(obj, 'model_json_schema'):
            try:
                obj.model_json_schema()
                print(f"✓ {name} schema OK")
            except Exception as e:
                print(f"✗ {name} schema failed: {e}")
                failed_models.append((name, e))
                
    if failed_models:
        print(f"\nFailed models: {len(failed_models)}")
        for name, error in failed_models[:5]:  # Show first 5
            print(f"  {name}: {error}")
        
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
