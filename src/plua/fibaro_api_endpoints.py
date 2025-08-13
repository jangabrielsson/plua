"""
Fibaro HC3 API Emulation Server with Full Type Safety
Auto-generated from Swagger/OpenAPI specifications with Pydantic models.
Delegates all requests to Lua via simplified (method, path, data) pattern.
"""

# flake8: noqa

from fastapi import FastAPI, Query, Body, Request
from typing import Optional, Dict, Any
import logging
import json

# Import all models from the separate models file
from .fibaro_api_models import *

logger = logging.getLogger(__name__)

# This will be set by the main module
interpreter = None


def set_interpreter(lua_interpreter):
    """Set the Lua interpreter instance."""
    global interpreter
    interpreter = lua_interpreter


# Helper function to handle all requests
async def handle_request(request: Request, method: str, body_data: Any = None):
    """Common handler for all API requests"""
    full_path = str(request.url.path)
    if request.url.query:
        full_path += f"?{request.url.query}"

    # Convert body data to JSON string if present
    data = ""
    if body_data is not None:
        if hasattr(body_data, "dict"):
            data = json.dumps(body_data.dict())
        elif isinstance(body_data, dict):
            data = json.dumps(body_data)
        else:
            data = str(body_data)

    try:
        logger.debug(f"Calling fibaroApiHook with method={method}, path={full_path}, data={data}")
        result = interpreter.lua.globals()._PY.fibaroApiHook(method, full_path, data)
        logger.debug(f"fibaroApiHook returned: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in Fibaro API hook for {method} {full_path}: {e}")
        logger.error(f"Exception traceback:", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}


