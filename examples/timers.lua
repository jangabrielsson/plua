-- Timer example demonstrating setTimeout and clearTimeout functionality

local function debug(...)
  print(os.date("%Y-%m-%d %H:%M:%S> "), ...)
end
print("=== Timer Example ===")

-- Simple timer
debug("Setting up a timer for 2 seconds...")
local timer1 = _PY.setTimeout(function()
  debug("Timer 1 fired after 2 seconds!")
end, 2000)

-- Multiple timers with different intervals
debug("Setting up multiple timers...")

local timer2 = _PY.setTimeout(function()
  debug("Timer 2: 1 second elapsed")
end, 1000)

local timer3 = _PY.setTimeout(function()
  debug("Timer 3: 3 seconds elapsed")
end, 3000)

local timer4 = _PY.setTimeout(function()
  debug("Timer 4: 4 seconds elapsed")
end, 4000)

-- Cancel a timer
debug("Setting up a timer to cancel timer2 after 500ms...")
_PY.setTimeout(function()
  debug("Cancelling timer2...")
  local cancelled = _PY.clearTimeout(timer2)
  if cancelled then
  debug("Timer2 was successfully cancelled")
  else
  debug("Timer2 was not found or already executed")
  end
end, 500)

-- Timer that cancels itself
debug("Setting up a self-cancelling timer...")
local self_cancel_timer
self_cancel_timer = _PY.setTimeout(function()
  debug("This timer will cancel itself immediately")
  _PY.clearTimeout(self_cancel_timer)
  debug("Self-cancellation completed")
end, 1500)

-- Nested timers
debug("Setting up nested timers...")
_PY.setTimeout(function()
  debug("Outer timer fired at 2.5 seconds")
  _PY.setTimeout(function()
  debug("Inner timer fired 1 second later")
  end, 1000)
end, 2500)

debug("All timers set up. Waiting for execution...")
debug("(This script will continue running until all timers complete)") 