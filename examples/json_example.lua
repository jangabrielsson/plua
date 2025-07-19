-- JSON Example
-- This example shows how to work with JSON data in plua2

print("=== JSON Example ===")

-- Example 1: Basic JSON encoding and decoding
print("\n1. Basic JSON operations")

local person = {
    name = "Alice",
    age = 30,
    city = "New York",
    hobbies = {"reading", "coding", "hiking"},
    active = true
}

print("Original Lua table:")
for key, value in pairs(person) do
    if type(value) == "table" then
        print("  " .. key .. ": [" .. table.concat(value, ", ") .. "]")
    else
        print("  " .. key .. ": " .. tostring(value))
    end
end

-- Encode to JSON
local json_string = json.encode(person)
print("\nEncoded as JSON:")
print(json_string)

-- Decode back to Lua
local decoded_person = json.decode(json_string)
print("\nDecoded back to Lua table:")
for key, value in pairs(decoded_person) do
    if type(value) == "table" then
        print("  " .. key .. ": [" .. table.concat(value, ", ") .. "]")
    else
        print("  " .. key .. ": " .. tostring(value))
    end
end

-- Example 2: Working with nested objects
setTimeout(function()
    print("\n2. Nested JSON objects")
    
    local company = {
        name = "Tech Corp",
        founded = 2010,
        employees = {
            {
                name = "John Doe",
                position = "Developer",
                skills = {"Lua", "Python", "JavaScript"},
                remote = true
            },
            {
                name = "Jane Smith", 
                position = "Designer",
                skills = {"Photoshop", "Figma"},
                remote = false
            }
        },
        locations = {
            headquarters = {
                city = "San Francisco",
                country = "USA"
            },
            branches = {
                {city = "London", country = "UK"},
                {city = "Tokyo", country = "Japan"}
            }
        }
    }
    
    local company_json = json.encode(company)
    print("Company data as JSON:")
    print(company_json)
    
    -- Access nested data after decoding
    local decoded_company = json.decode(company_json)
    print("\nCompany info:")
    print("  Name: " .. decoded_company.name)
    print("  Founded: " .. decoded_company.founded)
    print("  Employees: " .. #decoded_company.employees)
    print("  First employee: " .. decoded_company.employees[1].name)
    print("  HQ: " .. decoded_company.locations.headquarters.city)
    
end, 1000)

-- Example 3: JSON with HTTP requests
setTimeout(function()
    print("\n3. JSON in HTTP communication")
    
    -- Simulate API data
    local api_request = {
        action = "get_user",
        user_id = 12345,
        fields = {"name", "email", "last_login"},
        options = {
            include_metadata = true,
            format = "detailed"
        }
    }
    
    local api_response = {
        status = "success",
        data = {
            user_id = 12345,
            name = "Bob Wilson",
            email = "bob@example.com",
            last_login = "2025-07-18T10:30:00Z",
            metadata = {
                account_type = "premium",
                created_date = "2023-01-15",
                login_count = 847
            }
        },
        timestamp = os.time()
    }
    
    print("API Request JSON:")
    print(json.encode(api_request))
    
    print("\nAPI Response JSON:")
    print(json.encode(api_response))
    
    -- Demonstrate parsing response
    local response_json = json.encode(api_response)
    local parsed_response = json.decode(response_json)
    
    if parsed_response.status == "success" then
        local user = parsed_response.data
        print("\nParsed user info:")
        print("  Name: " .. user.name)
        print("  Email: " .. user.email)
        print("  Account: " .. user.metadata.account_type)
        print("  Logins: " .. user.metadata.login_count)
    end
    
end, 2000)

-- Example 4: Error handling with JSON
setTimeout(function()
    print("\n4. JSON error handling")
    
    -- Valid JSON
    local valid_json = '{"name": "Test", "value": 42}'
    local result = json.decode(valid_json)
    if result then
        print("✅ Valid JSON parsed successfully:")
        print("  Name: " .. result.name .. ", Value: " .. result.value)
    end
    
    -- Invalid JSON (will be handled gracefully)
    local invalid_json = '{"name": "Test", "value": 42' -- Missing closing brace
    local result2 = json.decode(invalid_json)
    if result2 then
        print("Parsed invalid JSON (unexpected)")
    else
        print("✅ Invalid JSON handled gracefully (returned nil)")
    end
    
    -- Empty/nil handling
    local empty_result = json.decode("")
    print("Empty string decode result:", tostring(empty_result))
    
    local nil_result = json.decode(nil)
    print("Nil decode result:", tostring(nil_result))
    
end, 3000)

print("\nJSON examples will run with delays to show output clearly...")
