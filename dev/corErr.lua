  --%%name:TestErr

  -- Call API on QA toplevel, causes yield error.
  api.post("/plugins/"..plugin.mainDeviceId.."/variables",{ name='test', value="Foo"}) -- create var if not exist