--%%name:HTMLTest
--%%type:com.fibaro.binarySwitch
--%%desktop:true

--%%u:{label="lbl1",text="Plain text"}
--%%u:{label="lbl2",text="<b>Bold text</b>"}
--%%u:{label="lbl3",text="<span style='color:red;'>Red text</span>"}
--%%u:{label="lbl4",text="<div>Multiple<br/>lines<br/>of text</div>"}
--%%u:{{button="btn1",text="Update HTML",onReleased="updateLabels"}}

function QuickApp:onInit()
  self:debug("onInit - Testing HTML rendering in labels")
end

function QuickApp:updateLabels()
  self:debug("Updating labels with HTML content")
  
  -- Update labels with different HTML content
  self:updateView("lbl1", "text", "<i>Now italic</i>")
  self:updateView("lbl2", "text", "<span style='color:blue; font-size:18px;'>Large blue text</span>")
  self:updateView("lbl3", "text", "<div style='background:yellow; padding:5px;'>Yellow background</div>")
  self:updateView("lbl4", "text", "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>")
end
