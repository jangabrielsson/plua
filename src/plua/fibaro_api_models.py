"""
Fibaro HC3 API Pydantic Models
Auto-generated from Swagger/OpenAPI specifications.
Contains all data models used by the Fibaro API endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union


# Generated Pydantic Models


class CreateSceneRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    mode: Optional[str] = None
    icon: Optional[str] = None
    content: Optional[str] = None
    maxRunningInstances: Optional[int] = None
    hidden: Optional[bool] = None
    protectedByPin: Optional[bool] = None
    stopOnAlarm: Optional[bool] = None
    enabled: Optional[bool] = None
    restart: Optional[bool] = Field(
        ..., description="Allow to restart a running scene."
    )
    categories: Optional[List[int]] = None
    scenarioData: Optional[ScenarioContent] = None
    roomId: Optional[int] = None


class ExecuteSceneRequest(BaseModel):
    alexaProhibited: Optional[bool] = Field(
        ..., description="Execute scene by alexaProhibited"
    )
    args: Optional[Dict[str, Any]] = None


class FilterSceneRequest(BaseModel):
    pass


class CreateSceneResponse(BaseModel):
    id: Optional[int] = None


class SceneDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    mode: Optional[str] = None
    icon: Optional[str] = None
    iconExtension: Optional[str] = None
    content: Optional[str] = None
    maxRunningInstances: Optional[int] = None
    hidden: Optional[bool] = None
    protectedByPin: Optional[bool] = None
    scenarioData: Optional[ScenarioContent] = None
    stopOnAlarm: Optional[bool] = None
    enabled: Optional[bool] = None
    restart: Optional[bool] = Field(
        ..., description="Allow to restart a running scene."
    )
    categories: Optional[List[int]] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    isRunning: Optional[bool] = Field(
        ..., description="If scene is running return true otherwise false."
    )
    isScenarioDataCorrect: Optional[bool] = Field(
        ...,
        description="If scene is custom scenario and scenario data is incorrect, e.g. device was deleted",
    )
    started: Optional[int] = Field(..., description="Timestamp of the scene start.")
    roomId: Optional[int] = None
    sortOrder: Optional[int] = None


class UpdateSceneRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mode: Optional[str] = None
    maxRunningInstances: Optional[int] = None
    icon: Optional[str] = None
    content: Optional[str] = None
    hidden: Optional[bool] = None
    protectedByPin: Optional[bool] = None
    stopOnAlarm: Optional[bool] = None
    enabled: Optional[bool] = None
    restart: Optional[bool] = Field(
        ..., description="Allow to restart a running scene."
    )
    categories: Optional[List[int]] = None
    scenarioData: Optional[ScenarioContent] = None
    roomId: Optional[int] = None


class ScenarioContent(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    version: Optional[int] = None
    when: Optional[ScenarioContentWhen] = None
    where: Optional[ScenarioContentWhere] = None
    what: Optional[ScenarioContentWhat] = None
    trigger: Optional[ScenarioContentWhere] = None
    turnOffDelay: Optional[int] = None
    actions: Optional[List[Dict[str, Any]]] = None
    triggers: Optional[triggers] = None
    conditions: Optional[conditions] = None


class ScenarioContentWhen(BaseModel):
    daysOfWeek: Optional[List[str]] = None
    exactTime: Optional[str] = None
    afterTime: Optional[str] = None
    timeOffset: Optional[int] = None
    notEarlierThan: Optional[str] = None
    notLaterThan: Optional[str] = None


class ScenarioContentWhere(BaseModel):
    wholeHouse: Optional[bool] = None
    sections: Optional[List[int]] = None
    rooms: Optional[List[int]] = None
    devices: Optional[List[int]] = None


class ScenarioContentWhat(BaseModel):
    action: Optional[Dict[str, Any]] = None


class triggers(BaseModel):
    pass


class conditions(BaseModel):
    pass


class complexConditions(BaseModel):
    group: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    conditions: conditions
    operator: str


class deviceTriggerOrCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    id: float
    property: str
    operator: str
    value: Dict[str, Any]
    duration: Optional[float] = None


class profileTriggerOrCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    value: float
    property: str
    operator: str
    duration: Optional[float] = None


class cronTriggerOrCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    property: str
    operator: str
    value: Dict[str, Any]


class cron(BaseModel):
    pass


class interval(BaseModel):
    date: cron
    interval: float


class weatherBasicCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    value: float
    property: str
    operator: str
    duration: Optional[float] = None


class weatherConditionsCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    value: str
    property: str
    operator: str
    duration: Optional[float] = None


class isDayOrNightCondition(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    operator: str
    value: bool
    property: Optional[str] = None


class sunEventTrigger(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    property: str
    value: float
    operator: str


class deviceAction(BaseModel):
    group: str
    id: List[float]
    action: str
    args: List[Dict[str, Any]]
    delay: Optional[float] = None


class profileAction(BaseModel):
    group: str
    id: float
    action: str
    delay: Optional[float] = None


class remoteControllerTrigger(BaseModel):
    group: str
    type_: str = Field(..., alias="type")
    id: float
    property: str
    value: Dict[str, Any]
    operator: str


class DeviceIconDto(BaseModel):
    deviceType: Optional[str] = None
    iconSetName: Optional[str] = None
    id: Optional[int] = None
    fileExtension: Optional[str] = None


class RoomIconDto(BaseModel):
    iconName: Optional[str] = None
    id: Optional[int] = None
    fileExtension: Optional[str] = None


class SceneIconDto(BaseModel):
    iconName: Optional[str] = None
    id: Optional[int] = None
    fileExtension: Optional[str] = None


class CreatedIconDto(BaseModel):
    id: Optional[int] = None
    iconSetName: Optional[str] = None


class IconListDto(BaseModel):
    device: Optional[List[DeviceIconDto]] = None
    room: Optional[List[RoomIconDto]] = None
    scene: Optional[List[SceneIconDto]] = None


class SortOrderRequest(BaseModel):
    from_: Optional[int] = Field(None, alias="from")
    to_: Optional[int] = Field(None, alias="to")
    fromSection: Optional[int] = None
    toSection: Optional[int] = None
    fromRoom: Optional[int] = None
    toRoom: Optional[int] = None
    fromType: Optional[str] = None
    toType: Optional[str] = None
    action: Optional[str] = None


class FavoriteColor(BaseModel):
    id: Optional[int] = None
    r: Optional[int] = None
    g: Optional[int] = None
    b: Optional[int] = None
    w: Optional[int] = None
    brightness: Optional[int] = None
    created: Optional[int] = None
    modified: Optional[int] = None


class NewFavoriteColor(BaseModel):
    r: Optional[int] = None
    g: Optional[int] = None
    b: Optional[int] = None
    w: Optional[int] = None
    brightness: Optional[int] = None


class RefreshStateDto(BaseModel):
    status: Optional[str] = None
    last: Optional[int] = None
    date: Optional[str] = None
    timestamp: Optional[int] = None
    logs: Optional[List[DebugMessageDto]] = None
    events: Optional[List[Dict[str, Any]]] = None
    changes: Optional[List[Dict[str, Any]]] = None
    alarmChanges: Optional[List[Dict[str, Any]]] = None


class ProfileCreateDto(BaseModel):
    name: Optional[str] = None
    iconId: Optional[int] = None
    sourceId: Optional[int] = None


class ProfileServiceDto(BaseModel):
    activeProfile: Optional[int] = None
    profiles: Optional[List[ProfileDto]] = None


class ProfileDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    iconId: Optional[int] = None
    devices: Optional[List[DeviceActorDto]] = None
    scenes: Optional[List[SceneActorDto]] = None
    partitions: Optional[List[PartitionActionDto]] = None
    climateZones: Optional[List[ClimateZonesActionDto]] = None


class DeviceActorDto(BaseModel):
    id: Optional[int] = None
    action: Optional[DeviceActionDto] = None


class SceneActorDto(BaseModel):
    sceneId: Optional[int] = None
    actions: Optional[List[action]] = None


class PartitionActionDto(BaseModel):
    partitionId: Optional[int] = None
    action: Optional[str] = None


class ClimateZonesActionDto(BaseModel):
    id: int
    mode: ClimateZonesActionMode
    properties: Optional[ClimateZonesActionProperties] = None


class ClimateZonesActionMode(BaseModel):
    pass


class ClimateZonesActionProperties(BaseModel):
    handSetPointHeating: Optional[float] = Field(
        ..., description="Heating temperature for manual mode"
    )
    handSetPointCooling: Optional[float] = Field(
        ..., description="Cooling temperature for manual mode"
    )
    handMode: Optional[ClimateZonesActionHandMode] = None


class ClimateZonesActionHandMode(BaseModel):
    pass


class PartitionActionUpdateDto(BaseModel):
    action: Optional[str] = None


class ClimateZoneActionUpdateDto(BaseModel):
    mode: ClimateZonesActionMode
    properties: Optional[ClimateZonesActionProperties] = None


class SceneActorUpdateDto(BaseModel):
    actions: Optional[List[action]] = None


class action(BaseModel):
    pass


class DeviceActionDto(BaseModel):
    name: str
    isUIAction: Optional[bool] = None
    args: List[Dict[str, Any]]


class CpuLoad(BaseModel):
    name: Optional[str] = Field(..., description="CPU core name")
    idle: Optional[float] = None
    nice: Optional[float] = None
    system: Optional[float] = None
    user: Optional[float] = None


class Memory(BaseModel):
    buffers: Optional[int] = None
    cache: Optional[int] = None
    free: Optional[int] = None
    used: Optional[int] = None


class Storage(BaseModel):
    name: Optional[str] = None
    used: Optional[int] = None


class Diagnostic(BaseModel):
    cpuLoad: Optional[List[CpuLoad]] = None
    memory: Optional[Memory] = None
    storage: Optional[Diagnostic_storage] = None


class Diagnostic_storage(BaseModel):
    internal: Optional[List[Storage]] = None


class DiagnosticTransmissions(BaseModel):
    items: Optional[List[DiagnosticTransmissionsItem]] = None
    since: Optional[float] = None
    until: Optional[float] = None


class DiagnosticTransmissionsItem(BaseModel):
    incomingFailedCrc: Optional[float] = None
    incomingFailedDecryption: Optional[float] = None
    incomingNonceGet: Optional[float] = None
    incomingNonceReport: Optional[float] = None
    incomingTimedOutNonce: Optional[float] = None
    incomingTotal: Optional[float] = None
    nodeId: Optional[float] = None
    outgoingFailed: Optional[float] = None
    outgoingNonceGet: Optional[float] = None
    outgoingTotal: Optional[float] = None


class UserCreateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")


class UserDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    password: Optional[str] = None
    pin: Optional[str] = None
    passwordConfirm: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    email: Optional[str] = None
    alarmRights: Optional[List[int]] = None
    climateZoneRights: Optional[List[int]] = None
    profileRights: Optional[List[int]] = None
    raStatus: Optional[str] = None
    isAdminTransferPossible: Optional[bool] = None
    rights: Optional[UserDtoRights] = None
    hotelRoom: Optional[int] = None
    sendNotifications: Optional[bool] = None
    tracking: Optional[int] = None
    useOptionalArmPin: Optional[bool] = None
    useIntegrationPin: Optional[bool] = None
    integrationPin: Optional[str] = None
    initialWizard: Optional[bool] = None
    pendingAdminRoleTransfer: Optional[bool] = None
    fidUuid: Optional[str] = None
    fidLastSynchronizationTimestamp: Optional[int] = None
    fidRole: Optional[str] = None
    skin: Optional[str] = None
    skinSetting: Optional[str] = None
    isAddTileVisible: Optional[bool] = None
    buiSettings: Optional[Dict[str, Any]] = None


class UserDtoRights(BaseModel):
    advanced: Optional[Dict[str, Any]] = None
    devices: Optional[Dict[str, Any]] = None
    scenes: Optional[Dict[str, Any]] = None
    alarmPartitions: Optional[Dict[str, Any]] = None
    profiles: Optional[Dict[str, Any]] = None
    climateZones: Optional[Dict[str, Any]] = None


class DebugMessagesDto(BaseModel):
    nextLast: Optional[float] = None
    messages: Optional[List[DebugMessageDto]] = None


class DebugMessageDto(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[int] = None
    type_: Optional[str] = Field(None, alias="type")
    tag: Optional[str] = None
    message: Optional[str] = None


class DefaultSensors(BaseModel):
    temperature: Optional[int] = None
    humidity: Optional[int] = None
    light: Optional[int] = None


class IconColor(BaseModel):
    pass


class RoomCreateRequest(BaseModel):
    name: str
    sectionID: int
    category: str
    icon: str
    iconExtension: Optional[str] = None
    iconColor: Optional[IconColor] = None
    visible: Optional[bool] = None


class RoomUpdateRequest(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sectionID: Optional[int] = None
    icon: Optional[str] = None
    iconExtension: Optional[str] = None
    iconColor: Optional[IconColor] = None
    defaultSensors: Optional[DefaultSensors] = None
    defaultThermostat: Optional[int] = None
    sortOrder: Optional[int] = None
    category: Optional[str] = None
    visible: Optional[bool] = None


class RoomDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sectionID: Optional[int] = None
    isDefault: Optional[bool] = None
    visible: Optional[bool] = None
    icon: Optional[str] = None
    iconExtension: Optional[str] = None
    iconColor: Optional[IconColor] = None
    defaultSensors: Optional[DefaultSensors] = None
    defaultThermostat: Optional[int] = None
    sortOrder: Optional[int] = None
    category: Optional[str] = None


class RoomGroupAssignment(BaseModel):
    deviceIds: Optional[List[int]] = None


class TimeIntervalEnum(BaseModel):
    pass


class ConsumptionMeasurementEnum(BaseModel):
    pass


class EnergyDeviceInfo(BaseModel):
    id: Optional[float] = Field(..., description="Id of device")
    deleted: Optional[bool] = Field(..., description="Is device deleted")
    roomId: Optional[float] = Field(..., description="Id of room")
    mainEnergyMeter: Optional[bool] = Field(..., description="Is main energy meter")


class EnergyValueDto(BaseModel):
    pass


class PowerValueDto(BaseModel):
    pass


class EnergyCostDto(BaseModel):
    pass


class DateTimeUnitDto(BaseModel):
    pass


class BillingDurationEnum(BaseModel):
    pass


class EnergyBillingPeriodDto(BaseModel):
    duration: Optional[BillingDurationEnum] = Field(
        ...,
        description="How long the billing period lasts - curently only 1,2,3,6,12 months are supported",
    )
    startDate: Optional[str] = Field(
        ..., description="Day at which billing period started: YYYY-MM-DD"
    )
    endDate: Optional[str] = Field(
        ...,
        description="Day at which billing period ended: YYYY-MM-DD. This value is empty for current period.",
    )
    fixedCost: Optional[float] = Field(..., description="Fixed cost per billing period")


class EnergyDeviceEntryDto(BaseModel):
    id: Optional[int] = Field(..., description="id of device")
    name: Optional[str] = Field(
        ...,
        description="name of device; this is important if record coresponds to device that is already deleted",
    )
    roomId: Optional[int] = Field(
        ...,
        description="Id of room the device is in; this is important if record coresponds to device that is already deleted",
    )
    consumption: Optional[EnergyValueDto] = None
    production: Optional[EnergyValueDto] = None
    consumptionCost: Optional[EnergyCostDto] = None
    productionCost: Optional[EnergyCostDto] = None


class EnergyRoomEntryDto(BaseModel):
    id: Optional[int] = Field(..., description="id of room")
    production: Optional[EnergyValueDto] = None
    consumption: Optional[EnergyValueDto] = None
    productionCost: Optional[EnergyCostDto] = None
    consumptionCost: Optional[EnergyCostDto] = None


class EnergyCategoryEntryDto(BaseModel):
    category: Optional[str] = Field(..., description="name of category")
    production: Optional[EnergyValueDto] = None
    consumption: Optional[EnergyValueDto] = None
    productionCost: Optional[EnergyCostDto] = None
    consumptionCost: Optional[EnergyCostDto] = None


class EnergySummaryDto(BaseModel):
    production: Optional[EnergyValueDto] = None
    consumption: Optional[EnergyValueDto] = None
    productionCost: Optional[EnergyCostDto] = None
    consumptionCost: Optional[EnergyCostDto] = None
    topConsumingDevices: Optional[List[EnergyDeviceEntryDto]] = None


class EnergyMetricsDto(BaseModel):
    productionPower: Optional[PowerValueDto] = None
    consumptionPower: Optional[PowerValueDto] = None


class EnergyDetailDto(BaseModel):
    energy: Optional[List[Dict[str, Any]]] = None


class EnergyRoomDetailDto(BaseModel):
    energy: Optional[List[Dict[str, Any]]] = None


class EnergyDeviceDetailDto(BaseModel):
    energy: Optional[List[Dict[str, Any]]] = None


class EnergyBillingSummaryTypesDto(BaseModel):
    currentBillingPeriod: Optional[EnergyBillingSummaryDto] = None
    previousBillingPeriod: Optional[EnergyBillingSummaryDto] = None


class EnergyBillingSummaryDto(BaseModel):
    startDate: Optional[DateTimeUnitDto] = None
    endDate: Optional[DateTimeUnitDto] = None
    productionCost: Optional[float] = Field(
        ..., description="Cost of energy produced during billig period"
    )
    consumptionCost: Optional[float] = Field(
        ..., description="Cost of energy consumed during billig period"
    )
    production: Optional[EnergyValueDto] = None
    consumption: Optional[EnergyValueDto] = None


class InstallationCostDto(BaseModel):
    id: Optional[int] = Field(..., description="Id of installation cost")
    date: Optional[str] = Field(..., description="YYYY-MM-DD")
    cost: Optional[float] = Field(..., description="cost of installation >= 0")
    name: Optional[str] = Field(..., description="installation cost name")


class DayEnum(BaseModel):
    pass


class EnergyAdditionalTariffDto(BaseModel):
    """represents kWh cost for specified period of time during week (from startTime to endTime in specified days)"""

    rate: Optional[float] = Field(..., description="how much 1kWh costs")
    name: Optional[str] = Field(..., description="name of tariff")
    startTime: Optional[str] = Field(..., description="HH:mm")
    endTime: Optional[str] = Field(
        ...,
        description="HH:mm if endTime<startTime it means next day (e.g.: from 23:00 till 03:00 next day)",
    )
    days: Optional[List[DayEnum]] = None


class EnergyTariffDto(BaseModel):
    rate: Optional[float] = Field(..., description="how much 1kWh costs")
    name: Optional[str] = Field(..., description="name of main tariff")
    returnRate: Optional[float] = Field(..., description="rate of return ")
    additionalTariffs: Optional[List[EnergyAdditionalTariffDto]] = Field(
        ...,
        description="additionl tariffs for some time periods during week. The higher the tariff in the list, the more priority it has",
    )


class SavingsDetailsDto(BaseModel):
    periodStart: Optional[DateTimeUnitDto] = None
    periodEnd: Optional[DateTimeUnitDto] = None
    production: Optional[EnergyValueDto] = None
    consumption: Optional[EnergyValueDto] = None
    productionCost: Optional[EnergyCostDto] = None
    consumptionCost: Optional[EnergyCostDto] = None
    devices: Optional[List[EnergyDeviceEntryDto]] = None


class SavingsSummaryDto(BaseModel):
    hasProduction: Optional[bool] = Field(
        ..., description="Determines whether user has producing device"
    )
    installationCost: Optional[float] = Field(
        ..., description="Installation cost (producing device only)"
    )
    averageReturn: Optional[float] = Field(
        ..., description="Average return per billing period (producing device only)"
    )
    averageReturnPeriod: Optional[BillingDurationEnum] = Field(
        ..., description="Billing period for average return (producing device only)"
    )
    alreadyReturned: Optional[float] = Field(
        ..., description="An amount of produced energy in money (producing device only)"
    )
    currentPeriodCost: Optional[float] = Field(
        ...,
        description="Cost of enrgy in current billing period (without producing device only)",
    )
    averageCost: Optional[float] = Field(
        ...,
        description="Average cost of energy per billing period (without producing device only)",
    )
    averageCostPeriod: Optional[BillingDurationEnum] = Field(
        ...,
        description="Billing period for average cost (without producing device only)",
    )
    currentYearCost: Optional[float] = Field(
        ...,
        description="Cost of energy in current year (without producing device only)",
    )


class SavingsInstallationDto(BaseModel):
    period: Optional[DateTimeUnitDto] = None
    production: Optional[EnergyValueDto] = None
    productionCost: Optional[EnergyCostDto] = None


class EcologySummaryDto(BaseModel):
    productionStart: Optional[str] = Field(
        ..., description="Date when energy production has started"
    )
    selfSufficiency: Optional[float] = Field(
        ...,
        description="Percentage value describing how many of produced energy is directly used by the household",
    )
    treesPlanted: Optional[float] = Field(
        ..., description="Equivalent of produced energy in trees planted"
    )
    reductionCO2: Optional[float] = Field(
        ..., description="Tons of CO2 reduced thanks to produced energy"
    )


class EcologyDetailsDto(BaseModel):
    periodStart: Optional[DateTimeUnitDto] = None
    periodEnd: Optional[DateTimeUnitDto] = None
    treesPlanted: Optional[float] = Field(
        ..., description="Cumulative equivalent of produced energy in trees planted"
    )
    reductionCO2: Optional[float] = Field(
        ..., description="Cumulative tons of CO2 reduced thanks to produced energy"
    )


class EnergySettingsDto(BaseModel):
    consumptionMeasurement: Optional[ConsumptionMeasurementEnum] = None
    energyConsumptionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as energy consumption meters."
    )
    energyProductionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as energy production meters."
    )
    powerConsumptionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as power consumption meters."
    )
    powerProductionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as power production meters."
    )
    gridConsumptionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as grid energy consumption meters."
    )
    gridProductionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as grid energy production meters."
    )
    gridPowerConsumptionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as grid power consumption meters."
    )
    gridPowerProductionMeters: Optional[List[float]] = Field(
        ..., description="List of device ids set as grid power production meters."
    )


class ResetRequestDto(BaseModel):
    recovery: Optional[bool] = None


class Energy(BaseModel):
    id: Optional[int] = None
    totalEnergy: Optional[float] = None
    current: Optional[EnergyData] = None
    total: Optional[EnergyData] = None


class EnergyData(BaseModel):
    H: Optional[float] = None
    D: Optional[float] = None
    W: Optional[float] = None
    M: Optional[float] = None
    Y: Optional[float] = None
    costH: Optional[float] = None
    costD: Optional[float] = None
    costW: Optional[float] = None
    costM: Optional[float] = None
    costY: Optional[float] = None


class Temperature(BaseModel):
    id: Optional[int] = None
    temperatureD: Optional[float] = None
    temperatureH: Optional[float] = None
    temperatureM: Optional[float] = None
    temperatureW: Optional[float] = None


class EnergyFromTo(BaseModel):
    pass


class DataTypeRoomsOrDevices(BaseModel):
    pass


class DataTypeSummaryOrCompare(BaseModel):
    pass


class TemperatureFromTo(BaseModel):
    pass


class CoFromToArray(BaseModel):
    pass


class CoFromTo(BaseModel):
    timestamp: float
    value: Dict[str, Any]
    id: float


class SmokeFromTo(BaseModel):
    smoke: List[List[float]]
    temperature: List[List[float]]
    max: float


class ThermostatMode(BaseModel):
    pass


class ThermostatFromTo(BaseModel):
    targetLevel: List[List[float]]
    temperature: List[List[float]]
    thermostatMode: List[List[Dict[str, Any]]]
    min: float
    max: float


class iOSDev(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    push: Optional[bool] = None
    udid: Optional[str] = None


class Weather(BaseModel):
    ConditionCode: Optional[int] = None
    Humidity: Optional[float] = None
    Temperature: Optional[float] = None
    TemperatureUnit: Optional[str] = None
    WeatherCondition: Optional[str] = None
    WeatherConditionConverted: Optional[str] = None
    Wind: Optional[float] = None
    WindUnit: Optional[str] = None


class NotificationType(BaseModel):
    pass


class ChannelType(BaseModel):
    pass


class IntervalType(BaseModel):
    pass


class NotificationsSettings(BaseModel):
    type_: NotificationType = Field(..., alias="type")
    active: bool
    label: str
    interval: Dict[str, Any]
    channels: List[ChannelType]
    supportedChannels: Optional[List[ChannelType]] = None
    users: List[int]
    supportedInterval: Optional[List[IntervalType]] = None
    category: Optional[str] = None


class DeviceNotificationsSettings(BaseModel):
    deviceId: int
    notifications: List[NotificationsSettings]


class SectionCreateRequest(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class SectionUpdateRequest(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    sortOrder: Optional[int] = None


class SectionDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    sortOrder: Optional[int] = None


class FavoriteColorV2(BaseModel):
    id: int
    colorComponents: Dict[str, Any]
    brightness: int
    created: Optional[int] = None
    modified: Optional[int] = None


class NewFavoriteColorV2(BaseModel):
    colorComponents: Dict[str, Any]
    brightness: int


class DeviceNetworkDataDto(BaseModel):
    ip: Optional[str] = None
    mac: Optional[str] = None
    vendor: Optional[str] = None


class NetworkDiscoveryDto(BaseModel):
    mac: Optional[List[str]] = None


class priorityEnum(BaseModel):
    pass


class NotificationCenterDto(BaseModel):
    id: Optional[int] = Field(..., description="Notification unique id")
    priority: Optional[str] = Field(
        ..., description="Notification priority: 'info', 'warning' or 'alert'"
    )
    wasRead: Optional[bool] = Field(
        ...,
        description="Flag: if true: notification marked as read, if false: notification marked as unread",
    )
    canBeDeleted: Optional[bool] = Field(
        ...,
        description="Flag:if true: notification can be deleted, if false: notification can't be deleted",
    )
    type_: Optional[str] = Field(
        ...,
        alias="type",
        description="Notification type, each type of notification has its own data structure",
    )
    created: Optional[int] = Field(
        ..., description="Timestamp: Date and time of creation"
    )
    data: Optional[NotificationCenterDataDto] = None


class NotificationCenterRequestDto(BaseModel):
    priority: Optional[str] = Field(
        ..., description="Notification priority: 'info', 'warning' or 'alert'"
    )
    wasRead: Optional[bool] = Field(
        ...,
        description="Flag: if true: notification marked as read, if false: notification marked as unread",
    )
    canBeDeleted: Optional[bool] = Field(
        ...,
        description="Flag:if true: notification can be deleted, if false: notification can't be deleted",
    )
    type_: Optional[str] = Field(
        ...,
        alias="type",
        description="Notification type, each type of notification has its own data structure",
    )
    data: Optional[NotificationCenterDataDto] = None


class NotificationCenterDataDto(BaseModel):
    """Data describing the characteristics of individual notifications. Data specific to particular types of notifications."""

    deviceId: Optional[int] = Field(
        ...,
        description="Scene id associated with notification. Return SatelConfigurationRequest, FirmwareUpdateRequest and GenericDeviceRequest",
    )
    sceneId: Optional[int] = Field(
        ...,
        description="Scene id associated with notification. Return for GenericSceneRequest",
    )
    taskId: Optional[int] = Field(
        ...,
        description="Task id associated with notification. Return for ZwaveReconfigurationNotificationRequest",
    )
    title: Optional[str] = Field(
        ...,
        description="Notification title. Return for GenericDeviceRequest and GenericSceneRequest",
    )
    text: Optional[str] = Field(
        ...,
        description="Text describing the notification, visible in the notification center.Return for GenericDeviceRequest, \
            GenericSceneRequest and GenericSystemNotificationRequest",
    )
    name: Optional[str] = Field(
        ...,
        description="Notification name. Return for GenericSystemNotificationRequest",
    )
    subType: Optional[str] = Field(
        ...,
        description="Additional type for GenericSystemNotification. Possible options: 'Generic', 'EmailInvalid', 'DeviceNotConfigured', 'DeviceNoTemplate', \
            'NoFibaroPartitionInAlarm', 'ZwavePollingTime', 'UserNameDuplicated'. Return for GenericSystemNotificationRequest",
    )
    status: Optional[str] = Field(
        ...,
        description="Notification status for FirmwareUpdateNotification. Possible options: 'Available', 'QueuedForUpdate', 'Downloading', 'WaitingForCommunication', \
        'Updating', 'UpdateOk', 'UpdateFail', 'UpToDate', 'QueuedForCheck'. Return for GenericSystemNotificationRequest",
    )
    url: Optional[str] = Field(
        ...,
        description="Notification button url. Return for GenericSystemNotificationRequest",
    )
    urlText: Optional[str] = Field(
        ...,
        description="Notification button text. Return for GenericSystemNotificationRequest",
    )
    info: Optional[str] = Field(
        ...,
        description="Additional info about firmware update. Return for FirmwareUpdateRequest",
    )
    progress: Optional[int] = Field(
        ...,
        description="Progress of the operation related to notification (in percent: 0-100). Return for SatelConfigurationRequest and FirmwareUpdateRequest",
    )
    icon: Optional[NotificationCenterDataIconDto] = None


class NotificationCenterDataIconDto(BaseModel):
    """Notification icon. Return for GenericDeviceRequest"""

    path: Optional[str] = Field(..., description="Path to icon file")
    source: Optional[str] = Field(..., description="Icon source")


class ColorDto(BaseModel):
    b: Optional[int] = None
    g: Optional[int] = None
    r: Optional[int] = None
    w: Optional[int] = None


class StepDto(BaseModel):
    color: Optional[ColorDto] = None
    duration: Optional[int] = None
    transitionTime: Optional[int] = None


class ProgramDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    totalDurationTime: Optional[float] = None
    steps: Optional[List[StepDto]] = None


class CreateProgramRequest(BaseModel):
    created: Optional[int] = None
    id: Optional[int] = None
    modified: Optional[int] = None
    name: Optional[str] = None
    steps: Optional[List[StepDto]] = None
    totalDurationTime: Optional[int] = None


class CreateQuickAppRequest(BaseModel):
    name: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    roomId: Optional[float] = None
    initialProperties: Optional[Dict[str, Any]] = None
    initialInterfaces: Optional[List[str]] = None
    initialView: Optional[Dict[str, Any]] = None


class QuickAvailableTypeDto(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    label: Optional[str] = None


class QuickAppFile(BaseModel):
    name: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    isOpen: Optional[bool] = None
    isMain: Optional[bool] = None


class QuickAppFileDetails(BaseModel):
    name: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    isOpen: Optional[bool] = None
    isMain: Optional[bool] = None
    content: Optional[str] = None


class QuickAppExportRequest(BaseModel):
    encrypted: Optional[bool] = Field(
        ..., description="If true encrypted file will be exported."
    )
    serialNumbers: Optional[List[str]] = Field(
        ...,
        description="List of serial numbers with the possibility to import the quick app. Requires encrypted field to be true.",
    )


class HCErrorDto(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    reason: Optional[str] = None
    message: Optional[str] = Field(
        ..., description="Datild infomations about an error."
    )


class Icon(BaseModel):
    path: Optional[str] = None
    source: Optional[str] = None
    overlay: Optional[str] = None


class BlackBoxDto(BaseModel):
    fileName: Optional[str] = None
    state: Optional[str] = None
    timestamp: Optional[float] = None


class DeviceListFiltersDto(BaseModel):
    filters: List[DeviceListFilterDto] = Field(
        ..., description="Set of device filters that all should be fulfilled"
    )
    attributes: Dict[str, Any] = Field(
        ..., description="Defines which device attributes will be returned"
    )


class DeviceListFilterDto(BaseModel):
    filter_: Optional[str] = Field(None, alias="filter")
    value: Optional[List[Dict[str, Any]]] = None


class DevicesInterfacesDto(BaseModel):
    devicesId: List[int] = Field(
        ...,
        description="List of device ids for which we want to add/delete interfaces.",
    )
    interfaces: List[str] = Field(
        ...,
        description="List of interfaces which we want to add/delete to/from devices.",
    )


class RateType(BaseModel):
    pass


class ButtonType(BaseModel):
    pass


class DoorLockMode(BaseModel):
    pass


class DeviceAvailableSceneDto(BaseModel):
    name: Optional[str] = None
    sceneId: Optional[float] = None


class DevicePropertiesDto(BaseModel):
    alarmLevel: Optional[int] = None
    alarmType: Optional[int] = None
    armed: Optional[bool] = None
    autoOffChannel1: Optional[float] = None
    autoOffChannel2: Optional[float] = None
    zwaveResources: Optional[List[ResourceTypeDto]] = None
    associationMode: Optional[int] = None
    availableDoorLockModes: Optional[List[DoorLockMode]] = None
    availablePositions: Optional[List[AvailablePosition]] = None
    availableScenes: Optional[List[DeviceAvailableSceneDto]] = None
    batteryLevel: Optional[int] = None
    batteryLowNotification: Optional[bool] = None
    blackBox: Optional[BlackBoxDto] = None
    buttonHold: Optional[int] = None
    buttonsType: Optional[ButtonType] = None
    currentHumidity: Optional[int] = None
    showFreezeAlarm: Optional[bool] = None
    showFireAlarm: Optional[bool] = None
    buttonType: Optional[Dict[str, Any]] = None
    configurationSourceDeviceId: Optional[float] = None
    motorInversion: Optional[bool] = None
    restoreStateAfterPowerShortage: Optional[bool] = None
    voltageMeasurementReport: Optional[int] = None
    steeringInversion: Optional[bool] = None
    movingUpTime: Optional[int] = None
    movingDownTime: Optional[int] = None
    slatsRotationTime: Optional[int] = None
    virtualBottomLimit: Optional[int] = None
    cameraType: Optional[int] = None
    categories: Optional[List[str]] = None
    calibrationVariants: Optional[List[str]] = None
    calibrated: Optional[bool] = None
    centralSceneSupport: Optional[List[CentralScene]] = None
    channel1: Optional[str] = None
    channel2: Optional[str] = None
    channel3: Optional[str] = None
    channel4: Optional[str] = None
    climateZoneHash: Optional[str] = None
    climateZoneId: Optional[int] = None
    configured: Optional[bool] = None
    dead: Optional[bool] = None
    position: Optional[str] = None
    port: Optional[float] = None
    strategy: Optional[str] = None
    deadReason: Optional[str] = None
    defInterval: Optional[int] = None
    defaultPartyTime: Optional[int] = None
    defaultTone: Optional[int] = None
    defaultWateringTime: Optional[int] = None
    deviceControlType: Optional[int] = None
    deviceRole: Optional[DeviceRole] = None
    deviceState: Optional[str] = None
    supportedDeviceRoles: Optional[List[DeviceRole]] = None
    deviceGroup: Optional[List[int]] = None
    raStatus: Optional[str] = None
    deviceGroupMaster: Optional[int] = None
    deviceIcon: Optional[int] = None
    devices: Optional[List[int]] = None
    devicesInitializationProcess: Optional[str] = None
    DeviceUID: Optional[str] = None
    displayOnMainPage: Optional[int] = None
    doorLockMode: Optional[DoorLockMode] = None
    emailNotificationID: Optional[int] = None
    emailNotificationType: Optional[int] = None
    endPointId: Optional[int] = None
    externalSensorConnected: Optional[bool] = None
    favoritePositionsNativeSupport: Optional[bool] = None
    favoritePositions: Optional[List[FavoritePositions]] = None
    fgrgbwMode: Optional[str] = None
    fidUuid: Optional[str] = None
    fidLastSynchronizationTimestamp: Optional[int] = None
    fidRole: Optional[str] = None
    firmwareUpdate: Optional[DeviceFirmwareUpdateDto] = None
    gatewayId: Optional[str] = None
    humidityThreshold: Optional[int] = None
    httpsEnabled: Optional[bool] = None
    icon: Optional[Icon] = None
    includeInEnergyPanel: Optional[bool] = None
    inputToChannelMap: Optional[DeviceInputToChannelMapDto] = None
    ip: Optional[str] = None
    isLight: Optional[bool] = None
    jpgPath: Optional[str] = None
    lastBreached: Optional[float] = None
    lastHealthy: Optional[float] = None
    lastLoggedUser: Optional[float] = None
    lastModerate: Optional[float] = None
    liliOffCommand: Optional[str] = None
    liliOnCommand: Optional[str] = None
    linkedDeviceType: Optional[str] = None
    localProtectionEnabledChannel1: Optional[bool] = None
    localProtectionEnabledChannel2: Optional[bool] = None
    localProtectionState: Optional[int] = None
    localProtectionSupport: Optional[int] = None
    log: Optional[str] = None
    logTemp: Optional[str] = None
    manufacturer: Optional[str] = None
    markAsDead: Optional[bool] = None
    maxInterval: Optional[int] = None
    maxUsers: Optional[int] = None
    maxValue: Optional[int] = None
    maxVoltage: Optional[int] = None
    minInterval: Optional[int] = None
    minValue: Optional[int] = None
    minVoltage: Optional[int] = None
    mjpgPath: Optional[str] = None
    mode: Optional[float] = None
    model: Optional[str] = None
    moveDownPath: Optional[str] = None
    moveLeftPath: Optional[str] = None
    moveRightPath: Optional[str] = None
    moveStopPath: Optional[str] = None
    moveUpPath: Optional[str] = None
    networkStatus: Optional[str] = None
    niceId: Optional[int] = None
    niceProtocol: Optional[str] = None
    nodeId: Optional[int] = None
    numberOfSupportedButtons: Optional[int] = None
    offset: Optional[str] = None
    overridesSchedule: Optional[bool] = None
    output1Id: Optional[float] = None
    output2Id: Optional[float] = None
    outputsChannelsConnected: Optional[bool] = None
    panicMode: Optional[bool] = None
    parameters: Optional[List[DevicePropertiesDto_parameters]] = None
    parametersTemplate: Optional[float] = None
    password: Optional[str] = None
    pendingActions: Optional[bool] = None
    pollingDeadDevice: Optional[bool] = None
    pollingInterval: Optional[float] = None
    pollingTimeSec: Optional[str] = None
    power: Optional[float] = None
    productInfo: Optional[str] = None
    protectionExclusiveControl: Optional[float] = None
    protectionExclusiveControlSupport: Optional[float] = None
    protectionState: Optional[float] = None
    protectionTimeout: Optional[float] = None
    protectionTimeoutSupport: Optional[bool] = None
    pushNotificationID: Optional[int] = None
    pushNotificationType: Optional[float] = None
    rateType: Optional[RateType] = None
    refreshTime: Optional[int] = None
    remoteId: Optional[int] = None
    remoteGatewayId: Optional[int] = None
    RFProtectionEnabledChannel1: Optional[bool] = None
    RFProtectionEnabledChannel2: Optional[bool] = None
    RFProtectionState: Optional[int] = None
    RFProtectionSupport: Optional[int] = None
    rtspPath: Optional[str] = None
    rtspPort: Optional[int] = None
    saveLogs: Optional[bool] = None
    slatsRange: Optional[int] = None
    slatsRangeMin: Optional[int] = None
    slatsRangeMax: Optional[int] = None
    storeEnergyData: Optional[bool] = None
    saveToEnergyPanel: Optional[bool] = None
    schedules: Optional[List[Dict[str, Any]]] = None
    securityLevel: Optional[str] = None
    securitySchemes: Optional[List[str]] = None
    sendStopAfterMove: Optional[bool] = None
    serialNumber: Optional[str] = None
    showEnergy: Optional[bool] = None
    state: Optional[Dict[str, Any]] = None
    energy: Optional[float] = None
    sipUserPassword: Optional[str] = None
    sipDisplayName: Optional[str] = None
    sipUserID: Optional[str] = None
    sipUserEnabled: Optional[bool] = None
    smsNotificationID: Optional[int] = None
    smsNotificationType: Optional[float] = None
    softwareVersion: Optional[str] = None
    stepInterval: Optional[float] = None
    supportedThermostatFanModes: Optional[List[str]] = None
    supportedThermostatModes: Optional[List[str]] = None
    supportedTones: Optional[List[Dict[str, Any]]] = None
    tamperMode: Optional[str] = None
    targetLevel: Optional[float] = None
    targetLevelDry: Optional[float] = None
    targetLevelHumidify: Optional[float] = None
    targetLevelMax: Optional[float] = None
    targetLevelMin: Optional[float] = None
    targetLevelStep: Optional[float] = None
    targetLevelTimestamp: Optional[float] = None
    thermostatFanMode: Optional[str] = None
    thermostatFanOff: Optional[bool] = None
    thermostatFanState: Optional[str] = None
    thermostatMode: Optional[str] = None
    thermostatModeFuture: Optional[str] = None
    thermostatOperatingState: Optional[str] = None
    thermostatModeManufacturerData: Optional[List[int]] = None
    thermostatState: Optional[str] = None
    powerConsumption: Optional[float] = None
    timestamp: Optional[int] = None
    tone: Optional[int] = None
    unit: Optional[str] = None
    updateVersion: Optional[str] = None
    useTemplate: Optional[bool] = None
    userCodes: Optional[List[UserCodeDto]] = None
    userDescription: Optional[str] = None
    username: Optional[str] = None
    wakeUpTime: Optional[float] = None
    zwaveCompany: Optional[str] = None
    zwaveInfo: Optional[str] = None
    zwaveScheduleClimatePanelCompatibileBlocks: Optional[List[Dict[str, Any]]] = None
    zwaveVersion: Optional[str] = None
    value: Optional[Dict[str, Any]] = None
    viewLayout: Optional[Dict[str, Any]] = None
    volume: Optional[int] = None
    mainFunction: Optional[str] = None
    uiCallbacks: Optional[List[Dict[str, Any]]] = None
    quickAppVariables: Optional[List[Dict[str, Any]]] = None
    colorComponents: Optional[Dict[str, Any]] = None
    walliOperatingMode: Optional[str] = None
    ringUpperColor: Optional[str] = None
    ringBottomColor: Optional[str] = None
    ringBrightness: Optional[float] = None
    ringLightMode: Optional[str] = None
    ringConfirmingTime: Optional[float] = None
    encrypted: Optional[bool] = None
    useUiView: Optional[bool] = None
    uiView: Optional[Dict[str, Any]] = None
    Humidity: Optional[float] = None
    Pressure: Optional[float] = None
    Temperature: Optional[float] = None
    Wind: Optional[float] = None
    ConditionCode: Optional[float] = None
    WeatherCondition: Optional[str] = None


class DeviceActionArgumentsDto(BaseModel):
    args: Optional[List[Dict[str, Any]]] = None
    delay: Optional[float] = None  # Now truly optional
    integrationPin: Optional[str] = None  # Now truly optional


class ResourceTypeDto(BaseModel):
    name: str
    type_: float = Field(..., alias="type")
    scales: List[float]
    rateType: Optional[float] = None


class DeviceInputToChannelMapDto(BaseModel):
    close: Optional[List[float]] = None
    open: Optional[List[float]] = None
    partialOpen1: Optional[List[float]] = None
    step: Optional[List[float]] = None
    stop: Optional[List[float]] = None
    toggleCh1: Optional[List[float]] = None
    toggleCh2: Optional[List[float]] = None
    turnOffCh1: Optional[List[float]] = None
    turnOffCh2: Optional[List[float]] = None
    turnOnCh1: Optional[List[float]] = None
    turnOnCh2: Optional[List[float]] = None
    unsupported: Optional[List[float]] = None


class PluginCreateDto(BaseModel):
    name: str = Field(..., description="Name of device to be created")
    type_: str = Field(
        ..., alias="type", description="Plugin device type to be created"
    )
    roomID: Optional[int] = Field(
        ...,
        description="Room ID to which device will be added; default room when not given",
    )
    properties: Optional[DevicePropertiesDto] = None


class DeviceDto(BaseModel):
    actions: Optional[Dict[str, Any]] = None
    baseType: Optional[str] = None
    configXml: Optional[bool] = None
    created: Optional[int] = None
    enabled: Optional[bool] = None
    hasUIView: Optional[bool] = None
    id: Optional[int] = None
    interfaces: Optional[List[str]] = None
    isPlugin: Optional[bool] = None
    modified: Optional[int] = None
    name: Optional[str] = None
    parentId: Optional[float] = None
    properties: Optional[DevicePropertiesDto] = None
    roomID: Optional[int] = None
    sortOrder: Optional[int] = None
    type_: Optional[str] = Field(None, alias="type")
    viewXml: Optional[bool] = None
    view: Optional[List[ViewConfig]] = None
    visible: Optional[bool] = None


class DeviceInfoDto(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    classification: Optional[DeviceClassificationDto] = None
    roomId: Optional[int] = None
    type_: Optional[str] = Field(None, alias="type")
    properties: Optional[List[DeviceInfoPropertyDto]] = None
    role: Optional[str] = None
    actions: Optional[List[DeviceInfoPropertyDto]] = None
    events: Optional[List[Dict[str, Any]]] = None


class DeviceClassificationDto(BaseModel):
    pass


class DeviceInfoPropertyDto(BaseModel):
    name: Optional[Dict[str, Any]] = None
    type_: Optional[str] = Field(None, alias="type")
    conditionType: Optional[List[Dict[str, Any]]] = None
    operator: Optional[str] = None
    picker: Optional[str] = None
    label: Optional[str] = None
    unitPath: Optional[str] = None
    unit: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    args: Optional[List[DeviceInfoPropertyDto]] = None
    enumValues: Optional[DeviceInfoPropertyEnumValuesDto] = None
    valueMapping: Optional[List[ValueMappingDto]] = None
    isUIAction: Optional[bool] = None
    definedValues: Optional[List[DeviceInfoPropertyDefinedValue]] = None
    description: Optional[str] = None
    colorComponents: Optional[DeviceInfoPropertyColorComponents] = None


class DeviceInfoPropertyEnumValuesDto(BaseModel):
    items: Optional[List[Dict[str, Any]]] = None
    type_: Optional[str] = Field(None, alias="type")
    key: Optional[str] = None


class ValueMappingDto(BaseModel):
    value: bool
    label: str


class DeviceFirmwareUpdateDto(BaseModel):
    info: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    updateVersion: Optional[str] = None


class GroupActionArguments(BaseModel):
    args: Optional[List[Dict[str, Any]]] = Field(
        ..., description="Action arguments if needed"
    )
    filters: Optional[List[Dict[str, Any]]] = Field(
        ..., description="Filters definitions for devices"
    )
    integrationPin: Optional[str] = Field(..., description="Cloud integration pin")


class CentralScene(BaseModel):
    keyAttributes: Optional[List[KeyAttribute]] = None
    keyId: Optional[float] = None


class KeyAttribute(BaseModel):
    pass


class NewDevice(BaseModel):
    name: Optional[str] = None
    properties: Optional[DevicePropertiesDto] = None
    type_: Optional[str] = Field(None, alias="type")


class DevicePropertiesDto_parameters(BaseModel):
    lastReportedValue: Optional[float] = None
    size: Optional[float] = None
    lastSetValue: Optional[float] = None
    id: Optional[float] = None
    value: Optional[float] = None
    readyOnly: Optional[bool] = None
    setDefault: Optional[bool] = None


class UserCodeDto(BaseModel):
    id: Optional[float] = None
    name: Optional[str] = None
    status: Optional[str] = None
    update: Optional[str] = None


class ViewConfig(BaseModel):
    type_: str = Field(..., alias="type")
    assetsPath: Optional[str] = None
    translatesPath: Optional[str] = None
    name: Optional[str] = None


class FavoritePositions(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    value: Optional[float] = None
    slatsAngle: Optional[float] = None


class AvailablePosition(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None


class DeviceRole(BaseModel):
    pass


class DeviceTypeHierarchy(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    children: Optional[List[Dict[str, Any]]] = Field(
        ..., description="Items are of type DeviceTypeHierarchy"
    )


class DeviceInfoPropertyDefinedValue(BaseModel):
    unit: Optional[str] = None
    values: Optional[List[Dict[str, Any]]] = None


class DeviceInfoPropertyDefinedColorComponent(BaseModel):
    brightness: Optional[float] = None
    color: Optional[str] = None
    colorComponents: Optional[Dict[str, Any]] = None
    label: Optional[str] = None


class DeviceInfoPropertyColorComponents(BaseModel):
    blue: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    green: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    red: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    warmWhite: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    coldWhite: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    amber: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    cyan: Optional[DeviceInfoPropertyColorComponentsComponent] = None
    purple: Optional[DeviceInfoPropertyColorComponentsComponent] = None


class DeviceInfoPropertyColorComponentsComponent(BaseModel):
    label: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None


class ViewVersionEnum(BaseModel):
    pass


class DevicesDto(BaseModel):
    pass


class SystemStatusDto(BaseModel):
    description: Optional[str] = None
    os: Optional[str] = None
    stage: Optional[SystemStatusStageDto] = None
    current: Optional[int] = None
    done: Optional[bool] = None
    max: Optional[int] = None
    status: Optional[str] = None
    title: Optional[str] = None
    update: Optional[SystemStatusUpdateDto] = None
    platform: Optional[str] = None
    oemId: Optional[str] = None


class SystemStatusStageDto(BaseModel):
    description: Optional[str] = None
    current: Optional[int] = None
    done: Optional[bool] = None
    max: Optional[int] = None


class SystemStatusUpdateDto(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    version: Optional[str] = None


class SystemStatusAction(BaseModel):
    pass


class HomeDto(BaseModel):
    timestamp: Optional[float] = None
    defaultSensors: Optional[HomeDto_defaultSensors] = None
    meters: Optional[HomeDto_meters] = None
    notificationClient: Optional[HomeDto_notificationClient] = None
    hcName: Optional[str] = None
    weatherProvider: Optional[float] = None
    currency: Optional[str] = None
    fireAlarmTemperature: Optional[float] = None
    freezeAlarmTemperature: Optional[float] = None
    timeFormat: Optional[float] = None
    dateFormat: Optional[str] = None
    firstRunAfterUpdate: Optional[bool] = None


class HomeDto_defaultSensors(BaseModel):
    light: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None


class HomeDto_meters(BaseModel):
    energy: Optional[List[float]] = None


class HomeDto_notificationClient(BaseModel):
    marketingNotificationAllowed: Optional[bool] = None


class UserActivityDto(BaseModel):
    email: Optional[str] = None
    lastActivity: Optional[int] = None
    type_: Optional[str] = Field(None, alias="type")
    user: Optional[str] = None
    userId: Optional[int] = None


class LoginStatus(BaseModel):
    status: Optional[bool] = None
    type_: Optional[str] = Field(None, alias="type")
    userID: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    analyticsUserIdHash: Optional[str] = None
    skin: Optional[str] = None
    skinSetting: Optional[str] = None
    isAddTileVisible: Optional[bool] = None
    buiSettings: Optional[Dict[str, Any]] = None
    rights: Optional[UserDtoRights] = None


class LogoutStatus(BaseModel):
    status: Optional[bool] = None
    retryNumber: Optional[int] = None
    limit: Optional[int] = None
    timeLeft: Optional[int] = None


class PluginViewDto(BaseModel):
    field__jason: Optional[Dict[str, Any]] = Field(None, alias="$jason")


class PluginBodyDto(BaseModel):
    sections: Optional[PluginSectionsDto] = None
    header: Optional[PluginHeaderDto] = None


class PluginHeaderDto(BaseModel):
    title: Optional[str] = Field(..., description="Page title")
    style: Optional[Dict[str, Any]] = None


class PluginSectionsDto(BaseModel):
    items: Optional[List[Dict[str, Any]]] = None


class PluginButtonDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    text: Optional[str] = Field(
        ..., description="The Text displayed as the content of the button"
    )
    visible: Optional[bool] = None
    type_: Optional[str] = Field(None, alias="type")
    style: Optional[Dict[str, Any]] = None
    image: Optional[str] = Field(..., description="Button image")
    classes: Optional[List[str]] = None
    eventBinding: Optional[Dict[str, Any]] = None


class PluginHorizontalLayoutDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    components: Optional[List[Dict[str, Any]]] = None
    style: Optional[Dict[str, Any]] = None


class PluginImageDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    url: Optional[str] = Field(..., description="Path to image")
    style: Optional[Dict[str, Any]] = None


class PluginLabelDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    text: Optional[str] = Field(
        ..., description="The text to be displayed inside of the label."
    )
    style: Optional[Dict[str, Any]] = None


class PluginMultiSelectDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    text: Optional[str] = Field(
        ..., description="The text to be displayed next to component."
    )
    selectionType: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    options: Optional[List[PluginOptionDto]] = None
    values: Optional[List[str]] = None


class PluginOptionDto(BaseModel):
    value: Optional[str] = Field(..., description="Option value.")
    type_: Optional[str] = Field(None, alias="type")
    text: Optional[str] = Field(..., description="The text to be displayed.")


class PluginSingleSelectDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    text: Optional[str] = Field(
        ..., description="The text to be displayed next to component."
    )
    selectionType: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    options: Optional[List[PluginOptionDto]] = None
    values: Optional[List[str]] = None


class PluginSliderDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    max: Optional[str] = Field(..., description="The maximum selectable value.")
    min: Optional[str] = Field(..., description="The minimum selectable value.")
    step: Optional[str] = Field(..., description="The step between values.")
    value: Optional[str] = Field(..., description="The chosen value.")
    style: Optional[Dict[str, Any]] = None


class PluginSpaceDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    style: Optional[Dict[str, Any]] = None


class PluginSwitchDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    value: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class PluginVerticalLayoutDto(BaseModel):
    name: Optional[str] = Field(..., description="Component name")
    type_: Optional[str] = Field(None, alias="type")
    components: Optional[List[Dict[str, Any]]] = None
    style: Optional[Dict[str, Any]] = None


class PluginsTypesDto(BaseModel):
    installed: Optional[InstalledPluginsDto] = None
    all: Optional[Dict[str, Any]] = None
    promo: Optional[List[Dict[str, Any]]] = None


class PluginUpdateDto(BaseModel):
    deviceId: int
    componentName: str
    propertyName: str
    newValue: Union[str, int, float, bool, Dict[str, Any], List[Any]]


class PluginsV2Dto(BaseModel):
    pass


class PluginV2ElementDto(BaseModel):
    compatibility: Optional[List[str]] = None
    defaultMainDeviceName: Optional[str] = None
    description: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    url: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[IconDto] = None


class IconDto(BaseModel):
    path: Optional[str] = None


class PluginsDto(BaseModel):
    installed: Optional[List[InstalledPluginElementDto]] = None
    all: Optional[AllPluginsDto] = None
    promo: Optional[List[PluginsPromoElementDto]] = None


class IPCameraDto(BaseModel):
    id: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None


class InstalledPluginsDto(BaseModel):
    pass


class InstalledPluginElementDto(BaseModel):
    name: Optional[str] = Field(..., description="Installed plugin name")
    predefined: Optional[bool] = Field(
        ..., description="Describes whether the plugin is predefined in the system."
    )


class AllPluginsDto(BaseModel):
    types: Optional[List[PluginByCategoryDto]] = None


class PluginByCategoryDto(BaseModel):
    category: Optional[float] = None
    plugins: Optional[List[PluginDto]] = None
    installed: Optional[float] = None


class PluginDto(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    name: Optional[str] = None
    defaultMainDeviceName: Optional[str] = None
    description: Optional[str] = None
    user: Optional[str] = None
    compatibility: Optional[List[str]] = None
    predefined: Optional[bool] = None
    version: Optional[str] = None
    url: Optional[str] = None
    installed: Optional[bool] = None


class PluginsPromoDto(BaseModel):
    pass


class PluginsPromoElementDto(BaseModel):
    image: Optional[PluginsPromoElementImageDto] = None
    predefined: Optional[str] = None


class PluginsPromoElementImageDto(BaseModel):
    big: Optional[str] = None
    small: Optional[str] = None


class UiEventType(BaseModel):
    pass


class CreateChildDeviceDto(BaseModel):
    parentId: int = Field(..., description="Parent id")
    type_: str = Field(..., alias="type", description="Type")
    name: str = Field(..., description="Name")
    initialProperties: Optional[Dict[str, Any]] = Field(
        ..., description="Initial properties"
    )
    initialInterfaces: Optional[List[str]] = None


class UpdatePropertyDto(BaseModel):
    deviceId: int
    propertyName: str
    value: Optional[Dict[str, Any]] = None


class ZwaveNodeRemovedEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    data: Dict[str, Any]


class CentralSceneEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    source: int = Field(..., description="Device id")
    data: Dict[str, Any]


class DeviceFirmwareUpdateEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    source: int = Field(..., description="Device id")
    data: Dict[str, Any]


class SceneActivationEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    source: int = Field(..., description="Device id")
    data: Dict[str, Any]


class ZwaveNetworkResetEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")


class AccessControlEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    source: int = Field(..., description="Device id")
    data: Dict[str, Any]


class VideoGateIncomingCallEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    data: Dict[str, Any]


class ZwaveDeviceParametersChangedEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    source: int = Field(..., description="Device id")


class GeofenceEventDto(BaseModel):
    type_: str = Field(..., alias="type", description="Type")
    userId: int = Field(..., description="User id")
    deviceId: int = Field(..., description="Device id")
    locationId: int = Field(..., description="Location id")
    geofenceAction: str = Field(..., description="Geofence action")
    timestamp: int = Field(..., description="timestamp")


class PluginsInterfaceParamDto(BaseModel):
    action: str = Field(..., description="Action")
    deviceId: int = Field(..., description="Device id")
    interfaces: List[str] = Field(..., description="Interfaces to add or remove")


class RestartPluginRequestDto(BaseModel):
    deviceId: int = Field(..., description="Device id")


class RestartPluginResponseDto(BaseModel):
    status: bool = Field(..., description="Request status")


class LocationSettingsDate(BaseModel):
    """Current date on your device"""

    day: Optional[int] = Field(..., description="Day")
    month: Optional[int] = Field(..., description="Month")
    year: Optional[int] = Field(..., description="Year")


class LocationSettingsTime(BaseModel):
    """Current time on your device"""

    hour: Optional[int] = Field(..., description="Hour, format depends on timeFormat")
    minute: Optional[int] = Field(..., description="Minute, format mm")


class LocationSettings(BaseModel):
    houseNumber: Optional[int] = Field(..., description="Your location house number")
    timezone: Optional[str] = Field(..., description="Your location time zone")
    timezoneOffset: Optional[int] = Field(
        ...,
        description="Time zone difference, in minutes, from current locale (host system settings) to UTC",
    )
    ntp: Optional[bool] = Field(..., description="Is NTP enabled")
    ntpServer: Optional[str] = Field(
        ..., description="Network Time Protocol Server address"
    )
    date: Optional[LocationSettingsDate] = None
    time: Optional[LocationSettingsTime] = None
    longitude: Optional[float] = Field(
        ..., description="The longitude of the location in EPSG:4326 coordinate system"
    )
    latitude: Optional[float] = Field(
        ..., description="The latitude of the location in EPSG:4326 coordinate system"
    )
    city: Optional[str] = Field(..., description="City")
    temperatureUnit: Optional[str] = Field(
        ..., description="Temperature Unit: Celsius (C) or Fahrenheit(F)"
    )
    windUnit: Optional[str] = Field(..., description="Wind unit")
    timeFormat: Optional[int] = Field(..., description="Time format: 12 or 24")
    dateFormat: Optional[str] = Field(..., description="Date format")
    decimalMark: Optional[str] = Field(..., description="Decimal mark")


class LedDto(BaseModel):
    brightness: Optional[int] = None


class interfaces(BaseModel):
    interfaces: Optional[List[str]] = None


class ipConfig(BaseModel):
    ipMode: str
    ip: Optional[str] = None
    mask: Optional[str] = None
    gateway: Optional[str] = None
    dns1: Optional[str] = None
    dns2: Optional[str] = None
    macAddress: Optional[str] = None


class apConfig(BaseModel):
    ssid: str
    security: str
    password: Optional[str] = None
    fallback: Optional[bool] = None
    hidden: Optional[bool] = None
    signal: Optional[int] = None
    bssid: Optional[str] = None
    frequency: Optional[int] = None


class interfaceConfiguration(BaseModel):
    enabled: bool
    ipConfig: Optional[ipConfig] = None
    apConfig: Optional[apConfig] = None


class configN(BaseModel):
    pass


class networkConfiguration(BaseModel):
    networkConfig: Optional[configN] = None


class ap(BaseModel):
    ssid: str
    signal: Optional[int] = None
    security: List[str]


class apInfo(BaseModel):
    ssid: str
    bssid: Optional[str] = None
    frequency: Optional[int] = None
    signal: Optional[int] = None
    apMode: Optional[str] = None
    security: List[str]


class apList(BaseModel):
    apList: Optional[List[ap]] = None


class apListInfo(BaseModel):
    apListInfo: Optional[List[apInfo]] = None


class accessPointMode(BaseModel):
    accessPointEnabled: Optional[bool] = None


class protocols(BaseModel):
    http: bool
    https: bool


class internetConnectivity(BaseModel):
    internetConnectivity: bool


class connections(BaseModel):
    pass


class connection(BaseModel):
    uuid: Optional[str] = None
    name: str
    enabled: bool
    status: Optional[str] = None
    apConfig: Optional[apConfig] = None
    ipConfig: Optional[ipConfig] = None


class statusResponse(BaseModel):
    code: int
    message: str


class radioConfiguration(BaseModel):
    enabled: bool


class radioListConfiguration(BaseModel):
    pass


class remoteAccessState(BaseModel):
    active: bool
    deadline: Optional[int] = None
    supportUser: Optional[bool] = None


class remoteAccessStatus(BaseModel):
    user: Optional[remoteAccessState] = None
    support: Optional[remoteAccessState] = None


class Settings(BaseModel):
    pass


class CurrentVersion(BaseModel):
    version: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")


class InstallVersion(BaseModel):
    version: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")
    status: Optional[str] = None
    progress: Optional[int] = None


class Info(BaseModel):
    serialNumber: Optional[str] = None
    platform: Optional[str] = None
    zwaveEngineVersion: Optional[ZwaveEngineVersion] = None
    zigbeeStatus: Optional[bool] = None
    hcName: Optional[str] = None
    mac: Optional[str] = None
    zwaveVersion: Optional[str] = None
    timeFormat: Optional[int] = None
    dateFormat: Optional[str] = None
    timezoneOffset: Optional[int] = None
    decimalMark: Optional[str] = None
    zwaveRegion: Optional[ZwaveRegion] = None
    serverStatus: Optional[int] = None
    defaultLanguage: Optional[str] = None
    defaultRoomId: Optional[int] = None
    sunsetHour: Optional[str] = None
    sunriseHour: Optional[str] = None
    hotelMode: Optional[bool] = None
    temperatureUnit: Optional[str] = None
    batteryLowNotification: Optional[bool] = None
    date: Optional[str] = None
    currency: Optional[str] = None
    softVersion: Optional[str] = None
    beta: Optional[bool] = None
    currentVersion: Optional[CurrentVersion] = None
    installVersion: Optional[InstallVersion] = None
    timestamp: Optional[int] = None
    online: Optional[bool] = None
    updateStableAvailable: Optional[bool] = None
    updateBetaAvailable: Optional[bool] = None
    newestStableVersion: Optional[str] = None
    newestBetaVersion: Optional[str] = None
    isFTIConfigured: Optional[bool] = None
    skin: Optional[str] = None
    skinSetting: Optional[str] = None
    isSlave: Optional[bool] = None
    oemId: Optional[OemId] = None


class ZwaveEngineVersion(BaseModel):
    pass


class ZwaveRegion(BaseModel):
    pass


class OemId(BaseModel):
    pass


class AlarmHistoryEntryDto(BaseModel):
    type_: Optional[str] = Field(..., alias="type", description="Event type.")
    partitionId: Optional[float] = Field(
        ..., description="Partition id which generated the entry."
    )
    userId: Optional[float] = Field(
        ...,
        description="Field required for PartitionArmed and PartitionDisarmed types. Does not occur in PartitionBreached.",
    )
    deviceId: Optional[float] = Field(
        ...,
        description="Field required for PartitionBreached type. Does not occur in PartitionArmed and PartitionDisarmed.",
    )
    timestamp: Optional[float] = Field(..., description="Creation time.")


class NewPartitionDto(BaseModel):
    name: str
    armDelay: int
    breachDelay: int
    devices: List[int]


class AlarmPartitionDto(BaseModel):
    id: int
    name: str
    armed: bool
    breached: bool
    armDelay: float
    breachDelay: float
    devices: List[int]
    secondsToArm: Optional[int] = None
    lastActionAt: Optional[int] = None


class PartitionArmTryResult(BaseModel):
    id: int
    result: PartitionArmState
    armTime: Optional[int] = None
    breachedDevices: Optional[List[int]] = None


class PartitionArmState(BaseModel):
    pass


class inline_response_201(BaseModel):
    id: Optional[int] = None


class AlarmDeviceEntryDto(BaseModel):
    id: Optional[float] = None
    name: Optional[str] = None


class HumiditySetpoint(BaseModel):
    hour: Optional[int] = None
    minute: Optional[int] = None
    humidity: Optional[float] = None


class HumidityScheduleDay(BaseModel):
    day: Optional[HumiditySetpoint] = None
    evening: Optional[HumiditySetpoint] = None
    morning: Optional[HumiditySetpoint] = None
    night: Optional[HumiditySetpoint] = None


class HumidityScheduleWeek(BaseModel):
    currentHumidity: Optional[float] = None
    handHumidity: Optional[float] = None
    handTimestamp: Optional[int] = None
    vacationHumidity: Optional[float] = None
    rooms: Optional[List[int]] = None
    monday: Optional[HumidityScheduleDay] = None
    tuesday: Optional[HumidityScheduleDay] = None
    wednesday: Optional[HumidityScheduleDay] = None
    thursday: Optional[HumidityScheduleDay] = None
    friday: Optional[HumidityScheduleDay] = None
    saturday: Optional[HumidityScheduleDay] = None
    sunday: Optional[HumidityScheduleDay] = None


class HumidityZone(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    properties: Optional[HumidityScheduleWeek] = None


class inline_object(BaseModel):
    name: Optional[str] = None


class Location(BaseModel):
    id: Optional[int] = Field(..., description="Location Id")
    name: str = Field(..., description="Location name")
    address: Optional[str] = Field(..., description="Location addres")
    longitude: Optional[float] = Field(
        ..., description="The longitude of the location in EPSG:4326 coordinate system"
    )
    latitude: Optional[float] = Field(
        ..., description="The latitude of the location in EPSG:4326 coordinate system"
    )
    radius: Optional[int] = Field(..., description="Map radius in meters")
    home: Optional[bool] = Field(
        ...,
        description="Location type. If 'true': Home location, if 'false': Other location. There can be only one Home Location",
    )
    created: Optional[int] = Field(
        ..., description="Timestamp: Date and time of creation"
    )
    modified: Optional[int] = Field(
        ..., description="Timestamp: Date and time of last modification"
    )


class LocationRequest(BaseModel):
    name: str = Field(..., description="Location name")
    address: Optional[str] = Field(..., description="Location addres")
    longitude: Optional[float] = Field(
        ..., description="The longitude of the location in EPSG:4326 coordinate system"
    )
    latitude: Optional[float] = Field(
        ..., description="The latitude of the location in EPSG:4326 coordinate system"
    )
    radius: Optional[int] = Field(..., description="Map radius in meters")


class Day(BaseModel):
    pass


class sprinklers_DayEnum(BaseModel):
    pass


class SprinklerZone(BaseModel):
    deviceId: Optional[int] = None
    duration: Optional[int] = Field(..., description="seconds")


class SprinklerSequenceRequest(BaseModel):
    startTime: Optional[int] = Field(..., description="seconds from midnight")
    sprinklers: Optional[List[SprinklerZone]] = None


class SprinklerSequence(BaseModel):
    id: Optional[int] = None
    isRunning: Optional[bool] = None
    startTime: Optional[int] = Field(..., description="seconds from midnight")
    sprinklers: Optional[List[SprinklerZone]] = None


class SprinklerSequenceStartWateringRequest(BaseModel):
    wateringTime: Optional[int] = None


class SprinklerSchedule(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    isActive: Optional[bool] = None
    days: Optional[Day] = None
    sequences: Optional[List[SprinklerSequence]] = None


class SprinklerScheduleCreateRequest(BaseModel):
    name: Optional[str] = None


class SprinklerScheduleRequest(BaseModel):
    name: Optional[str] = None
    days: Optional[Day] = None
    sequences: Optional[List[SprinklerSequenceRequest]] = None
    isActive: Optional[bool] = None


class FamilyLocation(BaseModel):
    timestamp: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Notifications(BaseModel):
    pass


class Notification(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sms: Optional[str] = None
    email: Optional[str] = None
    push: Optional[str] = None
    created: Optional[int] = None
    modified: Optional[int] = None


class notifications_inline_object(BaseModel):
    name: Optional[str] = None


class CustomEventDto(BaseModel):
    name: Optional[str] = None
    userDescription: Optional[str] = None


class GlobalVariableDto(BaseModel):
    enumValues: Optional[List[str]] = None
    isEnum: Optional[bool] = None
    name: Optional[str] = None
    readOnly: Optional[bool] = None
    value: Optional[str] = None


class PanelMode(BaseModel):
    pass


class CalculationStrategy(BaseModel):
    pass


class Mode(BaseModel):
    pass


class ClimateSetpoint(BaseModel):
    """Temperature settings for period of time"""

    hour: Optional[int] = None
    minute: Optional[int] = None
    temperatureHeating: Optional[float] = None
    temperatureCooling: Optional[float] = None


class ClimateScheduleDay(BaseModel):
    """Periods of time during the day"""

    morning: Optional[ClimateSetpoint] = None
    day: Optional[ClimateSetpoint] = None
    evening: Optional[ClimateSetpoint] = None
    night: Optional[ClimateSetpoint] = None


class BasicProperties(BaseModel):
    mode: Optional[Mode] = None
    handSetPointHeating: Optional[float] = Field(
        ..., description="Heating temperature for manual mode"
    )
    handSetPointCooling: Optional[float] = Field(
        ..., description="Cooling temperature for manual mode"
    )
    handTimestamp: Optional[int] = Field(
        ..., description="End date and time for manual mode (timestamp)"
    )
    handMode: Optional[Mode] = None
    vacationSetPointHeating: Optional[float] = Field(
        ..., description="Heating temperature for vacation mode"
    )
    vacationSetPointCooling: Optional[float] = Field(
        ..., description="Cooling temperature for vacation mode"
    )
    vacationMode: Optional[Mode] = None
    vacationStartTime: Optional[float] = Field(
        ..., description="Start date and time for vacation mode (timestamp)"
    )
    vacationEndTime: Optional[float] = Field(
        ..., description="End date and time for vacation mode (timestamp)"
    )
    currentTemperature: Optional[float] = Field(
        ..., description="Current temperature settings"
    )
    currentTemperatureHeating: Optional[float] = Field(
        ..., description="Current temperature settings for heating"
    )
    currentTemperatureCooling: Optional[float] = Field(
        ..., description="Current temperature settings for cooling"
    )
    currentSetpointTimeStartHour: Optional[float] = Field(
        ..., description="Current hour of range start"
    )
    currentSetpointTimeStartMinute: Optional[float] = Field(
        ..., description="Current minute of range start"
    )
    currentSetpointTimeEndHour: Optional[float] = Field(
        ..., description="Current hour of range end"
    )
    currentSetpointTimeEndMinute: Optional[float] = Field(
        ..., description="Current minute of range end"
    )


class AdvancedProperties(BaseModel):
    mode: Optional[Mode] = None
    monday: Optional[ClimateScheduleDay] = None
    tuesday: Optional[ClimateScheduleDay] = None
    wednesday: Optional[ClimateScheduleDay] = None
    thursday: Optional[ClimateScheduleDay] = None
    friday: Optional[ClimateScheduleDay] = None
    saturday: Optional[ClimateScheduleDay] = None
    sunday: Optional[ClimateScheduleDay] = None
    handSetPointHeating: Optional[float] = Field(
        ..., description="Heating temperature for manual mode"
    )
    handSetPointCooling: Optional[float] = Field(
        ..., description="Cooling temperature for manual mode"
    )
    handTimestamp: Optional[int] = Field(
        ..., description="End date and time for manual mode (timestamp)"
    )
    handMode: Optional[Mode] = None
    vacationSetPointHeating: Optional[float] = Field(
        ..., description="Heating temperature for vacation mode"
    )
    vacationSetPointCooling: Optional[float] = Field(
        ..., description="Cooling temperature for vacation mode"
    )
    vacationMode: Optional[Mode] = None
    vacationStartTime: Optional[float] = Field(
        ..., description="Start date and time for vacation mode (timestamp)"
    )
    vacationEndTime: Optional[float] = Field(
        ..., description="End date and time for vacation mode (timestamp)"
    )
    currentTemperatureHeating: Optional[float] = Field(
        ..., description="Current temperature settings for heating"
    )
    currentTemperatureCooling: Optional[float] = Field(
        ..., description="Current temperature settings for cooling"
    )
    currentSetpointTimeStartHour: Optional[float] = Field(
        ..., description="Current hour of range start"
    )
    currentSetpointTimeStartMinute: Optional[float] = Field(
        ..., description="Current minute of range start"
    )
    currentSetpointTimeEndHour: Optional[float] = Field(
        ..., description="Current hour of range end"
    )
    currentSetpointTimeEndMinute: Optional[float] = Field(
        ..., description="Current minute of range end"
    )
    devices: Optional[List[int]] = None
    incompatibleDevices: Optional[List[int]] = None
    temperatureSensors: Optional[List[int]] = Field(
        ...,
        description="List of temperature sensors that will be used in calculatig currentTemperature",
    )
    calculationStrategy: Optional[CalculationStrategy] = None
    currentTemperature: Optional[float] = Field(
        ..., description="Current calculated temperature in climate zone"
    )


class BasicClimateZone(BaseModel):
    id: Optional[int] = Field(..., description="Climate zone id")
    name: Optional[str] = Field(..., description="Climate zone name")
    active: Optional[bool] = Field(..., description="Is climate zone active")
    mode: Optional[PanelMode] = None
    properties: Optional[BasicProperties] = None


class AdvancedClimateZone(BaseModel):
    id: Optional[int] = Field(..., description="Climate zone id")
    name: Optional[str] = Field(..., description="Climate zone name")
    active: Optional[bool] = Field(..., description="Is climate zone active")
    mode: Optional[PanelMode] = None
    created: Optional[int] = Field(
        ..., description="Timestamp: Date and time of creation"
    )
    modified: Optional[int] = Field(
        ..., description="Timestamp: Date and time of modification"
    )
    properties: Optional[AdvancedProperties] = None


class CreatePushRequest(BaseModel):
    mobileDevices: List[int] = Field(..., description="List of push receivers.")
    title: str = Field(..., description="Push title.")
    message: str = Field(..., description="Push message")
    category: str = Field(..., description="Push category")
    service: Optional[str] = Field(..., description="Service where action will be run.")
    action: Optional[str] = Field(
        ...,
        description="Action which will be run on the service. Value depends on service value.",
    )
    data: Dict[str, Any] = Field(..., description="Push data.")


class FactoryResetRequestBody(BaseModel):
    ticket: Optional[str] = Field(..., description="RA ticket")
    deleteBackups: Optional[bool] = Field(
        ..., description="Flag indicating whether stored backups should be removed"
    )
    detachFibaroId: Optional[bool] = Field(
        ...,
        description="Flag indicating whether HC should be detached from cloud account",
    )


class SourceType(BaseModel):
    pass


class EventDto(BaseModel):
    id: Optional[int] = None
    sourceType: Optional[SourceType] = None
    sourceId: Optional[int] = None
    timestamp: Optional[int] = None
    type_: Optional[str] = Field(None, alias="type")
    data: Optional[Dict[str, Any]] = None
    objects: Optional[List[Dict[str, Any]]] = None


# Note: The add_extra_blank_lines_between_classes function was moved to the generator script
# to avoid self-modification at import time which breaks installed packages.
