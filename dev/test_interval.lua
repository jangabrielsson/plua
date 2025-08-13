-- Test script with infinite interval for testing --run-for time limits
print("Starting infinite interval test...")

local count = 0
_PY.setInterval(function()
    count = count + 1
    print("Interval tick:", count)
end, 1000)

print("Interval started, should run until time limit or Ctrl-C")
