local function foo()
    print("A")
    
    -- Set a timer and get its ID
    local timer_id = setTimeout(function() 
      print("This should be cancelled!") 
    end, 2000)
    
    print("Timer ID:", timer_id)
    
    -- Cancel the timer after 500ms
    setTimeout(function()
      print("Cancelling timer", timer_id)
      clearTimeout(timer_id)
    end, 500)
    
    -- Set another timer that should execute
    setTimeout(function()
      print("This timer should execute normally")
    end, 1000)
    
    print("B")
  end
  foo()