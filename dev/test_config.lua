-- Test config access
print("=== Config Test ===")
print("nogreet setting:", _PY.config.nogreet)
print("debugger setting:", _PY.config.debugger)
print("script files:", table.concat(_PY.config.scripts or {}, ", "))
print("offline setting:", _PY.config.offline)
print("fibaro setting:", _PY.config.fibaro)
print("=== End Config Test ===")
