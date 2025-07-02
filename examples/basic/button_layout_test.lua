--%%name:ButtonLayoutTest
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%% offline:true

--%%u:{label="lbl1",text="Button Layout Test - Different button counts per row"}
--%%u:{{button="btn1",text="1 Button",visible=true,onReleased="testBtn1"}}
--%%u:{{button="btn2",text="Button 1",visible=true,onReleased="testBtn2"},{button="btn3",text="Button 2",visible=true,onReleased="testBtn3"}}
--%%u:{{button="btn4",text="Btn 1",visible=true,onReleased="testBtn4"},{button="btn5",text="Btn 2",visible=true,onReleased="testBtn5"},{button="btn6",text="Btn 3",visible=true,onReleased="testBtn6"}}
--%%u:{{button="btn7",text="B1",visible=true,onReleased="testBtn7"},{button="btn8",text="B2",visible=true,onReleased="testBtn8"},{button="btn9",text="B3",visible=true,onReleased="testBtn9"},{button="btn10",text="B4",visible=true,onReleased="testBtn10"}}
--%%u:{{button="btn11",text="1",visible=true,onReleased="testBtn11"},{button="btn12",text="2",visible=true,onReleased="testBtn12"},{button="btn13",text="3",visible=true,onReleased="testBtn13"},{button="btn14",text="4",visible=true,onReleased="testBtn14"},{button="btn15",text="5",visible=true,onReleased="testBtn15"}}
--%%u:{label="lbl2",text="Full width elements below:"}
--%%u:{slider="slider1",text="Slider",min="0",max="100",visible=true,onChanged="mySlider"}
--%%u:{select="select1",text="Select",visible=true,onToggled="mySelect",value='2',options={{type='option',text='Option 1',value='1'},{type='option',text='Option 2',value='2'},{type='option',text='Option 3',value='3'}}}

function QuickApp:testBtn1(ev)
  print("testBtn1")
end

function QuickApp:testBtn2(ev)
  print("testBtn2")
end

function QuickApp:testBtn3(ev)
  print("testBtn3")
end

function QuickApp:testBtn4(ev)
  print("testBtn4")
end

function QuickApp:testBtn5(ev)
  print("testBtn5")
end

function QuickApp:testBtn6(ev)
  print("testBtn6")
end

function QuickApp:testBtn7(ev)
  print("testBtn7")
end

function QuickApp:testBtn8(ev)
  print("testBtn8")
end

function QuickApp:testBtn9(ev)
  print("testBtn9")
end

function QuickApp:testBtn10(ev)
  print("testBtn10")
end

function QuickApp:testBtn11(ev)
  print("testBtn11")
end

function QuickApp:testBtn12(ev)
  print("testBtn12")
end

function QuickApp:testBtn13(ev)
  print("testBtn13")
end

function QuickApp:testBtn14(ev)
  print("testBtn14")
end

function QuickApp:testBtn15(ev)
  print("testBtn15")
end

function QuickApp:mySlider(ev)
  print("mySlider",ev.values[1])
end

function QuickApp:mySelect(ev)
  print("mySelect",ev.values[1])
end

function QuickApp:onInit()
  self:debug("Button Layout Test initialized")
  setInterval(function() print("PING") end,2000) -- keep script alive
end 