def create_fibaro_api_routes(app: FastAPI):
    """Create all typed Fibaro API routes."""

    # Check if we have an interpreter set
    if interpreter is None:
        raise RuntimeError("Interpreter not set. Call set_interpreter() first.")

    # Generated Fibaro API endpoints

    @app.get("/api/scenes", tags=["scenes"])
    async def getSceneList(
        request: Request,
        alexaProhibited: Optional[str] = Query(
            None, description="Scene list filtered by alexa prohibited"
        ),
    ):
        """
        Get a list of all available scenes


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/scenes", tags=["scenes"])
    async def createScene(
        request: Request, request_data: CreateSceneRequest = Body(...)
    ):
        """
        Create scene


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/scenes/hasTriggers", tags=["scenes"])
    async def filterScenesByTriggers(
        request: Request, request_data: FilterSceneRequest = Body(...)
    ):
        """
        Filter scenes by triggers


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/scenes/{sceneID}", tags=["scenes"])
    async def getScene(
        request: Request,
        sceneID: int,
        alexaProhibited: Optional[str] = Query(
            None, description="Get scene by alexaProhibited"
        ),
    ):
        """
        Get scene object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/scenes/{sceneID}", tags=["scenes"])
    async def modifyScene(
        request: Request, sceneID: int, request_data: UpdateSceneRequest = Body(...)
    ):
        """
        Modify scene


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/scenes/{sceneID}", tags=["scenes"])
    async def deleteScene(request: Request, sceneID: int):
        """
        Delete scene


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/scenes/{sceneID}/execute", tags=["scenes"])
    async def executeSceneByGet(
        request: Request,
        sceneID: int,
        pin: Optional[str] = Query(None, description="PIN"),
    ):
        """
        Executes asynchronously executive part of the scene neglecting conditional part.


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/scenes/{sceneID}/execute", tags=["scenes"])
    async def executeScene(
        request: Request, sceneID: int, request_data: ExecuteSceneRequest = Body(...)
    ):
        """
        Executes asynchronously executive part of the scene neglecting conditional part.


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/scenes/{sceneID}/executeSync", tags=["scenes"])
    async def executeSceneSyncByGet(
        request: Request,
        sceneID: int,
        pin: Optional[str] = Query(None, description="PIN"),
    ):
        """
        Executes synchronously executive part of the scene neglecting conditional part.


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/scenes/{sceneID}/executeSync", tags=["scenes"])
    async def executeSceneSync(
        request: Request, sceneID: int, request_data: ExecuteSceneRequest = Body(...)
    ):
        """
        Executes synchronously executive part of the scene neglecting conditional part.


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/scenes/{sceneID}/convert", tags=["scenes"])
    async def convertScene(request: Request, sceneID: int):
        """
        Convert block scene to lua.


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/scenes/{sceneID}/copy", tags=["scenes"])
    async def copyScene(request: Request, sceneID: int):
        """
        Create scene copy.


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/scenes/{sceneID}/copyAndConvert", tags=["scenes"])
    async def copyAndConvertScene(request: Request, sceneID: int):
        """
        Copy and convert block scene to lua.


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/scenes/{sceneID}/kill", tags=["scenes"])
    async def killSceneByGet(
        request: Request,
        sceneID: int,
        pin: Optional[str] = Query(None, description="PIN"),
    ):
        """
        Kill running scene.


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/scenes/{sceneID}/kill", tags=["scenes"])
    async def killScene(request: Request, sceneID: int):
        """
        Kill running scene.


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/icons", tags=["icons"])
    async def getIcons(
        request: Request,
        deviceType: Optional[str] = Query(
            None, description="Device type to filter icons"
        ),
    ):
        """
        Get a list of all available icons


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/icons", tags=["icons"])
    async def uploadIcon(request: Request, request_data: Dict[str, Any] = Body(...)):
        """
        Upload icon


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/icons", tags=["icons"])
    async def deleteIcon(
        request: Request,
        type_: str = Query(..., description="Icon type"),
        id: Optional[int] = Query(None, description="Icon Id"),
        name: Optional[str] = Query(None, description="Icon name"),
        fileExtension: Optional[str] = Query(None, description="File extension"),
    ):
        """
        Delete icon


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/sortOrder", tags=["sortOrder"])
    async def updateSortOrder(
        request: Request, request_data: SortOrderRequest = Body(...)
    ):
        """
        Update sort order


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/favoriteColors", tags=["favoriteColors"])
    async def getFavoriteColors(request: Request):
        """
        Get favorite colors


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/favoriteColors", tags=["favoriteColors"])
    async def newFavoriteColor(
        request: Request, request_data: NewFavoriteColor = Body(...)
    ):
        """
        Create favorite colors object


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put("/api/panels/favoriteColors/{favoriteColorID}", tags=["favoriteColors"])
    async def modifyFavoriteColor(
        request: Request, favoriteColorID: int, request_data: FavoriteColor = Body(...)
    ):
        """
        Modify favorite colors object


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/panels/favoriteColors/{favoriteColorID}", tags=["favoriteColors"])
    async def deleteFavoriteColor(request: Request, favoriteColorID: int):
        """
        Delete favorite colors


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/refreshStates", tags=["refreshStates"])
    async def refreshStates(
        request: Request,
        last: int = Query(..., description="Last refresh"),
        lang: str = Query(..., description="Language"),
        rand: str = Query(..., description="Random number"),
        logs: Optional[str] = Query(None, description="Return logs if true."),
    ):
        """
        Refresh sates


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/profiles", tags=["profiles"])
    async def getProfiles(
        request: Request,
        showHidden: Optional[str] = Query(
            None, description="Return all or visible actors."
        ),
    ):
        """
        Get all profiles and active profile


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/profiles", tags=["profiles"])
    async def updateProfiles(
        request: Request, request_data: ProfileServiceDto = Body(...)
    ):
        """
        Update profiles and set active profile


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/profiles", tags=["profiles"])
    async def createProfile(
        request: Request, request_data: ProfileCreateDto = Body(...)
    ):
        """
        Create new profile with provided name


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/profiles/{profileId}", tags=["profiles"])
    async def getProfileById(
        request: Request,
        profileId: int,
        showHidden: Optional[str] = Query(
            None, description="Return all or visible actors."
        ),
    ):
        """
        Get profile


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/profiles/{profileId}", tags=["profiles"])
    async def updateProfileById(
        request: Request, profileId: int, request_data: ProfileDto = Body(...)
    ):
        """
        Update existing profile


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/profiles/{profileId}", tags=["profiles"])
    async def removeProfileById(request: Request, profileId: int):
        """
        Remove existing profile


        """
        return await handle_request(request, "DELETE", None)

    @app.put("/api/profiles/{profileId}/partitions/{partitionId}", tags=["profiles"])
    async def updateProfilePartitionAction(
        request: Request,
        profileId: int,
        partitionId: int,
        request_data: PartitionActionUpdateDto = Body(...),
    ):
        """
        Update profile partition action


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put("/api/profiles/{profileId}/climateZones/{zoneId}", tags=["profiles"])
    async def updateProfileClimateZoneAction(
        request: Request,
        profileId: int,
        zoneId: int,
        request_data: ClimateZoneActionUpdateDto = Body(...),
    ):
        """
        Update profile climate zone action


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put("/api/profiles/{profileId}/scenes/{sceneId}", tags=["profiles"])
    async def updateProfileSceneActor(
        request: Request,
        profileId: int,
        sceneId: int,
        request_data: SceneActorUpdateDto = Body(...),
    ):
        """
        Update profile scene actor


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/profiles/reset", tags=["profiles"])
    async def resetProfiles(request: Request):
        """
        Rest profiles model to default value


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/profiles/activeProfile/{profileId}", tags=["profiles"])
    async def setActiveProfile(request: Request, profileId: int):
        """
        Set active profile


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/diagnostics", tags=["diagnostics"])
    async def getDiagnostics(request: Request):
        """
        Get diagnostics


        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/apps/com.fibaro.zwave/diagnostics/transmissions", tags=["diagnostics"]
    )
    async def get__apps_com_fibaro_zwave_diagnostics_transmissions(request: Request):
        """
        Returns information about zwave transmissions


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/users", tags=["users"])
    async def getUsers(
        request: Request,
        hasDeviceRights: Optional[str] = Query(
            None, description="Filter users by rights to given devices"
        ),
        hasSceneRights: Optional[str] = Query(
            None, description="Filter users by rights to given scenes"
        ),
    ):
        """
        Get a list of available users


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/users", tags=["users"])
    async def createUser(
        request: Request,
        isOffline: Optional[str] = Query(None, description="Is user created offline"),
        request_data: UserCreateRequest = Body(...),
    ):
        """
        Create User


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/users/{userID}", tags=["users"])
    async def getUser(request: Request, userID: int):
        """
        Get user object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/users/{userID}", tags=["users"])
    async def modifyUser(
        request: Request, userID: int, request_data: UserDto = Body(...)
    ):
        """
        Modify user


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/users/{userID}", tags=["users"])
    async def deleteUser(
        request: Request,
        userID: int,
        keepLocalUser: Optional[str] = Query(None, description="Keep Local User"),
    ):
        """
        Delete user


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/users/{userID}/raInvite", tags=["users"])
    async def inviteUser(request: Request, userID: int):
        """
        User invitation


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/users/action/changeAdmin/{newAdminId}", tags=["users"])
    async def transferAdminRoleInit(request: Request, newAdminId: int):
        """
        Initiates transfer of administrator role to {newAdminId}


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/users/action/confirmAdminTransfer", tags=["users"])
    async def transferAdminRoleConfirm(request: Request):
        """
        Confirms pending admin role transfer. Only user that is target for admin role may call this endpoint successfully


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/users/action/cancelAdminTransfer", tags=["users"])
    async def transferAdminRoleCancel(request: Request):
        """
        Cancels pending admin role transfer. Only current superuser may call this endpoint successfully


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/users/action/synchronize", tags=["users"])
    async def synchronize(request: Request):
        """
        Users synchronization


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/debugMessages", tags=["debugMessages"])
    async def getDebugMessages(
        request: Request,
        filter_: Optional[str] = Query(None, description="Filter messages by tags."),
        types: Optional[str] = Query(None, description="Filter messages by types."),
        from_: Optional[int] = Query(
            None,
            description="Filter messages younger than or equal to parameter value in timestamp.",
        ),
        to_: Optional[int] = Query(
            None,
            description="Filter messages older than or equal to parameter value in timestamp.",
        ),
        last: Optional[int] = Query(
            None,
            description="The identifier of the message that will be returned first. If last is set to 0 then return from the newest message.",
        ),
        offset: Optional[int] = Query(
            None, description="Number of returned messages. -1 means all messages."
        ),
    ):
        """
        Get a list of debug messages


        """
        return await handle_request(request, "GET", None)

    @app.delete("/api/debugMessages", tags=["debugMessages"])
    async def deleteDebugMessages(request: Request):
        """
        Delete debug messages


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/debugMessages/tags", tags=["debugMessages"])
    async def getDebugMessagesTags(request: Request):
        """
        Get a list of defined debug tags


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/rooms", tags=["rooms"])
    async def getRooms(
        request: Request,
        visible: Optional[str] = Query(None, description="Filter rooms by visible."),
        empty: Optional[str] = Query(
            None, description="Filter rooms if are empty or not."
        ),
    ):
        """
        Get a list of all available rooms


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/rooms", tags=["rooms"])
    async def newRoom(request: Request, request_data: RoomCreateRequest = Body(...)):
        """
        Create room


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/rooms/{roomID}", tags=["rooms"])
    async def getRoom(request: Request, roomID: int):
        """
        Get room object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/rooms/{roomID}", tags=["rooms"])
    async def modifyRoom(
        request: Request, roomID: int, request_data: RoomUpdateRequest = Body(...)
    ):
        """
        Modify room


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/rooms/{roomID}", tags=["rooms"])
    async def deleteRoom(request: Request, roomID: int):
        """
        Delete room


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/rooms/{roomID}/action/setAsDefault", tags=["rooms"])
    async def setAsDefault(request: Request, roomID: int):
        """
        Sets as default room in system


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/rooms/{roomID}/groupAssignment", tags=["rooms"])
    async def groupAssignment(
        request: Request, roomID: int, request_data: RoomGroupAssignment = Body(...)
    ):
        """
        Assigns roomID to all entities given in a body


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/energy/devices", tags=["energy"])
    async def getEnergyDevices(request: Request):
        """
        Energy devices info


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/consumption/summary", tags=["energy"])
    async def getConsumptionSummary(
        request: Request,
        period: str = Query(..., description="Time period for which data is returned"),
    ):
        """
        Summary of energy production/consumption


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/consumption/metrics", tags=["energy"])
    async def getConsumptionMetrics(request: Request):
        """
        Metrics of energy production/consumption


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/consumption/detail", tags=["energy"])
    async def getConsumptionDetail(
        request: Request,
        period: str = Query(
            ..., description="Array of time periods for which data is returned"
        ),
    ):
        """
        Details of energy production/consumption


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/consumption/room/{roomId}/detail", tags=["energy"])
    async def getConsumptionRoomDetail(
        request: Request,
        roomId: int,
        period: str = Query(
            ..., description="Array of time periods for which data is returned"
        ),
    ):
        """
        Details of energy production/consumption in room


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/consumption/device/{deviceId}/detail", tags=["energy"])
    async def getConsumptionDeviceDetail(
        request: Request,
        deviceId: int,
        periods: str = Query(
            ..., description="Array of time periods for which data is returned"
        ),
    ):
        """
        Details of given device energy production/consumption in given periods of time


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/billing/summary", tags=["energy"])
    async def getBillingSummary(request: Request):
        """
        Summary of energy cost and consumption during current and last billing periods


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/billing/periods", tags=["energy"])
    async def getBillingPeriods(request: Request):
        """
        List of billing periods


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/energy/billing/periods", tags=["energy"])
    async def postBillingPeriods(
        request: Request, request_data: EnergyBillingPeriodDto = Body(...)
    ):
        """
        Sets new billing period


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/energy/billing/tariff", tags=["energy"])
    async def getBillingTariff(request: Request):
        """
        Energy billing tariff


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/energy/billing/tariff", tags=["energy"])
    async def putBillingTariff(
        request: Request, request_data: EnergyTariffDto = Body(...)
    ):
        """
        Changes energy tariff


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/energy/installationCost", tags=["energy"])
    async def getInstallationCosts(request: Request):
        """
        List of energy installation costs


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/energy/installationCost", tags=["energy"])
    async def createInstallationCost(
        request: Request, request_data: InstallationCostDto = Body(...)
    ):
        """
        Creates installation cost


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/energy/installationCost/{id}", tags=["energy"])
    async def getInstallationCostById(request: Request, id: int):
        """
        Energy installation cost by id


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/energy/installationCost/{id}", tags=["energy"])
    async def updateInstallationCostById(
        request: Request, id: int, request_data: InstallationCostDto = Body(...)
    ):
        """
        Updates energy installation cost with given id.


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/energy/installationCost/{id}", tags=["energy"])
    async def deleteInstallationCostById(request: Request, id: int):
        """
        Deletes installation cost with given id. Main installation cost with id 1 cannot deleted.


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/energy/savings/detail", tags=["energy"])
    async def getSavingsDetail(
        request: Request,
        startDate: str = Query(
            ..., description="Start of time period for which data is returned."
        ),
        endDate: str = Query(
            ..., description="End of time period for which data is returned."
        ),
        intervalType: Optional[str] = Query(
            None,
            description="Time interval seed for data to be returned. Default is Daily.",
        ),
        interval: Optional[str] = Query(
            None,
            description="Time interval seed for data to be returned. Default is 1.",
        ),
    ):
        """
        Details of energy savings


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/savings/summary", tags=["energy"])
    async def getSavingsSummary(request: Request):
        """
        Summary of energy savings


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/savings/installation", tags=["energy"])
    async def getSavingsInstallation(request: Request):
        """
        Energy savings data from beginning of installation


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/ecology/summary", tags=["energy"])
    async def getEcologySummary(request: Request):
        """
        Summary of energy ecology


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/energy/ecology/detail", tags=["energy"])
    async def getEcologyDetail(
        request: Request,
        startDate: str = Query(
            ..., description="Start of time period for which data is returned."
        ),
        endDate: str = Query(
            ..., description="End of time period for which data is returned."
        ),
        intervalType: Optional[str] = Query(
            None,
            description="Time interval seed for data to be returned. Default is Daily.",
        ),
        interval: Optional[str] = Query(
            None,
            description="Time interval seed for data to be returned. Default is 1.",
        ),
    ):
        """
        Details of energy ecology


        """
        return await handle_request(request, "GET", None)

    @app.delete("/api/energy/consumption", tags=["energy"])
    async def clearEnergyData(
        request: Request,
        deviceIds: Optional[str] = Query(
            None,
            description="Device ids for which energy data should be cleared. If not given then energy data for all devices will be cleared.",
        ),
        startPeriod: Optional[str] = Query(
            None, description="Start period (inclusive) of the data to be cleared."
        ),
        endPeriod: Optional[str] = Query(
            None, description="End period (exclusive) of the data to be cleared."
        ),
        subtractWholeHouseEnergy: Optional[str] = Query(
            None,
            description="Flag indicating if removed devices energy data should be subtracted from cumulative house energy data",
        ),
    ):
        """
        Clears energy data. Clears all energy data when no parameters are passed.


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/energy/settings", tags=["energy"])
    async def getSettings(request: Request):
        """
        Energy related settings


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/energy/settings", tags=["energy"])
    async def updateSettings(
        request: Request, request_data: EnergySettingsDto = Body(...)
    ):
        """
        Updates energy related settings


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/service/reboot", tags=["reboot"])
    async def reboot(request: Request, request_data: ResetRequestDto = Body(...)):
        """
        Reboot device


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get(
        "/api/energy/{timestampFrom}/{timestampTo}/{dataSet}/{type}/{unit}/{id}",
        tags=["consumption"],
    )
    async def getEnergyFromTo(
        request: Request,
        timestampFrom: int,
        timestampTo: int,
        dataSet: str,
        type_: str,
        unit: str,
        id: int,
    ):
        """
        Get energy from/to


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/panels/energy?id={id}", tags=["consumption"])
    async def getEnergy(request: Request, id: int):
        """
        Get energy


        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/coPlot?id={id}&from={timestampFrom}&to={timestampTo}",
        tags=["consumption"],
    )
    async def getCoFromTo(
        request: Request, id: int, timestampFrom: int, timestampTo: int
    ):
        """
        Get co from/to


        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/temperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/temperature/{id}",
        tags=["consumption"],
    )
    async def getTemperatureFromTo(
        request: Request,
        timestampFrom: int,
        timestampTo: int,
        dataSet: str,
        type_: str,
        id: int,
    ):
        """
        Get temperature from/to


        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/smokeTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/smoke/{id}",
        tags=["consumption"],
    )
    async def getSmokeFromTo(
        request: Request,
        timestampFrom: int,
        timestampTo: int,
        dataSet: str,
        type_: str,
        id: int,
    ):
        """
        Get smoke from/to


        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/thermostatTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/thermostat/{id}",
        tags=["consumption"],
    )
    async def getThermostatFromTo(
        request: Request,
        timestampFrom: int,
        timestampTo: int,
        dataSet: str,
        type_: str,
        id: int,
    ):
        """
        Get thermostat from/to


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/iosDevices", tags=["iosDevices"])
    async def getIosDevices(request: Request):
        """
        Get a list of all available iosDevices


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/weather", tags=["weather"])
    async def getWeather(request: Request):
        """
        Get weather object


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/deviceNotifications/v1", tags=["deviceNotifications"])
    async def getAllDeviceNotificationsSettings(request: Request):
        """
        Get information about device notifications settings


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/deviceNotifications/v1/{deviceID}", tags=["deviceNotifications"])
    async def updateDeviceNotificationsSettings(
        request: Request, deviceID: int, request_data: Dict[str, Any] = Body(...)
    ):
        """
        Update notifications settings for given device


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/deviceNotifications/v1/{deviceID}", tags=["deviceNotifications"])
    async def getDeviceNotificationsSettings(request: Request, deviceID: int):
        """
        Get notifications settings for given device


        """
        return await handle_request(request, "GET", None)

    @app.delete("/api/deviceNotifications/v1/{deviceID}", tags=["deviceNotifications"])
    async def deleteNotificationsSettings(request: Request, deviceID: int):
        """
        Clear notifications settings for given device


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/sections", tags=["sections"])
    async def getSections(request: Request):
        """
        Get list of all available sections


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/sections", tags=["sections"])
    async def newSection(
        request: Request, request_data: SectionCreateRequest = Body(...)
    ):
        """
        Create section


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/sections/{sectionID}", tags=["sections"])
    async def getSection(request: Request, sectionID: int):
        """
        Get section object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/sections/{sectionID}", tags=["sections"])
    async def modifySection(
        request: Request, sectionID: int, request_data: SectionUpdateRequest = Body(...)
    ):
        """
        Modify section


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/sections/{sectionID}", tags=["sections"])
    async def deleteSection(request: Request, sectionID: int):
        """
        Delete section


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/panels/favoriteColors/v2", tags=["favoriteColors"])
    async def getFavoriteColorsV2(
        request: Request,
        colorComponents: Optional[str] = Query(
            None, description="Time period for which data is returned"
        ),
    ):
        """
        Get favorite colors


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/favoriteColors/v2", tags=["favoriteColors"])
    async def newFavoriteColorV2(
        request: Request, request_data: NewFavoriteColorV2 = Body(...)
    ):
        """
        Create favorite colors object


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put("/api/panels/favoriteColors/v2/{favoriteColorID}", tags=["favoriteColors"])
    async def modifyFavoriteColorV2(
        request: Request,
        favoriteColorID: int,
        request_data: FavoriteColorV2 = Body(...),
    ):
        """
        Modify favorite colors object


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/networkDiscovery/arp", tags=["networkDiscovery"])
    async def networkDiscoveryAction(
        request: Request, request_data: NetworkDiscoveryDto = Body(...)
    ):
        """
        Network Discovery


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/notificationCenter", tags=["notificationCenter"])
    async def createNotification(
        request: Request, request_data: NotificationCenterRequestDto = Body(...)
    ):
        """
        Create notification


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/notificationCenter/{notificationId}", tags=["notificationCenter"])
    async def getNotification(request: Request, notificationId: int):
        """
        Notification


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/notificationCenter/{notificationId}", tags=["notificationCenter"])
    async def putNotification(
        request: Request,
        notificationId: int,
        request_data: NotificationCenterRequestDto = Body(...),
    ):
        """
        Edit notification


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/notificationCenter/{notificationId}", tags=["notificationCenter"])
    async def deleteNotification(request: Request, notificationId: int):
        """
        Delete notification


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/RGBPrograms", tags=["RGBPrograms"])
    async def getRGBPrograms(request: Request):
        """
        Get a list of all available RGB programs


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/RGBPrograms", tags=["RGBPrograms"])
    async def newRGBProgram(
        request: Request, request_data: CreateProgramRequest = Body(...)
    ):
        """
        Create RGB program


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/RGBPrograms/{programID}", tags=["RGBPrograms"])
    async def getRGBProgram(request: Request, programID: int):
        """
        Get RGB program object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/RGBPrograms/{programID}", tags=["RGBPrograms"])
    async def modifyRGBProgram(
        request: Request, programID: int, request_data: ProgramDto = Body(...)
    ):
        """
        Modify RGB program


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/RGBPrograms/{programID}", tags=["RGBPrograms"])
    async def deleteProgram(request: Request, programID: int):
        """
        Delete RGB program


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/quickApp", tags=["quickApp"])
    async def createQuickApp(
        request: Request, request_data: CreateQuickAppRequest = Body(...)
    ):
        """
        Create QuickApp device

        Create QuickApp Device by CreateQuickAppRequest data
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/quickApp/availableTypes", tags=["quickApp"])
    async def getQuickAppTypes(request: Request):
        """
        Get quick apps available types

        Returns device types that can be used when creating new quick app.
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/quickApp/export/{deviceId}", tags=["quickApp"])
    async def exportFile(request: Request, deviceId: int):
        """
        Export QuickApp Device

        Export QuickApp Device to .fqa file
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/quickApp/export/{deviceId}", tags=["quickApp"])
    async def exportEncryptedFile(
        request: Request, deviceId: int, request_data: QuickAppExportRequest = Body(...)
    ):
        """
        Export QuickApp Device

        Export QuickApp Device to .fqa or .fqax (encrypted) file. Exporting encrypted quick app requires internet connection.
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/quickApp/import", tags=["quickApp"])
    async def importFile(request: Request, request_data: Dict[str, Any] = Body(...)):
        """
        Import QuickApp Device

        Import and create QuickApp device from .fqa file
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/quickApp/{deviceId}/files", tags=["quickApp"])
    async def getFiles(request: Request, deviceId: str):
        """
        Get QuickApp Source Files

        Get files list without content
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/quickApp/{deviceId}/files", tags=["quickApp"])
    async def createFile(
        request: Request, deviceId: str, request_data: QuickAppFile = Body(...)
    ):
        """
        Create QuickApp Source File

        Create quickapp file
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put("/api/quickApp/{deviceId}/files", tags=["quickApp"])
    async def updateFiles(
        request: Request, deviceId: str, request_data: Dict[str, Any] = Body(...)
    ):
        """
        Update QuickApp Source Files

        Update quickapp files
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/quickApp/{deviceId}/files/{fileName}", tags=["quickApp"])
    async def getFileDetails(request: Request, deviceId: str, fileName: str):
        """
        Get QuickApp Source File

        Get file details
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/quickApp/{deviceId}/files/{fileName}", tags=["quickApp"])
    async def updateFile(
        request: Request,
        deviceId: str,
        fileName: str,
        request_data: QuickAppFileDetails = Body(...),
    ):
        """
        Update QuickApp Source File

        Update quickapp file
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/quickApp/{deviceId}/files/{fileName}", tags=["quickApp"])
    async def deleteFile(request: Request, deviceId: str, fileName: str):
        """
        Delete QuickApp Source File

        Delete file, main file can't be deleted
        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/devices", tags=["devices"])
    async def getDevices(
        request: Request,
        roomID: Optional[int] = Query(
            None, description="Device list filtered by roomId"
        ),
        interface: Optional[str] = Query(
            None, description="Device list filtered by interface"
        ),
        type_: Optional[str] = Query(None, description="Device list filtered by type"),
        viewVersion: Optional[str] = Query(
            None, description="UI view version supported by the client (eg. v2)"
        ),
    ):
        """
        Get list of available devices for authenticated user


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/devices", tags=["devices"])
    async def create(request: Request, request_data: PluginCreateDto = Body(...)):
        """
        Create plugin


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/devices/filter", tags=["devices"])
    async def filterDevices(
        request: Request,
        viewVersion: Optional[str] = Query(
            None, description="UI view version supported by the client (eg. v2)"
        ),
        request_data: DeviceListFiltersDto = Body(...),
    ):
        """
        Get list of filtered devices available for authenticated user


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/devices/addInterface", tags=["devices"])
    async def addInterface(
        request: Request, request_data: DevicesInterfacesDto = Body(...)
    ):
        """
        Add interfaces to devices


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/devices/deleteInterface", tags=["devices"])
    async def deleteInterface(
        request: Request, request_data: DevicesInterfacesDto = Body(...)
    ):
        """
        Delete interfaces from devices


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/devices?property=[lastLoggedUser,{userId}]", tags=["devices"])
    async def getMobileDeviceForUser(request: Request, userId: int):
        """
        Get mobile device list for user with specified id


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/devices/groupAction/{actionName}", tags=["devices"])
    async def callGroupAction(
        request: Request,
        actionName: str,
        request_data: GroupActionArguments = Body(...),
    ):
        """
        Call group action


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/devices/{deviceID}", tags=["devices"])
    async def getDevice(
        request: Request,
        deviceID: int,
        viewVersion: Optional[str] = Query(
            None, description="UI view version supported by the client (eg. v2)"
        ),
    ):
        """
        Get device object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/devices/{deviceID}", tags=["devices"])
    async def modifyDevice(
        request: Request, deviceID: int, request_data: DeviceDto = Body(...)
    ):
        """
        Modify device


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/devices/{deviceID}", tags=["devices"])
    async def delDevice(request: Request, deviceID: int):
        """
        Delete device


        """
        return await handle_request(request, "DELETE", None)

    @app.delete("/api/slave/{uuid}/api/devices/{deviceID}", tags=["devices"])
    async def delDeviceProxy(request: Request, uuid: str, deviceID: int):
        """
        Delete device using master as a proxy for slave


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/devices/{deviceID}/action/{actionName}", tags=["devices"])
    async def callAction(
        request: Request,
        deviceID: int,
        actionName: str,
        request_data: DeviceActionArgumentsDto = Body(...),
    ):
        """
        Call action on given device


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/devices/action/{timestamp}/{id}", tags=["devices"])
    async def deleteDelayedAction(request: Request, timestamp: int, id: int):
        """
        Delete delayed action


        """
        return await handle_request(request, "DELETE", None)

    @app.post(
        "/api/slave/{uuid}/api/devices/{deviceID}/action/{actionName}", tags=["devices"]
    )
    async def callActionProxySlave(
        request: Request,
        uuid: str,
        deviceID: int,
        actionName: str,
        request_data: DeviceActionArgumentsDto = Body(...),
    ):
        """
        Call action using master as a proxy for slave


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/uiDeviceInfo", tags=["devices"])
    async def getUIDeviceInfo(
        request: Request,
        roomId: Optional[int] = Query(
            None, description="Filter ui device types by room id."
        ),
        type_: Optional[str] = Query(
            None, description="Filter ui device info by type."
        ),
        selectors: Optional[str] = Query(
            None, description="Returns specified fields only."
        ),
        source: Optional[str] = Query(
            None, description="Filter ui device info by source."
        ),
        visible: Optional[str] = Query(
            None, description="Filter ui device info by device visibility."
        ),
        classification: Optional[str] = Query(
            None, description="Filter ui device info by device classification."
        ),
    ):
        """
        Get device info


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/devices/hierarchy", tags=["devices"])
    async def getDeviceTypeHierarchy(request: Request):
        """
        Get device type hierarchy


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/additionalInterfaces", tags=["additionalInterfaces"])
    async def getAdditionalInterfaces(
        request: Request, deviceId: int = Query(..., description="Device id")
    ):
        """
        Get list of all additional interfaces


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/additionalInterfaces/{interfaceName}", tags=["additionalInterfaces"])
    async def getDevicesIdByAdditionalInterfaceName(
        request: Request, interfaceName: str
    ):
        """
        Get list of all devices id which can add this additional interface.


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/service/systemStatus", tags=["systemStatus"])
    async def systemStatus(
        request: Request,
        lang: str = Query(..., description="System status language"),
        _: int = Query(..., description="System status random number"),
    ):
        """
        System status


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/service/systemStatus", tags=["systemStatus"])
    async def setSystemStatus(
        request: Request,
        lang: str = Query(..., description="System status language"),
        request_data: Dict[str, Any] = Body(...),
    ):
        """
        Set system status


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/service/restartServices", tags=["systemStatus"])
    async def clearError(
        request: Request,
        lang: str = Query(..., description="System status language"),
        request_data: Dict[str, Any] = Body(...),
    ):
        """
        Clear error


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/home", tags=["home"])
    async def getHomeInfo(request: Request):
        """
        Get home info


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/home", tags=["home"])
    async def updateHomeInfo(request: Request, request_data: HomeDto = Body(...)):
        """
        Update home info


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/userActivity", tags=["userActivity"])
    async def getUserActivity(request: Request):
        """
        Get user activity list


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/loginStatus", tags=["loginStatus"])
    async def getLoginStatus(request: Request):
        """
        Get login status

        Produces different response when not logged in (optional parameters not included).
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/loginStatus", tags=["loginStatus"])
    async def callLoginAction(
        request: Request,
        action: str = Query(..., description="Name of an action"),
        tosAccepted: Optional[str] = Query(None),
    ):
        """
        Call login action


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/plugins", tags=["plugins"])
    async def getPlugins(request: Request):
        """
        Get all plugins object


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/plugins/callUIEvent", tags=["plugins"])
    async def callUIEvent(
        request: Request,
        deviceID: int = Query(..., description="Device ID"),
        elementName: str = Query(..., description="Element name"),
        eventType: str = Query(..., description="Event type"),
        value: Optional[str] = Query(None, description="Event value"),
    ):
        """
        Call UiEvent Action


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/plugins/callUIEvent", tags=["plugins"])
    async def callUIEvent_post(
        request: Request, request_data: Dict[str, Any] = Body(...)
    ):
        """
        Call UiEvent Action (POST version for JSON data)


        """
        return await handle_request(request, "POST", request_data)

    @app.post("/api/plugins/createChildDevice", tags=["plugins"])
    async def createChildDevice(
        request: Request, request_data: CreateChildDeviceDto = Body(...)
    ):
        """
        Create child device


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/plugins/getView", tags=["plugins"])
    async def getView(
        request: Request,
        id: Optional[int] = Query(None, description="Device id"),
        name: Optional[str] = Query(None, description="Device type name"),
        type_: Optional[str] = Query(
            None, description="View type (config or view). Only use for application/xml"
        ),
        version: Optional[str] = Query(
            None, description="View type (config or view). Only use for application/xml"
        ),
    ):
        """
               Get plugin view

               Get plugin view. Required parameters:
        * **id** - get plugin view by id
        * **name**, **Accept** and **Accept-Language** - get plugin view by type, parameter **type** is optional.
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/plugins/installed", tags=["plugins"])
    async def getInstalledPlugins(request: Request):
        """
        Get installed plugins

        Get installed plugins
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/plugins/installed", tags=["plugins"])
    async def installPlugin(
        request: Request,
        type_: Optional[str] = Query(
            None, description="Type of installing plugin. Type it like a **form data**."
        ),
    ):
        """
        Install plugin

        Install plugin. Valid only for HC2. In HC3 each plugin is being installed during the adding.
        """
        return await handle_request(request, "POST", None)

    @app.delete("/api/plugins/installed", tags=["plugins"])
    async def deletePlugin(
        request: Request,
        type_: Optional[str] = Query(
            None, description="Type of installing plugin. Type it like a **form data**."
        ),
    ):
        """
        Delete plugin

        Delete plugin
        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/plugins/interfaces", tags=["plugins"])
    async def interfaces(
        request: Request, request_data: PluginsInterfaceParamDto = Body(...)
    ):
        """
        Add or remove interfaces


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/plugins/ipCameras", tags=["plugins"])
    async def getIPCameras(request: Request):
        """
        Get all IP cameras object


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/plugins/publishEvent", tags=["plugins"])
    async def pluginPublishEvent(
        request: Request, request_data: Dict[str, Any] = Body(...)
    ):
        """
        Publish event


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/plugins/restart", tags=["plugins"])
    async def restartPlugin(
        request: Request, request_data: RestartPluginRequestDto = Body(...)
    ):
        """
        Restart plugin


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/plugins/types", tags=["plugins"])
    async def getPluginsTypes(request: Request):
        """
        Get information about plugins in system

        Get information about plugins in system
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/plugins/updateProperty", tags=["plugins"])
    async def updateProperty(
        request: Request, request_data: UpdatePropertyDto = Body(...)
    ):
        """
        Update property


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/plugins/updateView", tags=["plugins"])
    async def updateView(request: Request, request_data: PluginUpdateDto = Body(...)):
        """
        Update plugin view

        Update plugin view
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/plugins/v2", tags=["plugins"])
    async def getPluginsV2(request: Request):
        """
        Get all plugins object


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/location", tags=["location settings"])
    async def getLocation(request: Request):
        """
        Get current location


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/location", tags=["location settings"])
    async def modifyLocation(
        request: Request,
        reboot: Optional[str] = Query(None),
        request_data: LocationSettings = Body(...),
    ):
        """
        Modify current location.


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/led", tags=["led settings"])
    async def getLedBrightness(request: Request):
        """
        Get Home Center LED brightness


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/led", tags=["led settings"])
    async def changeLedBrightness(request: Request, request_data: LedDto = Body(...)):
        """
        Modify current Home Center LED brightness


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/network", tags=["network"])
    async def getNetworkConfigurations(request: Request):
        """
        Get network configuration

        Return list of network interfaces with their configuration
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/network/connectivity", tags=["network"])
    async def getInternetConnectivity(request: Request):
        """
        Get Internet connectivity status

        Returns Internet connectivity status
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/network/radio", tags=["network"])
    async def getRadioConfiguration(request: Request):
        """
        Get radio configuration

        Returns radio configuration
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/network/radio", tags=["network"])
    async def setRadioConfiguration(
        request: Request, request_data: radioListConfiguration = Body(...)
    ):
        """
        Update radio configuration

        Set radio configuration
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/network/radio/{radioType}", tags=["network"])
    async def getRadioConfigurationByType(request: Request, radioType: str):
        """
        Get radio configuration by device type

        Get radio configuration by device type
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/network/radio/{radioType}", tags=["network"])
    async def setRadioConfigurationByType(
        request: Request, radioType: str, request_data: radioConfiguration = Body(...)
    ):
        """
        Update radio configuration by device type

        Set radio configuration by device type
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/network/interfaces", tags=["network"])
    async def getNetworkInterfaces(request: Request):
        """
        Get list of network interfaces

        Get array with names of network interfaces
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/network/interfaces/{interfaceName}", tags=["network"])
    async def getNetworkConfigurationByName(request: Request, interfaceName: str):
        """
        Get interface configuration

        Get configuration for the network interface
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/network/interfaces/{interfaceName}", tags=["network"])
    async def setNetworkConfigurationByName(
        request: Request,
        interfaceName: str,
        request_data: interfaceConfiguration = Body(...),
    ):
        """
        Update interface configuration

        Set network configuration for the network interface
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get(
        "/api/settings/network/interfaces/{interfaceName}/apList", tags=["network"]
    )
    async def getListOfAccessPoints(request: Request, interfaceName: str):
        """
        Get list of APs

        Get list of available access points
        """
        return await handle_request(request, "GET", None)

    @app.get(
        "/api/settings/network/interfaces/{interfaceName}/apInfo", tags=["network"]
    )
    async def getListOfAccessPointsWithInfo(request: Request, interfaceName: str):
        """
        Get list of APs with additional information

        Get list of available access points with additional information
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/network/connections", tags=["network"])
    async def getConnections(request: Request):
        """
        Get list of network connections

        Returns list of connections
        """
        return await handle_request(request, "GET", None)

    @app.post("/api/settings/network/connections", tags=["network"])
    async def addConnection(request: Request, request_data: connection = Body(...)):
        """
        Add a new connection

        Add a new connection
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/network/connections/{connectionUuid}", tags=["network"])
    async def getConnection(request: Request, connectionUuid: str):
        """
        Get connection status

        Returns connection status
        """
        return await handle_request(request, "GET", None)

    @app.delete("/api/settings/network/connections/{connectionUuid}", tags=["network"])
    async def removeConnection(request: Request, connectionUuid: str):
        """
        Remove the network connection

        Remove the network connection
        """
        return await handle_request(request, "DELETE", None)

    @app.put("/api/settings/network/connections/{connectionUuid}", tags=["network"])
    async def updateConnection(
        request: Request, connectionUuid: str, request_data: connection = Body(...)
    ):
        """
        Update the network connection

        Update the network connection
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post(
        "/api/settings/network/connections/{connectionUuid}/check", tags=["network"]
    )
    async def checkConnection(request: Request, connectionUuid: str):
        """
        Check the connection status

        Check the connection status
        """
        return await handle_request(request, "POST", None)

    @app.post(
        "/api/settings/network/connections/{connectionUuid}/connect", tags=["network"]
    )
    async def connectConnection(request: Request, connectionUuid: str):
        """
        Connect to the wireless network

        Connect to the wireless network
        """
        return await handle_request(request, "POST", None)

    @app.post(
        "/api/settings/network/connections/{connectionUuid}/disconnect",
        tags=["network"],
    )
    async def disconnectConnection(request: Request, connectionUuid: str):
        """
        Disconnect from the wireless network

        Disconnect from the wireless network
        """
        return await handle_request(request, "POST", None)

    @app.put("/api/settings/network/resetInterfaces", tags=["network"])
    async def resetNetworkInterfaces(request: Request):
        """
        Reset network interfaces configuration

        Resets network interfaces configuration to defaults
        """
        return await handle_request(request, "PUT", None)

    @app.get("/api/settings/network/AccessPointMode", tags=["network"])
    async def getAccessPointMode(request: Request):
        """
        Get AccessPoint status

        Get AccessPoint status
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/network/AccessPointMode", tags=["network"])
    async def setAccessPointMode(
        request: Request, request_data: accessPointMode = Body(...)
    ):
        """
        Set AccessPoint mode

        Set AccessPoint mode
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/network/enabledProtocols", tags=["network"])
    async def getEnabledProtocols(request: Request):
        """
        Get enabled protocols

        Get enabled protocols
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/network/enabledProtocols", tags=["network"])
    async def setEnabledProtocols(
        request: Request, request_data: protocols = Body(...)
    ):
        """
        Set enabled protocols

        Set enabled protocols
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/remoteAccess/status", tags=["remoteAccess"])
    async def getRemoteAccessStatus(request: Request):
        """
        Get all remote access statuses

        Get all remote access statuses
        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/remoteAccess/status/{typeName}", tags=["remoteAccess"])
    async def getRemoteAccessTypeState(request: Request, typeName: str):
        """
        Get remote access type state

        Get remote access type state
        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/remoteAccess/status/{typeName}", tags=["remoteAccess"])
    async def setRemoteAccessTypeState(
        request: Request, typeName: str, request_data: remoteAccessState = Body(...)
    ):
        """
        Set remote access type state

        Set remote access type state
        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/settings/certificates/ca", tags=["certificates"])
    async def getRootCACertificate(request: Request):
        """
        Get the Root CA certificate


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/settings/info", tags=["info settings"])
    async def getSettings(request: Request):
        """
        Get current info settings


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/settings/info", tags=["info settings"])
    async def modifySettings(request: Request, request_data: Settings = Body(...)):
        """
        Modify current info settings


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/alarms/v1/history/", tags=["alarms"])
    async def getAlarmHistory(
        request: Request,
        from_: Optional[str] = Query(
            None,
            description="The start time 'from' which historical entries will be shown. Default value is 0 if not specifiad.",
        ),
        to_: Optional[str] = Query(
            None,
            description="The end time 'to' which historical entries will be shown. Default value is current timestamp if not specifiad.",
        ),
        pageSize: Optional[str] = Query(
            None,
            description="The number of items to skip before starting to collect the result set. Default value is 50 if not specifiad.",
        ),
        page: Optional[str] = Query(
            None,
            description="The number of items to return. Default value is 0 if not specifiad.",
        ),
        order: Optional[str] = Query(
            None,
            description="Sort history records by timestamp either in ascending or descending(default) order.",
        ),
        type_: Optional[str] = Query(
            None,
            description="Filter history records by type. If not specified return all records.",
        ),
    ):
        """
        Get alarm history entries


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/alarms/v1/partitions", tags=["alarms"])
    async def getAlarmPartitions(request: Request):
        """
        Get all alarm partitions


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/alarms/v1/partitions", tags=["alarms"])
    async def createAlarmPartition(
        request: Request, request_data: NewPartitionDto = Body(...)
    ):
        """
        Creates new alarm partition. The partition will be disarmed by default.


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/alarms/v1/partitions/breached", tags=["alarms"])
    async def getBreachedAlarmPartitions(request: Request):
        """
        Get breached partition ids


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/alarms/v1/partitions/{partitionID}", tags=["alarms"])
    async def getAlarmPartitionById(request: Request, partitionID: int):
        """
        Get existing partition


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/alarms/v1/partitions/{partitionID}", tags=["alarms"])
    async def updateAlarmPartitionById(
        request: Request, partitionID: int, request_data: NewPartitionDto = Body(...)
    ):
        """
        Update existing partition


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/alarms/v1/partitions/{partitionID}", tags=["alarms"])
    async def deleteAlarmPartitionById(request: Request, partitionID: int):
        """
        Delete existing partition


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/alarms/v1/partitions/actions/tryArm", tags=["alarms"])
    async def tryArmAlarmPartitions(request: Request):
        """
        Try to arm all alarm partitions after sensor breached status verification


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/alarms/v1/partitions/actions/arm", tags=["alarms"])
    async def armAlarmPartitions(request: Request):
        """
        Arm all alarm partitions


        """
        return await handle_request(request, "POST", None)

    @app.delete("/api/alarms/v1/partitions/actions/arm", tags=["alarms"])
    async def disarmAlarmPartitions(request: Request):
        """
        Disarm all alarm partitions


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/alarms/v1/partitions/{partitionID}/actions/tryArm", tags=["alarms"])
    async def tryArmAlarmPartitionById(request: Request, partitionID: int):
        """
        Try to arm alarm partition after sensor breached status verification


        """
        return await handle_request(request, "POST", None)

    @app.post("/api/alarms/v1/partitions/{partitionID}/actions/arm", tags=["alarms"])
    async def armAlarmPartitionById(request: Request, partitionID: int):
        """
        Arm alarm partition


        """
        return await handle_request(request, "POST", None)

    @app.delete("/api/alarms/v1/partitions/{partitionID}/actions/arm", tags=["alarms"])
    async def disarmAlarmPartitionById(request: Request, partitionID: int):
        """
        Disarm alarm partition


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/alarms/v1/devices/", tags=["alarms"])
    async def getAlarmDevices(request: Request):
        """
        Get alarm devices


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/panels/humidity", tags=["humidity panel"])
    async def getHumidity(request: Request):
        """
        Get a list of all available humidity objects


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/humidity", tags=["humidity panel"])
    async def createHumidity(request: Request, request_data: inline_object = Body(...)):
        """
        Create humidity


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/humidity/{humidityID}", tags=["humidity panel"])
    async def getHumidityById(request: Request, humidityID: int):
        """
        Get humidity object


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/panels/humidity/{humidityID}", tags=["humidity panel"])
    async def modifyHumidity(
        request: Request, humidityID: int, request_data: HumidityZone = Body(...)
    ):
        """
        Modify humidity


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/panels/humidity/{humidityID}", tags=["humidity panel"])
    async def deleteHumidity(request: Request, humidityID: int):
        """
        Delete humidity


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/panels/location", tags=["location panel"])
    async def getPanelsLocations(request: Request):
        """
        Get a list of all available locations


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/location", tags=["location panel"])
    async def newPanelsLocation(
        request: Request, request_data: LocationRequest = Body(...)
    ):
        """
        Create location


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/location/{locationID}", tags=["location panel"])
    async def getPanelsLocation(request: Request, locationID: int):
        """
        Get location


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/panels/location/{locationID}", tags=["location panel"])
    async def modifyPanelsLocationById(
        request: Request, locationID: int, request_data: LocationRequest = Body(...)
    ):
        """
        Modify location


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/panels/location/{locationID}", tags=["location panel"])
    async def deletePanelsLocation(request: Request, locationID: int):
        """
        Delete location


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/panels/sprinklers", tags=["sprinklers panel"])
    async def getSprinklerSchedules(request: Request):
        """
        Get all available sprinkler schedules


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/sprinklers", tags=["sprinklers panel"])
    async def postSprinklerSchedules(
        request: Request, request_data: SprinklerScheduleCreateRequest = Body(...)
    ):
        """
        Creates new sprinkler schedule


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/sprinklers/{scheduleId}", tags=["sprinklers panel"])
    async def getSprinklerSchedule(request: Request, scheduleId: int):
        """
        Get specific sprinkler schedule


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/panels/sprinklers/{scheduleId}", tags=["sprinklers panel"])
    async def putSprinklerSchedule(
        request: Request,
        scheduleId: int,
        request_data: SprinklerScheduleRequest = Body(...),
    ):
        """
        Update specific sprinkler schedule


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/panels/sprinklers/{scheduleId}", tags=["sprinklers panel"])
    async def deleteSprinklerSchedule(request: Request, scheduleId: int):
        """
        Removes specific sprinkler schedule


        """
        return await handle_request(request, "DELETE", None)

    @app.post(
        "/api/panels/sprinklers/{scheduleId}/sequences", tags=["sprinklers panel"]
    )
    async def postSprinklerSequence(
        request: Request,
        scheduleId: int,
        request_data: SprinklerSequenceRequest = Body(...),
    ):
        """
        Create new sprinkler sequence


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.put(
        "/api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}",
        tags=["sprinklers panel"],
    )
    async def putSprinklerSequence(
        request: Request,
        scheduleId: int,
        sequenceId: int,
        request_data: SprinklerSequenceRequest = Body(...),
    ):
        """
        Update specific sprinkler sequence


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete(
        "/api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}",
        tags=["sprinklers panel"],
    )
    async def deleteSprinklerSequence(
        request: Request, scheduleId: int, sequenceId: int
    ):
        """
        Removes specific sprinkler sequence from schedule


        """
        return await handle_request(request, "DELETE", None)

    @app.post(
        "/api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/startWatering",
        tags=["sprinklers panel"],
    )
    async def postSprinklerSequenceStartWatering(
        request: Request,
        scheduleId: int,
        sequenceId: int,
        wateringTime: Optional[str] = Query(
            None, description="Watering time in seconds"
        ),
    ):
        """
        Start given sequence


        """
        return await handle_request(request, "POST", None)

    @app.post(
        "/api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/stopWatering",
        tags=["sprinklers panel"],
    )
    async def postSprinklerSequenceStopWatering(
        request: Request, scheduleId: int, sequenceId: int
    ):
        """
        Stop given sequence


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/panels/family", tags=["family panel"])
    async def getFamily(
        request: Request,
        userID: int = Query(..., description="Request userID"),
        from_: int = Query(..., description="Request timestamp for from"),
        to_: int = Query(..., description="Request timestamp for to"),
    ):
        """
        Get users family


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/panels/notifications", tags=["notification panel"])
    async def getPanelsNotifications(request: Request):
        """
        Get a list of all available notifications


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/notifications", tags=["notification panel"])
    async def newPanelsNotification(
        request: Request, request_data: inline_object = Body(...)
    ):
        """
        Create notification

        Notification body
        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/notifications/{notificationID}", tags=["notification panel"])
    async def getPanelsNotification(request: Request, notificationID: int):
        """
        Get notification


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/panels/notifications/{notificationID}", tags=["notification panel"])
    async def modifyPanelsNotificationById(
        request: Request, notificationID: int, request_data: Dict[str, Any] = Body(...)
    ):
        """
        Modify notification


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete(
        "/api/panels/notifications/{notificationID}", tags=["notification panel"]
    )
    async def deletePanelsNotification(request: Request, notificationID: int):
        """
        Delete notification


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/customEvents", tags=["customEvents panel"])
    async def getCustomEvents(request: Request):
        """
        Get a list of all defined custom events


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/customEvents", tags=["customEvents panel"])
    async def createCustomEvent(
        request: Request, request_data: CustomEventDto = Body(...)
    ):
        """
        Create custom event


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/customEvents/{customEventName}", tags=["customEvents panel"])
    async def getCustomEvent(request: Request, customEventName: str):
        """
        Get custom event with provided name


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/customEvents/{customEventName}", tags=["customEvents panel"])
    async def emitCustomEvent(request: Request, customEventName: str):
        """
        Emit custom event


        """
        return await handle_request(request, "POST", None)

    @app.put("/api/customEvents/{customEventName}", tags=["customEvents panel"])
    async def modifyCustomEvent(
        request: Request, customEventName: str, request_data: CustomEventDto = Body(...)
    ):
        """
        Modify custom event


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/customEvents/{customEventName}", tags=["customEvents panel"])
    async def deleteCustomEvent(request: Request, customEventName: str):
        """
        Delete custom event


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/customEvents/{customEventName}/publish", tags=["customEvents panel"])
    async def emitCustomEventByGet(request: Request, customEventName: str):
        """
        Emit custom event


        """
        return await handle_request(request, "GET", None)

    @app.get("/api/globalVariables", tags=["globalVariables panel"])
    async def getGlobalVariables(request: Request):
        """
        Get a list of all available global variables


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/globalVariables", tags=["globalVariables panel"])
    async def createGlobalVariable(
        request: Request, request_data: GlobalVariableDto = Body(...)
    ):
        """
        Create global variable


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get(
        "/api/globalVariables/{globalVariableName}", tags=["globalVariables panel"]
    )
    async def getGlobalVariable(request: Request, globalVariableName: str):
        """
        Get global variable


        """
        return await handle_request(request, "GET", None)

    @app.put(
        "/api/globalVariables/{globalVariableName}", tags=["globalVariables panel"]
    )
    async def modifyGlobalVariable(
        request: Request,
        globalVariableName: str,
        request_data: GlobalVariableDto = Body(...),
    ):
        """
        Modify global variable


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete(
        "/api/globalVariables/{globalVariableName}", tags=["globalVariables panel"]
    )
    async def deleteGlobalVariable(request: Request, globalVariableName: str):
        """
        Delete global variable


        """
        return await handle_request(request, "DELETE", None)

    @app.get("/api/panels/climate", tags=["Climate panel"])
    async def getClimates(
        request: Request,
        detailed: Optional[str] = Query(
            None,
            description="True value returns advanced climate zone model. False value returns basic climate zone model. Default (if 'detailed' not exist) returns basic climate zone model.",
        ),
    ):
        """
        Get a list of all available climate zones


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/panels/climate", tags=["Climate panel"])
    async def createClimateZone(
        request: Request, request_data: AdvancedClimateZone = Body(...)
    ):
        """
        Create climate zone


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/panels/climate/{climateID}", tags=["Climate panel"])
    async def getClimate(request: Request, climateID: int):
        """
        Get specific climate zone


        """
        return await handle_request(request, "GET", None)

    @app.put("/api/panels/climate/{climateID}", tags=["Climate panel"])
    async def modifyClimateWithIdInPath(
        request: Request, climateID: int, request_data: AdvancedClimateZone = Body(...)
    ):
        """
        Modify specific climate zone


        """
        return await handle_request(
            request,
            "PUT",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.delete("/api/panels/climate/{climateID}", tags=["Climate panel"])
    async def deleteClimate(request: Request, climateID: int):
        """
        Delete specific climate zone


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/panels/climate/action/createDefaultZones", tags=["Climate panel"])
    async def createClimateDefaultZones(request: Request):
        """
        Create climate default zones


        """
        return await handle_request(request, "POST", None)

    @app.get("/api/panels/climate/availableDevices", tags=["Climate panel"])
    async def getClimateDevices(request: Request):
        """
        Get a list of all available climate devices


        """
        return await handle_request(request, "GET", None)

    @app.post("/api/mobile/push", tags=["push"])
    async def createPushMessage(
        request: Request, request_data: CreatePushRequest = Body(...)
    ):
        """
        Create push message


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.post("/api/mobile/push/{id}", tags=["push"])
    async def pushDoAction(request: Request, id: int):
        """
        Do action of push.


        """
        return await handle_request(request, "POST", None)

    @app.delete("/api/mobile/push/{id}", tags=["push"])
    async def deletePush(request: Request, id: int):
        """
        Delete push.


        """
        return await handle_request(request, "DELETE", None)

    @app.post("/api/service/factoryReset", tags=["system"])
    async def factoryReset(
        request: Request, request_data: FactoryResetRequestBody = Body(...)
    ):
        """
        Performs asynchronous system reset to factory defaults


        """
        return await handle_request(
            request,
            "POST",
            request_data.dict() if hasattr(request_data, "dict") else request_data,
        )

    @app.get("/api/events/history", tags=["historyEvent"])
    async def getHistoryEvents(
        request: Request,
        eventType: Optional[str] = Query(None, description="event type"),
        from_: Optional[int] = Query(None, description="time from"),
        to_: Optional[int] = Query(None, description="time to"),
        sourceType: Optional[str] = Query(None, description="event source object type"),
        sourceId: Optional[int] = Query(None, description="event source object id"),
        objectType: Optional[str] = Query(
            None, description="event related object type"
        ),
        objectId: Optional[int] = Query(None, description="event related object id"),
        lastId: Optional[int] = Query(
            None,
            description="requests with id<=lastId will be skipped (only more recent entries then lastId will be returned)",
        ),
        numberOfRecords: Optional[int] = Query(
            None, description="response will be limited to numberOfRecords entries"
        ),
        roomId: Optional[int] = Query(
            None, description="response will be filtered to objects having roomId"
        ),
        sectionId: Optional[int] = Query(
            None, description="response will be filtered to objects having sectionId"
        ),
        category: Optional[int] = Query(
            None, description="response will be filtered to objects having category"
        ),
    ):
        """
        Retrieves list of events that match filters


        """
        return await handle_request(request, "GET", None)

    @app.delete("/api/events/history", tags=["historyEvent"])
    async def deleteHistoryEvents(
        request: Request,
        eventType: Optional[str] = Query(None, description="event type"),
        timestamp: Optional[int] = Query(
            None, description="affects events before timestamp"
        ),
        shrink: Optional[int] = Query(
            None,
            description="deletes oldest events limiting number of events left to this value",
        ),
        objectType: Optional[str] = Query(
            None, description="event related object type"
        ),
        objectId: Optional[int] = Query(None, description="event related object id"),
    ):
        """
        deletes events that fulfill conditions


        """
        return await handle_request(request, "DELETE", None)

    logger.info(f"Created 269 API endpoints with full type safety")
