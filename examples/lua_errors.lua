-- Test lua error messages

--require('mobdebug').on()

a = 9
--fopp()

setTimeout(function() 
    error("FOO")
  end,500)