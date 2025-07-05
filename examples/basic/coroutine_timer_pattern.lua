--%%name:Coroutine Timer Pattern Example

-- This example demonstrates the correct pattern for using timers with coroutines in PLua
-- Due to Lupa limitations, you cannot call coroutine.resume() directly from timer callbacks

print("=== COROUTINE TIMER PATTERN EXAMPLE ===")

-- Example 1: CORRECT PATTERN - Using flags and polling
print("\n--- Example 1: Correct Pattern (Using Flags) ---")

local function correct_pattern()
  print("A: Starting correct pattern...")
  
  -- Use a flag to signal completion
  local done = false
  
  setTimeout(function() 
    print("D: Timer fired, setting flag...")
    done = true  -- Just set a flag, don't call coroutine.resume
  end, 1000)
  
  print("B: Timer set, yielding...")
  
  -- Yield and wait for the flag to be set
  while not done do
    coroutine.yield()
  end
  
  print("C: Flag set, continuing...")
end

local co1 = coroutine.create(correct_pattern)
coroutine.resume(co1)

-- Example 2: CORRECT PATTERN - Using _PY.sleep for simple delays
print("\n--- Example 2: Correct Pattern (Using _PY.sleep) ---")

local function sleep_pattern()
  print("A: Starting sleep pattern...")
  
  setTimeout(function() 
    print("D: Timer fired!")
  end, 500)
  
  print("B: Timer set, sleeping...")
  
  -- Use _PY.sleep instead of yielding in a loop
  _PY.sleep(1.0)
  
  print("C: Sleep completed, continuing...")
end

local co2 = coroutine.create(sleep_pattern)
coroutine.resume(co2)

-- Example 3: CORRECT PATTERN - Multiple timers with flags
print("\n--- Example 3: Correct Pattern (Multiple Timers) ---")

local function multiple_timers()
  print("A: Starting multiple timers...")
  
  local timer1_done = false
  local timer2_done = false
  
  setTimeout(function() 
    print("D: Timer 1 fired!")
    timer1_done = true
  end, 800)
  
  setTimeout(function() 
    print("E: Timer 2 fired!")
    timer2_done = true
  end, 1200)
  
  print("B: Timers set, waiting...")
  
  -- Wait for both timers
  while not (timer1_done and timer2_done) do
    coroutine.yield()
  end
  
  print("C: Both timers completed!")
end

local co3 = coroutine.create(multiple_timers)
coroutine.resume(co3)

-- Example 4: CORRECT PATTERN - Using setInterval
print("\n--- Example 4: Correct Pattern (setInterval) ---")

local function interval_pattern()
  print("A: Starting interval pattern...")
  
  local count = 0
  local interval_id = setInterval(function()
    count = count + 1
    print("D: Interval fired, count:", count)
    
    if count >= 3 then
      print("E: Cancelling interval...")
      clearInterval(interval_id)
    end
  end, 600)
  
  print("B: Interval set, waiting...")
  
  -- Wait for the interval to complete
  while count < 3 do
    coroutine.yield()
  end
  
  print("C: Interval completed!")
end

local co4 = coroutine.create(interval_pattern)
coroutine.resume(co4)

-- Example 5: WHAT NOT TO DO - Direct coroutine.resume from callback
print("\n--- Example 5: What NOT To Do (Direct Resume) ---")
print("WARNING: The following code would crash with a segmentation fault!")
print("This is commented out to prevent crashes.")

--[[
local function wrong_pattern()
  print("A: Starting wrong pattern...")
  local co = coroutine.running()
  
  setTimeout(function() 
    print("D: Timer fired, attempting direct resume...")
    coroutine.resume(co)  -- ❌ CRASH: Cannot resume from Python callback
    print("E: This will never print due to crash")
  end, 1000)
  
  print("B: Timer set, yielding...")
  coroutine.yield()
  print("C: This will never print due to crash")
end

local co5 = coroutine.create(wrong_pattern)
coroutine.resume(co5)
--]]

print("\n=== PATTERN SUMMARY ===")
print("✅ CORRECT: Use flags and polling")
print("✅ CORRECT: Use _PY.sleep for delays")
print("✅ CORRECT: Use setInterval with flags")
print("❌ WRONG: Direct coroutine.resume from timer callbacks")
print("\nSee docs/COROUTINE_LIMITATIONS.md for detailed explanation.")

-- Keep the main coroutine alive to see all output
print("\nWaiting for all examples to complete...")
_PY.sleep(3)
print("=== EXAMPLE COMPLETED ===") 