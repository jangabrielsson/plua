require("busted.runner")()
local runTest

function QuickApp:onInit()
  runTest()
end


function runTest()
  
  describe("Testing std QuickApp functionality", function()
    
    it("should be easy to use", function()
      assert.truthy(quickApp)
    end)
    
  end)
  
end