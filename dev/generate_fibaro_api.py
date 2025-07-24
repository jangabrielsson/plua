#!/usr/bin/env python3
"""
Fibaro API Generator
Parses Swagger/OpenAPI JSON files and generates FastAPI endpoints for Fibaro HC3 API emulation.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

def load_swagger_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load and parse a Swagger/OpenAPI JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_endpoints_from_swagger(swagger_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract endpoint definitions from Swagger data."""
    
    def _clean_operation_id(operation_id: str) -> str:
        """Clean operation ID to be a valid Python function name."""
        # Replace dots, hyphens, and other invalid characters with underscores
        cleaned = operation_id.replace('.', '_').replace('-', '_').replace('/', '_')
        # Remove any other non-alphanumeric characters except underscores
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', cleaned)
        # Ensure it starts with a letter or underscore
        if cleaned and not (cleaned[0].isalpha() or cleaned[0] == '_'):
            cleaned = 'api_' + cleaned
        return cleaned
    
    endpoints = []
    
    if 'paths' not in swagger_data:
        return endpoints
    
    # Get the base URL from servers
    base_url = ""
    if 'servers' in swagger_data and swagger_data['servers']:
        base_url = swagger_data['servers'][0].get('url', '')
    
    for path, methods in swagger_data['paths'].items():
        for method, definition in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            # Combine base URL with path
            full_path = base_url + path if base_url else path
            
            endpoint = {
                'path': full_path,
                'method': method.upper(),
                'operation_id': _clean_operation_id(definition.get('operationId', f"{method}_{path.replace('/', '_')}")),
                'summary': definition.get('summary', ''),
                'description': definition.get('description', ''),
                'tags': definition.get('tags', []),
                'parameters': definition.get('parameters', []),
                'request_body': definition.get('requestBody'),
                'responses': definition.get('responses', {}),
            }
            endpoints.append(endpoint)
    
    return endpoints

def generate_fastapi_endpoint(endpoint: Dict[str, Any]) -> str:
    """Generate FastAPI endpoint code for a single endpoint."""
    method = endpoint['method'].lower()
    path = endpoint['path']
    operation_id = endpoint['operation_id']
    summary = endpoint.get('summary', '')
    description = endpoint.get('description', '')
    parameters = endpoint.get('parameters', [])
    request_body = endpoint.get('request_body')
    
    # Convert path parameters to FastAPI format
    fastapi_path = path
    path_params = []
    query_params = []
    
    for param in parameters:
        param_name = param['name']
        param_type = param.get('schema', {}).get('type', 'str')
        param_required = param.get('required', False)
        param_in = param.get('in', 'query')
        
        if param_in == 'path':
            # Replace {param} with {param: type}
            fastapi_path = fastapi_path.replace(f"{{{param_name}}}", f"{{{param_name}}}")
            path_params.append({
                'name': param_name,
                'type': 'int' if param_type == 'integer' else 'str',
                'description': param.get('description', '')
            })
        elif param_in == 'query':
            query_params.append({
                'name': param_name,
                'type': 'int' if param_type == 'integer' else 'str',
                'required': param_required,
                'description': param.get('description', '')
            })
    
    # Build function signature
    func_args = []
    
    # Add path parameters
    for param in path_params:
        func_args.append(f"{param['name']}: {param['type']}")
    
    # Add query parameters
    for param in query_params:
        # Handle Python keywords
        param_name = param['name']
        if param_name in ['from', 'to', 'type', 'filter', 'import', 'class', 'def', 'if', 'else', 'for', 'while', 'in', 'is', 'not', 'and', 'or']:
            param_name = f"{param_name}_param"
        
        default = "None" if not param['required'] else "..."
        param_type = f"Optional[{param['type']}]" if not param['required'] else param['type']
        func_args.append(f"{param_name}: {param_type} = Query({default})")
    
    # Add request body if present
    if request_body:
        func_args.append("request_data: dict = Body(...)")
    
    func_signature = ", ".join(func_args)
    
    # Generate function code
    code = f'''
    @app.{method}("{fastapi_path}")
    async def {operation_id}({func_signature}):
        """
        {summary}
        {description}
        """
        # Prepare data for Lua hook
        method = "{endpoint['method']}"
        path = "{path}"
        query_params = {{}}
        path_params = {{}}
        
'''
    
    # Add path parameters to dict
    for param in path_params:
        code += f'        path_params["{param["name"]}"] = {param["name"]}\n'
    
    # Add query parameters to dict
    for param in query_params:
        param_name = param['name']
        # Handle Python keywords - use the modified parameter name
        func_param_name = param_name
        if param_name in ['from', 'to', 'type', 'filter', 'import', 'class', 'def', 'if', 'else', 'for', 'while', 'in', 'is', 'not', 'and', 'or']:
            func_param_name = f"{param_name}_param"
        
        code += f'        if {func_param_name} is not None:\n'
        code += f'            query_params["{param_name}"] = {func_param_name}\n'
    
    # Add request body handling
    if request_body:
        code += f'        body_data = request_data\n'
    else:
        code += f'        body_data = None\n'
    
    # Call Lua hook
    code += f'''
        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {{method}} {{path}}: {{e}}")
            return {{"error": "Internal server error", "message": str(e)}}
'''
    
    return code

