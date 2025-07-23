-- TCP Server and Client Demo
-- Demonstrates PLua Python TCP server extension and Lua client with bidirectional communication
--%%name:QA_tcp_server

local server = net.EchoServer("127.0.0.1", 8766,false)

function QuickApp:onInit()
  self:debug("onInit")

  setTimeout(function()
    local messages = {
      "Hello from TCP client!\n",
      "How are you?\n",
      "I'm fine, thank you!\n",
      "What's your name?\n",
      "My name is John Doe.\n",
      "What's your favorite color?\n",
      "My favorite color is blue\n"
    }
    print("[Client] Connecting to TCP server...")
    local client = net.TCPSocket()
    client:connect("127.0.0.1", 8766, {
      success = function()
        print("[Client] Connected to TCP server!")
        local function sendMessages(n)
          if n <= #messages then
            client:write(messages[n], {
              success = function()
                client:read({
                  success = function(data)
                    print("[Client] Received:", data:gsub("\n", "\\n"))
                    if n == #messages then 
                      print("[Client] All messages sent, stopping server and client")
                      server:stop() 
                      setTimeout(function() 
                        client:close()
                      end, 100)
                      return
                    end
                    setTimeout(function() sendMessages(n+1) end, 100)
                  end,
                  error = function(err)
                    print("[Client] Read error:", err)
                  end
                })
              end,
              error = function(err)
                print("[Client] Write error:", err)
              end
            })
          end
        end
        sendMessages(1)
      end,
      error = function(err)
        print("[Client] Connect error:", err)
        server:stop()
      end
    })
  end, 1000)
  
end

