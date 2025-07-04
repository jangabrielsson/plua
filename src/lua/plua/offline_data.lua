local Emu, store = ...

Emu:registerDevice({
  device ={
    id = 1, name = "zwave", roomID = 219,
    type = "com.fibaro.zwavePrimaryController",
    properties = {
      sunriseHour = "03:57",
      sunsetHour = "21:32",
    }
  }
})

store['settings/location']['_'] = {
  "INIT",{
    houseNumber = 0,
    timezone = "Europe/Stockholm",
    timezoneOffset = 7200,
    ntp = true,
    ntpServer = "pool.ntp.org",
    date = { day = 24, month = 5, year = 2025},
    time = { hour = 6, minute = 8 },
    latitude = Emu.lib.latitude or 59.3169518987572,
    longitude = Emu.lib.longitude or 18.06379775049387,
    city = "Gatan 6, Stockholm, Sweden",
    temperatureUnit = "C",
    windUnit = "km/h",
    timeFormat = 24,
    dateFormat = "dd.mm.yy",
    decimalMark = "."
  }
}

store['settings/info']['_'] = {
  "INIT",{
    serialNumber = "HC3-00000000",
    platform = "HC3",
    zwaveEngineVersion = "2.0",
    zigbeeStatus = true,
    hcName = "HC3-00000000",
    mac = "ac:17:a2:0d:35:e8",
    zwaveVersion = "4.33",
    timeFormat = 24,
    zwaveRegion = "EU",
    serverStatus = 1748004478,
    defaultLanguage = "en",
    defaultRoomId = 219,
    sunsetHour = "00:00",
    sunriseHour = "00:00",
    hotelMode = false,
    temperatureUnit = "C",
    batteryLowNotification = false,
    date = "16:01 | 25.5.2025",
    dateFormat = "dd.mm.yy",
    decimalMark = ".",
    timezoneOffset = 7200,
    currency = "EUR",
    softVersion = "5.180.17",
    beta = false,
    currentVersion = {
      version = "5.180.17",
      type = "stable"
    },
    installVersion = {
      version = "",
      type = "",
      status = "",
      progress = 0
    },
    timestamp = 1748181717,
    online = false,
    tosAccepted = true,
    skin = "light",
    skinSetting = "manual",
    updateStableAvailable = false,
    updateBetaAvailable = false,
    newestStableVersion = "5.180.17",
    newestBetaVersion = "5.0.0",
    isFTIConfigured = true,
    isSlave = false,
    hasFIDConnected = true,
    oemId = "HC3"
  }
}

store['home']['_'] = {
  "INIT",{
    timestamp = 1748181965,
    defaultSensors = {
      temperature = 1630,
      humidity = 0,
      light = 1629
    },
    notificationClient = {
      marketingNotificationAllowed = true
    },
    hcName = "HC3-00000000",
    weatherProvider = 3,
    currency = "EUR",
    fireAlarmTemperature = 60,
    freezeAlarmTemperature = 1,
    timeFormat = 24,
    dateFormat = "dd.mm.yy",
    firstRunAfterUpdate = true
  }
}

store['panels/location'][219] = {
  "POST", {
    id = 219,
    name = "HC3-00000000",
    latitude = Emu.lib.latitude or 59.3169518987572,
    longitude = Emu.lib.longitude or 18.06379775049387,
    radius = 150,
    address = "xyz",
    home = true
  }
}

store['rooms'][219] = {
  "POST", {
    id = 219,
    name = "Default Room",
    sectionID = 219,
    isDefault = true,
    visible = true,
    icon = "room_boy",
    iconExtension = "png",
    iconColor = "purple",
    defaultSensors = {
      temperature = 873,
      humidity = 1875,
      light = 1629
    },
    meters = {
      energy = 0
    },
    defaultThermostat = 353,
    sortOrder = 1,
    category = "pantry"
  }
}

store['sections'][219] = {
  "POST", {
    id = 219,
    name = "Default Section",
    sortOrder = 1
  }
}

store.weather.data = {
  "INIT",{
    Wind = 5.962133916683182,
    WindUnit = "km/h",
    Temperature = 1.4658129805029452,
    WeatherCondition = "WeatherCondition",
    Humidity = 6.027456183070403,
    TemperatureUnit = "TemperatureUnit",
    ConditionCode = 0,
    WeatherConditionConverted = "WeatherConditionConverted"
  }
}