def scan_api_docs(docs_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Scan all Swagger JSON files and extract endpoints."""
    all_endpoints = {}
    
    # Skip these files/directories (zwave, elero, nice, etc.)
    skip_patterns = [
        'zwave', 'elero', 'nice', 'installer', 'service', 
        'mobile', 'voip', 'panels', 'settings', 'events', 'alarms'
    ]
    
    for json_file in docs_dir.rglob("*.json"):
        # Check if file should be skipped
        relative_path = json_file.relative_to(docs_dir)
        if any(pattern in str(relative_path).lower() for pattern in skip_patterns):
            print(f"Skipping {relative_path} (excluded pattern)")
            continue
        
        print(f"Processing {relative_path}...")
        swagger_data = load_swagger_file(json_file)
        
        if swagger_data:
            endpoints = extract_endpoints_from_swagger(swagger_data)
            if endpoints:
                all_endpoints[str(relative_path)] = endpoints
                print(f"  Found {len(endpoints)} endpoints")
            else:
                print(f"  No endpoints found")
    
    return all_endpoints

def generate_api_module(all_endpoints: Dict[str, List[Dict[str, Any]]], output_file: Path):
    """Generate the complete FastAPI module with all endpoints."""
    
    header = '''"""
Fibaro HC3 API Emulation Server
Auto-generated from Swagger/OpenAPI specifications.
Delegates all requests to Lua via _PY.fibaro_api_hook function.
"""

from fastapi import FastAPI, Query, Body, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# This will be set by the main module
interpreter = None

def set_interpreter(lua_interpreter):
    """Set the Lua interpreter instance."""
    global interpreter
    interpreter = lua_interpreter

def create_fibaro_api_routes(app: FastAPI):
    """Create all Fibaro API routes."""
    
    # Check if we have an interpreter set
    if interpreter is None:
        raise RuntimeError("Interpreter not set. Call set_interpreter() first.")
    
'''
    
    # Generate all endpoints
    endpoint_code = ""
    total_endpoints = 0
    
    for file_path, endpoints in all_endpoints.items():
        endpoint_code += f"\n        # Endpoints from {file_path}\n"
        
        for endpoint in endpoints:
            try:
                code = generate_fastapi_endpoint(endpoint)
                endpoint_code += code
                total_endpoints += 1
            except Exception as e:
                print(f"Error generating endpoint {endpoint.get('operation_id', 'unknown')}: {e}")
    
    # Complete the function
    footer = f'''
        logger.info(f"Created {total_endpoints} Fibaro API endpoints")
'''
    
    # Write the complete module
    complete_code = header + endpoint_code + footer
    
    with open(output_file, 'w') as f:
        f.write(complete_code)
    
    print(f"Generated {output_file} with {total_endpoints} endpoints")
    return total_endpoints

def main():
    parser = argparse.ArgumentParser(description='Generate Fibaro API endpoints from Swagger files')
    parser.add_argument('--docs-dir', default='fibaro_api_docs', 
                       help='Directory containing Swagger JSON files')
    parser.add_argument('--output', default='src/plua/fibaro_api_endpoints.py',
                       help='Output file for generated API module')
    parser.add_argument('--list-only', action='store_true',
                       help='Only list endpoints, do not generate code')
    
    args = parser.parse_args()
    
    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"Error: Documentation directory {docs_dir} not found")
        return 1
    
    print(f"Scanning {docs_dir} for Swagger JSON files...")
    all_endpoints = scan_api_docs(docs_dir)
    
    if args.list_only:
        print("\nFound endpoints:")
        for file_path, endpoints in all_endpoints.items():
            print(f"\n{file_path}:")
            for endpoint in endpoints:
                print(f"  {endpoint['method']} {endpoint['path']} - {endpoint.get('summary', 'No summary')}")
        return 0
    
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    total_endpoints = generate_api_module(all_endpoints, output_file)
    print(f"\nSuccessfully generated {total_endpoints} endpoints in {output_file}")
    
    return 0

if __name__ == '__main__':
    exit(main())
