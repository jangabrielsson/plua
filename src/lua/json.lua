local json = {}
json.encode = _PY.to_json
json.decode = _PY.parse_json
json.encodeFormated = _PY.to_json_formatted

return json