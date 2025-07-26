--%%name:HTMLUpdateTest
--%%type:com.fibaro.multilevelSwitch
--%%desktop:true

--%%u:{label="lbl1",text="Click button to see HTML"}
--%%u:{{button="btn1",text="Test HTML",onReleased="testHTML"}}

function QuickApp:onInit()
  self:debug("onInit - HTML Update Test")
end

function QuickApp:testHTML()
  self:debug("Updating label with HTML content")
  
  -- Test different HTML content
  local htmlContent = "<div style='color:red; font-weight:bold; font-size:16px;'>" ..
                      "🎯 <b>HTML</b> <i>rendering</i> <u>works</u>!" ..
                      "<br/><span style='color:blue;'>This is blue text</span>" ..
                      "<br/><small>Small text with <code>code style</code></small>" ..
                      "</div>"
  
  self:updateView("lbl1", "text", htmlContent)
end
