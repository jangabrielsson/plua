-- Generate documentation for user-facing _PY functions
print("=== _PY User-Facing Functions Documentation Generator ===")

local user_by_category = _PY.list_user_functions_by_category()

-- Generate markdown content
local markdown_content = {}

table.insert(markdown_content, "# _PY Module Documentation")
table.insert(markdown_content, "")
table.insert(markdown_content, "The `_PY` module provides a collection of utility functions that bridge Lua with the underlying Python runtime. These functions offer file operations, system utilities, browser integration, JSON handling, and more.")
table.insert(markdown_content, "")
table.insert(markdown_content, "## Available Functions by Category")
table.insert(markdown_content, "")

-- Sort categories for consistent output
local categories = {}
for category, _ in pairs(user_by_category) do
    table.insert(categories, category)
end
table.sort(categories)

for _, category in ipairs(categories) do
    local functions = user_by_category[category]
    table.insert(markdown_content, "### " .. category:gsub("^%l", string.upper) .. " Functions")
    table.insert(markdown_content, "")
    
    table.sort(functions) -- Sort functions alphabetically
    
    for _, func_name in ipairs(functions) do
        local func_info = _PY.get_function_info(func_name)
        table.insert(markdown_content, "#### _PY." .. func_name .. "()")
        if func_info and func_info.description then
            table.insert(markdown_content, func_info.description)
        else
            table.insert(markdown_content, "Function: " .. func_name)
        end
        table.insert(markdown_content, "")
    end
end

-- Add usage examples section
table.insert(markdown_content, "## Usage Examples")
table.insert(markdown_content, "")
table.insert(markdown_content, "### File Operations")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- Read a file")
table.insert(markdown_content, "local content = _PY.readFile('config.txt')")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Write a file")
table.insert(markdown_content, "_PY.writeFile('output.txt', 'Hello World!')")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Check if file exists")
table.insert(markdown_content, "if _PY.fileExist('data.json') then")
table.insert(markdown_content, "    local data = _PY.readFile('data.json')")
table.insert(markdown_content, "    print('File found:', data)")
table.insert(markdown_content, "end")
table.insert(markdown_content, "```")
table.insert(markdown_content, "")

table.insert(markdown_content, "### JSON Operations")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- Encode Lua table to JSON")
table.insert(markdown_content, "local data = {name = 'test', value = 42}")
table.insert(markdown_content, "local json_str = _PY.json_encode(data)")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Decode JSON to Lua table")
table.insert(markdown_content, "local decoded = _PY.json_decode(json_str)")
table.insert(markdown_content, "print('Name:', decoded.name)")
table.insert(markdown_content, "```")
table.insert(markdown_content, "")

table.insert(markdown_content, "### Browser Integration")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- Open URL in default browser")
table.insert(markdown_content, "_PY.open_browser('https://example.com')")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Open in VS Code browser")
table.insert(markdown_content, "_PY.open_in_vscode_browser('https://docs.lua.org')")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- List available browsers")
table.insert(markdown_content, "local browsers = _PY.list_browsers()")
table.insert(markdown_content, "for i, browser in ipairs(browsers) do")
table.insert(markdown_content, "    print('Browser:', browser)")
table.insert(markdown_content, "end")
table.insert(markdown_content, "```")
table.insert(markdown_content, "")

table.insert(markdown_content, "### HTML Console Output")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- Convert HTML to colored console output")
table.insert(markdown_content, "local html = '<font color=\"red\">Error:</font> Something went wrong'")
table.insert(markdown_content, "local console_text = _PY.html2console(html)")
table.insert(markdown_content, "print(console_text) -- Will show colored text in terminal")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Get available colors")
table.insert(markdown_content, "local colors = _PY.get_available_colors()")
table.insert(markdown_content, "print('Available colors:', #colors)")
table.insert(markdown_content, "```")
table.insert(markdown_content, "")

table.insert(markdown_content, "### Utility Functions")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- Base64 encoding/decoding")
table.insert(markdown_content, "local text = 'Hello World! 🌍'")
table.insert(markdown_content, "local encoded = _PY.base64_encode(text)")
table.insert(markdown_content, "local decoded = _PY.base64_decode(encoded)")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Get current time in milliseconds")
table.insert(markdown_content, "local timestamp = _PY.millitime()")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Get current working directory")
table.insert(markdown_content, "local cwd = _PY.getcwd()")
table.insert(markdown_content, "print('Working directory:', cwd)")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- List directory contents")
table.insert(markdown_content, "local files = _PY.listdir('.')")
table.insert(markdown_content, "for i, file in ipairs(files) do")
table.insert(markdown_content, "    print('File:', file)")
table.insert(markdown_content, "end")
table.insert(markdown_content, "```")
table.insert(markdown_content, "")

table.insert(markdown_content, "## Function Discovery")
table.insert(markdown_content, "")
table.insert(markdown_content, "The _PY module includes introspection functions to help discover available functionality:")
table.insert(markdown_content, "")
table.insert(markdown_content, "```lua")
table.insert(markdown_content, "-- List all user-facing functions by category")
table.insert(markdown_content, "local by_category = _PY.list_user_functions_by_category()")
table.insert(markdown_content, "for category, functions in pairs(by_category) do")
table.insert(markdown_content, "    print('Category:', category)")
table.insert(markdown_content, "    for i, func_name in ipairs(functions) do")
table.insert(markdown_content, "        print('  Function:', func_name)")
table.insert(markdown_content, "    end")
table.insert(markdown_content, "end")
table.insert(markdown_content, "")
table.insert(markdown_content, "-- Get information about a specific function")
table.insert(markdown_content, "local info = _PY.get_function_info('readFile')")
table.insert(markdown_content, "print('Description:', info.description)")
table.insert(markdown_content, "print('Category:', info.category)")
table.insert(markdown_content, "```")

-- Write to file
local full_content = table.concat(markdown_content, "\n")
_PY.writeFile("docs/lua/_PY_Documentation.md", full_content)

print("Generated documentation file: docs/lua/_PY_Documentation.md")
print("Total lines generated:", #markdown_content)
