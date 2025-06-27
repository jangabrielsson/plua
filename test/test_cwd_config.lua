-- Test configuration file for current working directory (.plua.lua)
return {
    -- Override some values from home config
    app_name = "PLua Local App",  -- This should override the home config
    port = 9000,  -- This should override the home config
    
    -- Add new values specific to this directory
    local_setting = "local_value",
    project_name = "My Project",
    
    -- Override database settings
    database = {
        host = "production.example.com",
        port = 3306,
        name = "prod_db",
        ssl = true
    },
    
    -- Add new table
    api = {
        base_url = "https://api.example.com",
        version = "v2",
        timeout = 60
    },
    
    -- Override function
    on_startup = function()
        print("Local config startup function called")
    end
} 