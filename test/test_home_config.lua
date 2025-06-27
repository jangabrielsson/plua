-- Test configuration file for home directory (.plua.lua)
return {
    -- Basic values
    app_name = "PLua Test App",
    version = "1.0.0",
    debug = true,
    
    -- Numeric values
    port = 8080,
    timeout = 30.5,
    
    -- Table values
    database = {
        host = "localhost",
        port = 5432,
        name = "testdb"
    },
    
    -- Array values
    allowed_hosts = {"localhost", "127.0.0.1", "192.168.1.0/24"},
    
    -- Function values (will be stored as strings in Lua)
    on_startup = function()
        print("Home config startup function called")
    end,
    
    -- Boolean values
    enable_logging = true,
    verbose_output = false
} 