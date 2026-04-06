  --%%name:TestErr

  local a = {
    c = [[A
  B
  C
  D
  E]]
  }

  local b = json.encode(a)
  print("Encoded JSON:", b)
  local c = json.decode(b)
  print("Decoded JSON:", c)