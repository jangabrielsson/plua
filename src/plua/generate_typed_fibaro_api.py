#!/usr/bin/env python3
"""
Enhanced Fibaro API Generator with Full Type Safety

Parses Swagger/OpenAPI JSON files and generates:
1. Pydantic models from JSON schemas (fibaro_api_models.py)
2. Fully typed FastAPI endpoints (fibaro_api_endpoints.py)
3. Simple delegation to Lua dispatch system
4. Proper categorization for Swagger docs

Usage:
    # From project root - regenerate API with defaults
    python src/plua/generate_typed_fibaro_api.py
    
    # Custom directories
    python src/plua/generate_typed_fibaro_api.py --docs-dir fibaro_api_docs --output-dir src/plua
    
    # Get help
    python src/plua/generate_typed_fibaro_api.py --help

This script generates ~305 Pydantic models and ~267 FastAPI endpoints from the
official Fibaro HC3 Swagger specifications. All endpoints delegate to the Lua
fibaro_api_hook function for implementation.

Important: Keep this file in src/plua/ - it's critical for maintaining the API!
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import argparse
import re
from dataclasses import dataclass

@dataclass
class SchemaReference:
    """Represents a schema reference like #/components/schemas/DeviceDto"""
    ref_path: str
    
    @property
    def model_name(self) -> str:
        """Extract model name from reference path"""
        return self.ref_path.split('/')[-1]

