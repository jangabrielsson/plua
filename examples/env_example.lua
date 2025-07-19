-- Environment Variable Example
-- This example shows how to use the enhanced getenv function with .env file support

print("=== Environment Variable Example ===")

-- Test 1: Get value from .env file
print("\n1. Reading from .env file:")
local db_url = _PY.getenv_with_dotenv("DATABASE_URL", "not found")
print("DATABASE_URL:", db_url)

local api_key = _PY.getenv_with_dotenv("API_KEY", "not found")
print("API_KEY:", api_key)

local debug = _PY.getenv_with_dotenv("DEBUG", "false")
print("DEBUG:", debug)

local fibaro_host = _PY.getenv_with_dotenv("FIBARO_HOST", "localhost")
print("FIBARO_HOST:", fibaro_host)

-- Test 2: Fall back to system environment variable
print("\n2. Falling back to system environment:")
local path = _PY.getenv_with_dotenv("PATH", "not found")
print("PATH (first 100 chars):", string.sub(path, 1, 100) .. "...")

local home = _PY.getenv_with_dotenv("HOME", "not found")
print("HOME:", home)

-- Test 3: Use default value
print("\n3. Using default values:")
local nonexistent = _PY.getenv_with_dotenv("NONEXISTENT_VAR", "default_value")
print("NONEXISTENT_VAR:", nonexistent)

-- Test 4: Compare with regular getenv
print("\n4. Comparison with regular getenv:")
local env_db_url = _PY.getenv("DATABASE_URL", "not found")
local dotenv_db_url = _PY.getenv_with_dotenv("DATABASE_URL", "not found")
print("Regular getenv DATABASE_URL:", env_db_url)
print("Dotenv getenv DATABASE_URL:", dotenv_db_url)

print("\n=== Example complete ===")
