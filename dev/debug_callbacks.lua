-- Debug callback counts to see why EPLua doesn't terminate
print("=== Callback Debug ===")
print("Pending callbacks:", _PY.getPendingCallbackCount())
print("Running intervals:", _PY.getRunningIntervalsCount())

-- Test a simple setTimeout without os.exit()
_PY.setTimeout(function()
    print("=== Timeout callback executed ===")
    print("Pending callbacks:", _PY.getPendingCallbackCount())
    print("Running intervals:", _PY.getRunningIntervalsCount())
    
    -- Test again after this callback finishes
    _PY.setTimeout(function()
        print("=== Second timeout callback ===")
        print("Pending callbacks:", _PY.getPendingCallbackCount())
        print("Running intervals:", _PY.getRunningIntervalsCount())
    end, 50)
end, 100)