class TypedAPIGenerator:
    def __init__(self):
        self.all_schemas: Dict[str, Dict[str, Any]] = {}
        self.generated_models: Set[str] = set()
        
    def load_swagger_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Load and parse a Swagger/OpenAPI JSON file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None

    def python_type_from_schema(self, schema: Dict[str, Any], required: bool = True) -> str:
        """Convert JSON schema to Python type annotation."""
        if '$ref' in schema:
            # Reference to another schema
            ref_name = schema['$ref'].split('/')[-1]
            # Check if referenced schema exists or will be generated
            if ref_name in self.all_schemas or ref_name in ['triggers', 'conditions', 'complexConditions']:
                return ref_name if required else f"Optional[{ref_name}]"
            else:
                # Undefined reference - use generic type
                return 'Dict[str, Any]' if required else 'Optional[Dict[str, Any]]'
        
        schema_type = schema.get('type', 'object')
        schema_format = schema.get('format')
        
        if schema_type == 'string':
            if schema_format == 'date-time':
                return 'datetime' if required else 'Optional[datetime]'
            elif schema_format == 'date':
                return 'date' if required else 'Optional[date]'
            else:
                return 'str' if required else 'Optional[str]'
        elif schema_type == 'integer':
            return 'int' if required else 'Optional[int]'
        elif schema_type == 'number':
            return 'float' if required else 'Optional[float]'
        elif schema_type == 'boolean':
            return 'bool' if required else 'Optional[bool]'
        elif schema_type == 'array':
            items_type = self.python_type_from_schema(schema.get('items', {'type': 'object'}), True)
            return f"List[{items_type}]" if required else f"Optional[List[{items_type}]]"
        elif schema_type == 'object':
            # For generic objects, use Dict[str, Any]
            return 'Dict[str, Any]' if required else 'Optional[Dict[str, Any]]'
        else:
            return 'Any' if required else 'Optional[Any]'

    def generate_pydantic_model(self, model_name: str, schema: Dict[str, Any]) -> str:
        """Generate a Pydantic model from a JSON schema."""
        if model_name in self.generated_models:
            return ""
        self.generated_models.add(model_name)
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        # Clean model name for Python class
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', model_name)
        if clean_name[0].isdigit():
            clean_name = f"Model_{clean_name}"
        # Always two newlines before each class
        code = f"\n\nclass {clean_name}(BaseModel):\n"
        if not properties:
            code += "    pass\n"
            return code
        # Add description if available
        if 'description' in schema:
            code += f'    """{schema["description"]}"""\n'
        # Special case for DeviceActionArgumentsDto
        if model_name == 'DeviceActionArgumentsDto':
            # Always generate delay and integrationPin as optional
            for field_name, field_schema in properties.items():
                if field_name == 'delay':
                    code += '    delay: Optional[float] = None  # Now truly optional\n'
                elif field_name == 'integrationPin':
                    code += '    integrationPin: Optional[str] = None  # Now truly optional\n'
                else:
                    is_required = field_name in required_fields
                    field_type = self.python_type_from_schema(field_schema, is_required)
                    safe_field_name = field_name
                    if field_name in ['from', 'to', 'type', 'filter', 'import', 'class', 'def', 'if', 'else', 'for', 'while', 'in', 'is', 'not', 'and', 'or']:
                        safe_field_name = f"{field_name}_"
                    elif not field_name.replace('_', '').isalnum() or field_name[0].isdigit() or field_name.startswith('$'):
                        safe_field_name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
                        if safe_field_name[0].isdigit() or safe_field_name.startswith('_'):
                            safe_field_name = f"field_{safe_field_name}"
                    needs_alias = safe_field_name != field_name
                    description = field_schema.get('description', '')
                    if needs_alias:
                        if description:
                            code += f'    {safe_field_name}: {field_type} = Field(..., alias="{field_name}", description="{description}")\n'
                        elif is_required:
                            code += f'    {safe_field_name}: {field_type} = Field(..., alias="{field_name}")\n'
                        else:
                            code += f'    {safe_field_name}: {field_type} = Field(None, alias="{field_name}")\n'
                    else:
                        if description:
                            code += f'    {safe_field_name}: {field_type} = Field(..., description="{description}")\n'
                        elif is_required:
                            code += f'    {safe_field_name}: {field_type}\n'
                        else:
                            code += f'    {safe_field_name}: {field_type} = None\n'
            return code
        # Normal model generation for all other models
        for field_name, field_schema in properties.items():
            is_required = field_name in required_fields
            field_type = self.python_type_from_schema(field_schema, is_required)
            safe_field_name = field_name
            if field_name in ['from', 'to', 'type', 'filter', 'import', 'class', 'def', 'if', 'else', 'for', 'while', 'in', 'is', 'not', 'and', 'or']:
                safe_field_name = f"{field_name}_"
            elif not field_name.replace('_', '').isalnum() or field_name[0].isdigit() or field_name.startswith('$'):
                safe_field_name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
                if safe_field_name[0].isdigit() or safe_field_name.startswith('_'):
                    safe_field_name = f"field_{safe_field_name}"
            needs_alias = safe_field_name != field_name
            description = field_schema.get('description', '')
            if needs_alias:
                if description:
                    code += f'    {safe_field_name}: {field_type} = Field(..., alias="{field_name}", description="{description}")\n'
                elif is_required:
                    code += f'    {safe_field_name}: {field_type} = Field(..., alias="{field_name}")\n'
                else:
                    code += f'    {safe_field_name}: {field_type} = Field(None, alias="{field_name}")\n'
            else:
                if description:
                    code += f'    {safe_field_name}: {field_type} = Field(..., description="{description}")\n'
                elif is_required:
                    code += f'    {safe_field_name}: {field_type}\n'
                else:
                    code += f'    {safe_field_name}: {field_type} = None\n'
        return code

    def clean_operation_id(self, operation_id: str) -> str:
        """Clean operation ID to be a valid Python function name."""
        cleaned = operation_id.replace('.', '_').replace('-', '_').replace('/', '_')
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', cleaned)
        if cleaned and not (cleaned[0].isalpha() or cleaned[0] == '_'):
            cleaned = 'api_' + cleaned
        return cleaned

    def extract_endpoints_from_swagger(self, swagger_data: Dict[str, Any], file_name: str) -> List[Dict[str, Any]]:
        """Extract endpoint definitions from Swagger data."""
        endpoints = []
        
        if 'paths' not in swagger_data:
            return endpoints
        
        # Get base URL from servers field
        base_url = ""
        if 'servers' in swagger_data and swagger_data['servers']:
            # Use the first server's URL as base path
            base_url = swagger_data['servers'][0].get('url', '').rstrip('/')
        
        # Get category from file name or tags
        default_category = file_name.replace('.json', '').replace('-', '_')
        
        for path, methods in swagger_data['paths'].items():
            for method, definition in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                # Get category from tags or use default
                tags = definition.get('tags', [default_category])
                category = tags[0] if tags else default_category
                
                # Combine base URL with path
                full_path = base_url + path
                
                endpoint = {
                    'path': full_path,
                    'method': method.upper(),
                    'operation_id': self.clean_operation_id(definition.get('operationId', f"{method}_{path.replace('/', '_')}")),
                    'summary': definition.get('summary', ''),
                    'description': definition.get('description', ''),
                    'category': category,
                    'parameters': definition.get('parameters', []),
                    'request_body': definition.get('requestBody'),
                    'responses': definition.get('responses', {}),
                }
                endpoints.append(endpoint)
        
        return endpoints

    def generate_typed_endpoint(self, endpoint: Dict[str, Any]) -> str:
        """Generate a fully typed FastAPI endpoint."""
        method = endpoint['method'].lower()
        path = endpoint['path']
        operation_id = endpoint['operation_id']
        summary = endpoint.get('summary', '')
        description = endpoint.get('description', '')
        category = endpoint.get('category', 'api')
        parameters = endpoint.get('parameters', [])
        request_body = endpoint.get('request_body')
        
        # Convert path parameters to FastAPI format
        fastapi_path = path
        func_args = ["request: Request"]
        imports_needed = set()
        
        # Separate path, required query, and optional query parameters for correct ordering
        path_params = []
        required_query_params = []
        optional_query_params = []
        
        # Process parameters
        for param in parameters:
            param_name = param['name']
            param_type = param.get('schema', {}).get('type', 'str')
            param_required = param.get('required', False)
            param_in = param.get('in', 'query')
            param_description = param.get('description', '')
            
            # Handle Python keywords
            safe_param_name = param_name
            if param_name in ['from', 'to', 'type', 'filter', 'import', 'class', 'def', 'if', 'else', 'for', 'while', 'in', 'is', 'not', 'and', 'or']:
                safe_param_name = f"{param_name}_"
            
            if param_in == 'path':
                # Path parameters are always required and come first
                py_type = 'int' if param_type == 'integer' else 'str'
                path_params.append(f"{safe_param_name}: {py_type}")
            elif param_in == 'query':
                # Query parameters
                py_type = 'int' if param_type == 'integer' else 'str'
                if param_required:
                    if param_description:
                        required_query_params.append(f'{safe_param_name}: {py_type} = Query(..., description="{param_description}")')
                    else:
                        required_query_params.append(f'{safe_param_name}: {py_type} = Query(...)')
                else:
                    py_type = f"Optional[{py_type}]"
                    imports_needed.add("Optional")
                    if param_description:
                        optional_query_params.append(f'{safe_param_name}: {py_type} = Query(None, description="{param_description}")')
                    else:
                        optional_query_params.append(f'{safe_param_name}: {py_type} = Query(None)')
        
        # Add parameters in correct order: path first, then required query, then optional query
        func_args.extend(path_params)
        func_args.extend(required_query_params)
        func_args.extend(optional_query_params)
        
        # Handle request body
        request_model = None
        if request_body:
            content = request_body.get('content', {})
            json_content = content.get('application/json', {})
            schema = json_content.get('schema', {})
            
            if '$ref' in schema:
                # Use existing model
                request_model = schema['$ref'].split('/')[-1]
                func_args.append(f"request_data: {request_model} = Body(...)")
            else:
                # Generic dict for inline schemas
                func_args.append("request_data: Dict[str, Any] = Body(...)")
                imports_needed.add("Dict")
                imports_needed.add("Any")
        
        func_signature = ", ".join(func_args)
        
        # Generate the endpoint function  
        # Handle body data parameter
        if 'request_data' in func_signature:
            data_param = "request_data.dict() if hasattr(request_data, 'dict') else request_data"
        else:
            data_param = "None"
            
        code = f'''
    @app.{method}("{fastapi_path}", tags=["{category}"])
    async def {operation_id}({func_signature}):
        """
        {summary}
        
        {description}
        """
        return await handle_request(
            request, 
            "{endpoint['method']}", 
            {data_param}
        )
'''
        
        return code

    def generate_complete_api_module(self, docs_dir: Path, output_dir: Path):
        """Generate the complete typed API module with separate files for models and endpoints."""
        
        # Define ONLY the categories we want to include
        included_patterns = [
            'climate', 'rgbprograms', 'additionalinterfaces', 'partitions', 'consumption', 
            'customevents', 'debugmessages', 'devicenotifications', 'devices', 'diagnostics', 
            'energy', 'family', 'favoritecolors', 'globalvariables', 'history', 'home', 
            'humidity', 'icons', 'info', 'iosdevices', 'led', 'location', 'loginstatus', 
            'network', 'networkdiscovery', 'notifications', 'notificationcenter', 'plugins', 
            'profiles', 'push', 'quickapp', 'reboot', 'refreshstates', 'rooms', 'scenes', 
            'sections', 'sortorder', 'sprinklers', 'system', 'systemstatus', 'useractivity', 
            'users', 'weather'
        ]
        
        # Define patterns to explicitly exclude (to be more precise)
        excluded_patterns = [
            'linkeddevices', 'certificates', 'json'
        ]
        
        # First, collect all schemas (only including wanted ones)
        print("Collecting schemas...")
        for json_file in docs_dir.rglob("*.json"):
            file_stem = json_file.stem.lower()
            
            # Check if file should be included
            should_include = any(pattern.lower() in file_stem for pattern in included_patterns)
            
            # Check if file should be excluded
            should_exclude = any(pattern.lower() in file_stem for pattern in excluded_patterns)
            
            if not should_include or should_exclude:
                print(f"Skipping schemas from {json_file.name} (not in included list or in excluded list)")
                continue
                
            swagger_data = self.load_swagger_file(json_file)
            if swagger_data and 'components' in swagger_data and 'schemas' in swagger_data['components']:
                schemas = swagger_data['components']['schemas']
                # Prefix schema names with file name to avoid conflicts
                file_prefix = json_file.stem.replace('-', '_').replace('.', '_')
                for schema_name, schema_def in schemas.items():
                    # Use original name if no conflict, otherwise prefix
                    full_name = schema_name
                    if schema_name in self.all_schemas:
                        full_name = f"{file_prefix}_{schema_name}"
                    self.all_schemas[full_name] = schema_def
                print(f"Collected {len(schemas)} schemas from {json_file.name}")
        
        print(f"Found {len(self.all_schemas)} total schemas")
        
        # Generate Pydantic models file
        print("Generating Pydantic models file...")
        models_code = ""
        for model_name, schema in self.all_schemas.items():
            models_code += self.generate_pydantic_model(model_name, schema)
        
        # Format the models code (add extra blank lines between classes)
        def add_extra_blank_lines_between_classes(text):
            """Add an extra blank line between class definitions if only one exists"""
            return re.sub(r"(\nclass [A-Za-z_][\w]*)", r"\n\n\1", text)
        
        models_code = add_extra_blank_lines_between_classes(models_code)
        
        # Create models file
        models_header = '''"""
Fibaro HC3 API Pydantic Models
Auto-generated from Swagger/OpenAPI specifications.
Contains all data models used by the Fibaro API endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date

# Generated Pydantic Models
'''
        
        models_file = output_dir / "fibaro_api_models.py"
        with open(models_file, 'w') as f:
            f.write(models_header + models_code)
        
        print(f"Generated {models_file} with {len(self.all_schemas)} models")
        
        # Collect all endpoints (only including wanted ones)
        print("Collecting endpoints...")
        all_endpoints = []
        categories = set()
        
        for json_file in docs_dir.rglob("*.json"):
            file_stem = json_file.stem.lower()
            
            # Check if file should be included
            should_include = any(pattern.lower() in file_stem for pattern in included_patterns)
            
            # Check if file should be excluded
            should_exclude = any(pattern.lower() in file_stem for pattern in excluded_patterns)
            
            if not should_include or should_exclude:
                print(f"Skipping endpoints from {json_file.name} (not in included list or in excluded list)")
                continue
                
            swagger_data = self.load_swagger_file(json_file)
            if swagger_data:
                endpoints = self.extract_endpoints_from_swagger(swagger_data, json_file.stem)
                all_endpoints.extend(endpoints)
                categories.update(endpoint['category'] for endpoint in endpoints)
                print(f"Found {len(endpoints)} endpoints in {json_file.name}")
        
        print(f"Total endpoints: {len(all_endpoints)}")
        print(f"Categories: {', '.join(sorted(categories))}")
        
        # Generate endpoint code
        print("Generating endpoints...")
        endpoints_code = ""
        for endpoint in all_endpoints:
            try:
                endpoints_code += self.generate_typed_endpoint(endpoint)
            except Exception as e:
                print(f"Error generating endpoint {endpoint.get('operation_id', 'unknown')}: {e}")
        
        # Create the endpoints file
        endpoints_header = '''"""
Fibaro HC3 API Emulation Server with Full Type Safety
Auto-generated from Swagger/OpenAPI specifications with Pydantic models.
Delegates all requests to Lua via simplified (method, path, data) pattern.
"""

from fastapi import FastAPI, Query, Body, HTTPException, Request
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import logging
import json

# flake8: noqa
# Import all models from the separate models file
from .fibaro_api_models import *

logger = logging.getLogger(__name__)

# This will be set by the main module
interpreter = None

def set_interpreter(lua_interpreter):
    """Set the Lua interpreter instance."""
    global interpreter
    interpreter = lua_interpreter

# Helper function to handle all requests
async def handle_request(request: Request, method: str, body_data: Any = None):
    """Common handler for all API requests"""
    full_path = str(request.url.path)
    if request.url.query:
        full_path += f"?{request.url.query}"
    
    # Convert body data to JSON string if present
    data = ""
    if body_data is not None:
        if hasattr(body_data, 'dict'):
            data = json.dumps(body_data.dict())
        elif isinstance(body_data, dict):
            data = json.dumps(body_data)
        else:
            data = str(body_data)
    
    try:
        result = interpreter.lua.globals()._PY.fibaro_api_hook(method, full_path, data)
        return result
    except Exception as e:
        logger.error(f"Error in Fibaro API hook for {method} {full_path}: {e}")
        return {"error": "Internal server error", "message": str(e)}

'''
        
        endpoints_footer = '''

def create_fibaro_api_routes(app: FastAPI):
    """Create all typed Fibaro API routes."""
    
    # Check if we have an interpreter set
    if interpreter is None:
        raise RuntimeError("Interpreter not set. Call set_interpreter() first.")
    
    # Generated Fibaro API endpoints
'''

        endpoints_footer += endpoints_code
        endpoints_footer += """
    logger.info(f"Created {len(all_endpoints) + 2} API endpoints with full type safety")
"""

        # Write the endpoints file
        endpoints_file = output_dir / "fibaro_api_endpoints.py"
        complete_endpoints_code = endpoints_header + endpoints_footer

        with open(endpoints_file, 'w') as f:
            f.write(complete_endpoints_code)

        print(f"Generated {endpoints_file} with {len(all_endpoints)} endpoints")
        return len(all_endpoints)

def main():
    parser = argparse.ArgumentParser(description='Generate typed Fibaro API endpoints from Swagger files')
    
    # Get the script directory and calculate project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # src/plua -> src -> project_root
    
    parser.add_argument('--docs-dir', default=str(project_root / 'fibaro_api_docs'), 
                       help='Directory containing Swagger JSON files')
    parser.add_argument('--output-dir', default=str(script_dir),
                       help='Output directory for generated API files')
    
    args = parser.parse_args()
    
    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"Error: Documentation directory {docs_dir} not found")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = TypedAPIGenerator()
    total_endpoints = generator.generate_complete_api_module(docs_dir, output_dir)
    
    print(f"\nSuccessfully generated:")
    print(f"  - {output_dir}/fibaro_api_models.py with {len(generator.all_schemas)} models")
    print(f"  - {output_dir}/fibaro_api_endpoints.py with {total_endpoints} endpoints")
    return 0

if __name__ == '__main__':
    exit(main())
