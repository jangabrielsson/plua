"""
Fibaro HC3 API Emulation Server
Auto-generated from Swagger/OpenAPI specifications.
Delegates all requests to Lua via _PY.fibaro_api_hook function.
"""

from fastapi import FastAPI, Query, Body, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# This will be set by the main module
interpreter = None

def set_interpreter(lua_interpreter):
    """Set the Lua interpreter instance."""
    global interpreter
    interpreter = lua_interpreter

def create_fibaro_api_routes(app: FastAPI):
    """Create all Fibaro API routes."""
    
    # Check if we have an interpreter set
    if interpreter is None:
        raise RuntimeError("Interpreter not set. Call set_interpreter() first.")
    

        # Endpoints from categories.json

    @app.get("/api/categories")
    async def getCategories():
        """
        List of supported categories
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/categories"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from scenes.json

    @app.get("/api/scenes")
    async def getSceneList(alexaProhibited: Optional[str] = Query(None)):
        """
        Get a list of all available scenes
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/scenes"
        query_params = {}
        path_params = {}
        
        if alexaProhibited is not None:
            query_params["alexaProhibited"] = alexaProhibited
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes")
    async def createScene(request_data: dict = Body(...)):
        """
        Create scene
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/hasTriggers")
    async def filterScenesByTriggers(request_data: dict = Body(...)):
        """
        Filter scenes by triggers
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/hasTriggers"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/scenes/{sceneID}")
    async def getScene(sceneID: int, alexaProhibited: Optional[str] = Query(None)):
        """
        Get scene object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/scenes/{sceneID}"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        if alexaProhibited is not None:
            query_params["alexaProhibited"] = alexaProhibited
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/scenes/{sceneID}")
    async def modifyScene(sceneID: int, request_data: dict = Body(...)):
        """
        Modify scene
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/scenes/{sceneID}"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/scenes/{sceneID}")
    async def deleteScene(sceneID: int):
        """
        Delete scene
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/scenes/{sceneID}"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/scenes/{sceneID}/execute")
    async def executeSceneByGet(sceneID: int, pin: Optional[str] = Query(None)):
        """
        Executes asynchronously executive part of the scene neglecting conditional part.
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/scenes/{sceneID}/execute"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        if pin is not None:
            query_params["pin"] = pin
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/execute")
    async def executeScene(sceneID: int, request_data: dict = Body(...)):
        """
        Executes asynchronously executive part of the scene neglecting conditional part.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/execute"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/scenes/{sceneID}/executeSync")
    async def executeSceneSyncByGet(sceneID: int, pin: Optional[str] = Query(None)):
        """
        Executes synchronously executive part of the scene neglecting conditional part.
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/scenes/{sceneID}/executeSync"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        if pin is not None:
            query_params["pin"] = pin
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/executeSync")
    async def executeSceneSync(sceneID: int, request_data: dict = Body(...)):
        """
        Executes synchronously executive part of the scene neglecting conditional part.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/executeSync"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/convert")
    async def convertScene(sceneID: int):
        """
        Convert block scene to lua.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/convert"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/copy")
    async def copyScene(sceneID: int):
        """
        Create scene copy.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/copy"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/copyAndConvert")
    async def copyAndConvertScene(sceneID: int):
        """
        Copy and convert block scene to lua.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/copyAndConvert"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/scenes/{sceneID}/kill")
    async def killSceneByGet(sceneID: int, pin: Optional[str] = Query(None)):
        """
        Kill running scene.
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/scenes/{sceneID}/kill"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        if pin is not None:
            query_params["pin"] = pin
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/scenes/{sceneID}/kill")
    async def killScene(sceneID: int):
        """
        Kill running scene.
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/scenes/{sceneID}/kill"
        query_params = {}
        path_params = {}
        
        path_params["sceneID"] = sceneID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from resetZigbee.json

    @app.post("/api/service/resetZigbee")
    async def resetZigbee():
        """
        Reset Zigbee network
        Reset Zigbee network
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/service/resetZigbee"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from icons.json

    @app.get("/api/icons")
    async def getIcons(deviceType: Optional[str] = Query(None)):
        """
        Get a list of all available icons
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/icons"
        query_params = {}
        path_params = {}
        
        if deviceType is not None:
            query_params["deviceType"] = deviceType
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/icons")
    async def uploadIcon(request_data: dict = Body(...)):
        """
        Upload icon
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/icons"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/icons")
    async def deleteIcon(id: Optional[int] = Query(None), name: Optional[str] = Query(None), type_param: str = Query(...), fileExtension: Optional[str] = Query(None)):
        """
        Delete icon
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/icons"
        query_params = {}
        path_params = {}
        
        if id is not None:
            query_params["id"] = id
        if name is not None:
            query_params["name"] = name
        if type_param is not None:
            query_params["type"] = type_param
        if fileExtension is not None:
            query_params["fileExtension"] = fileExtension
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from capabilities.json

    @app.get("/api/service/capabilities")
    async def getCapabilities():
        """
        Get communication protocols capabilities
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/capabilities"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from limits.json

    @app.get("/api/limits")
    async def getLimits():
        """
        Get limits object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/limits"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from sortOrder.json

    @app.post("/api/sortOrder")
    async def updateSortOrder(request_data: dict = Body(...)):
        """
        Update sort order
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/sortOrder"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from favoriteColors.json

    @app.get("/api/panels/favoriteColors")
    async def getFavoriteColors():
        """
        Get favorite colors
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/panels/favoriteColors"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/panels/favoriteColors")
    async def newFavoriteColor(request_data: dict = Body(...)):
        """
        Create favorite colors object
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/panels/favoriteColors"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/panels/favoriteColors/{favoriteColorID}")
    async def modifyFavoriteColor(favoriteColorID: int, request_data: dict = Body(...)):
        """
        Modify favorite colors object
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/panels/favoriteColors/{favoriteColorID}"
        query_params = {}
        path_params = {}
        
        path_params["favoriteColorID"] = favoriteColorID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/panels/favoriteColors/{favoriteColorID}")
    async def deleteFavoriteColor(favoriteColorID: int):
        """
        Delete favorite colors
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/panels/favoriteColors/{favoriteColorID}"
        query_params = {}
        path_params = {}
        
        path_params["favoriteColorID"] = favoriteColorID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from refreshStates.json

    @app.get("/api/refreshStates")
    async def refreshStates(last: int = Query(...), lang: str = Query(...), rand: str = Query(...), logs: Optional[str] = Query(None)):
        """
        Refresh sates
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/refreshStates"
        query_params = {}
        path_params = {}
        
        if last is not None:
            query_params["last"] = last
        if lang is not None:
            query_params["lang"] = lang
        if rand is not None:
            query_params["rand"] = rand
        if logs is not None:
            query_params["logs"] = logs
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from profiles.json

    @app.get("/api/profiles")
    async def getProfiles(showHidden: Optional[str] = Query(None)):
        """
        Get all profiles and active profile
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/profiles"
        query_params = {}
        path_params = {}
        
        if showHidden is not None:
            query_params["showHidden"] = showHidden
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/profiles")
    async def updateProfiles(request_data: dict = Body(...)):
        """
        Update profiles and set active profile
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/profiles"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/profiles")
    async def createProfile(request_data: dict = Body(...)):
        """
        Create new profile with provided name
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/profiles"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/profiles/{profileId}")
    async def getProfileById(profileId: int, showHidden: Optional[str] = Query(None)):
        """
        Get profile
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/profiles/{profileId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        if showHidden is not None:
            query_params["showHidden"] = showHidden
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/profiles/{profileId}")
    async def updateProfileById(profileId: int, request_data: dict = Body(...)):
        """
        Update existing profile
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/profiles/{profileId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/profiles/{profileId}")
    async def removeProfileById(profileId: int):
        """
        Remove existing profile
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/profiles/{profileId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/profiles/{profileId}/partitions/{partitionId}")
    async def updateProfilePartitionAction(profileId: int, partitionId: int, request_data: dict = Body(...)):
        """
        Update profile partition action
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/profiles/{profileId}/partitions/{partitionId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        path_params["partitionId"] = partitionId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/profiles/{profileId}/climateZones/{zoneId}")
    async def updateProfileClimateZoneAction(profileId: int, zoneId: int, request_data: dict = Body(...)):
        """
        Update profile climate zone action
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/profiles/{profileId}/climateZones/{zoneId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        path_params["zoneId"] = zoneId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/profiles/{profileId}/scenes/{sceneId}")
    async def updateProfileSceneActor(profileId: int, sceneId: int, request_data: dict = Body(...)):
        """
        Update profile scene actor
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/profiles/{profileId}/scenes/{sceneId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        path_params["sceneId"] = sceneId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/profiles/reset")
    async def resetProfiles():
        """
        Rest profiles model to default value
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/profiles/reset"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/profiles/activeProfile/{profileId}")
    async def setActiveProfile(profileId: int):
        """
        Set active profile
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/profiles/activeProfile/{profileId}"
        query_params = {}
        path_params = {}
        
        path_params["profileId"] = profileId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from diagnostics.json

    @app.get("/api/diagnostics")
    async def getDiagnostics():
        """
        Get diagnostics
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/diagnostics"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/apps/com.fibaro.zwave/diagnostics/transmissions")
    async def get__apps_com_fibaro_zwave_diagnostics_transmissions():
        """
        Returns information about zwave transmissions
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/apps/com.fibaro.zwave/diagnostics/transmissions"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from users.json

    @app.get("/api/users")
    async def getUsers(hasDeviceRights: Optional[str] = Query(None), hasSceneRights: Optional[str] = Query(None)):
        """
        Get a list of available users
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/users"
        query_params = {}
        path_params = {}
        
        if hasDeviceRights is not None:
            query_params["hasDeviceRights"] = hasDeviceRights
        if hasSceneRights is not None:
            query_params["hasSceneRights"] = hasSceneRights
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users")
    async def createUser(isOffline: Optional[str] = Query(None), request_data: dict = Body(...)):
        """
        Create User
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users"
        query_params = {}
        path_params = {}
        
        if isOffline is not None:
            query_params["isOffline"] = isOffline
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/users/{userID}")
    async def getUser(userID: int):
        """
        Get user object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/users/{userID}"
        query_params = {}
        path_params = {}
        
        path_params["userID"] = userID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/users/{userID}")
    async def modifyUser(userID: int, request_data: dict = Body(...)):
        """
        Modify user
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/users/{userID}"
        query_params = {}
        path_params = {}
        
        path_params["userID"] = userID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/users/{userID}")
    async def deleteUser(userID: int, keepLocalUser: Optional[str] = Query(None)):
        """
        Delete user
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/users/{userID}"
        query_params = {}
        path_params = {}
        
        path_params["userID"] = userID
        if keepLocalUser is not None:
            query_params["keepLocalUser"] = keepLocalUser
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users/{userID}/raInvite")
    async def inviteUser(userID: int):
        """
        User invitation
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users/{userID}/raInvite"
        query_params = {}
        path_params = {}
        
        path_params["userID"] = userID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users/action/changeAdmin/{newAdminId}")
    async def transferAdminRoleInit(newAdminId: int):
        """
        Initiates transfer of administrator role to {newAdminId}
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users/action/changeAdmin/{newAdminId}"
        query_params = {}
        path_params = {}
        
        path_params["newAdminId"] = newAdminId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users/action/confirmAdminTransfer")
    async def transferAdminRoleConfirm():
        """
        Confirms pending admin role transfer. Only user that is target for admin role may call this endpoint successfully
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users/action/confirmAdminTransfer"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users/action/cancelAdminTransfer")
    async def transferAdminRoleCancel():
        """
        Cancels pending admin role transfer. Only current superuser may call this endpoint successfully
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users/action/cancelAdminTransfer"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/users/action/synchronize")
    async def synchronize():
        """
        Users synchronization
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/users/action/synchronize"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from debugMessages.json

    @app.get("/api/debugMessages")
    async def getDebugMessages(filter_param: Optional[str] = Query(None), types: Optional[str] = Query(None), from_param: Optional[int] = Query(None), to_param: Optional[int] = Query(None), last: Optional[int] = Query(None), offset: Optional[int] = Query(None)):
        """
        Get a list of debug messages
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/debugMessages"
        query_params = {}
        path_params = {}
        
        if filter_param is not None:
            query_params["filter"] = filter_param
        if types is not None:
            query_params["types"] = types
        if from_param is not None:
            query_params["from"] = from_param
        if to_param is not None:
            query_params["to"] = to_param
        if last is not None:
            query_params["last"] = last
        if offset is not None:
            query_params["offset"] = offset
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/debugMessages")
    async def deleteDebugMessages():
        """
        Delete debug messages
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/debugMessages"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/debugMessages/tags")
    async def getDebugMessagesTags():
        """
        Get a list of defined debug tags
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/debugMessages/tags"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from testSatelConnection.json

    @app.post("/api/testSatelConnection")
    async def getTestSatelConnection(request_data: dict = Body(...)):
        """
        Get Satel Connection Status
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/testSatelConnection"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from rooms.json

    @app.get("/api/rooms")
    async def getRooms(visible: Optional[str] = Query(None), empty: Optional[str] = Query(None)):
        """
        Get a list of all available rooms
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/rooms"
        query_params = {}
        path_params = {}
        
        if visible is not None:
            query_params["visible"] = visible
        if empty is not None:
            query_params["empty"] = empty
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/rooms")
    async def newRoom(request_data: dict = Body(...)):
        """
        Create room
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/rooms"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/rooms/{roomID}")
    async def getRoom(roomID: int):
        """
        Get room object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/rooms/{roomID}"
        query_params = {}
        path_params = {}
        
        path_params["roomID"] = roomID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/rooms/{roomID}")
    async def modifyRoom(roomID: int, request_data: dict = Body(...)):
        """
        Modify room
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/rooms/{roomID}"
        query_params = {}
        path_params = {}
        
        path_params["roomID"] = roomID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/rooms/{roomID}")
    async def deleteRoom(roomID: int):
        """
        Delete room
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/rooms/{roomID}"
        query_params = {}
        path_params = {}
        
        path_params["roomID"] = roomID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/rooms/{roomID}/action/setAsDefault")
    async def setAsDefault(roomID: int):
        """
        Sets as default room in system
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/rooms/{roomID}/action/setAsDefault"
        query_params = {}
        path_params = {}
        
        path_params["roomID"] = roomID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/rooms/{roomID}/groupAssignment")
    async def groupAssignment(roomID: int, request_data: dict = Body(...)):
        """
        Assigns roomID to all entities given in a body
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/rooms/{roomID}/groupAssignment"
        query_params = {}
        path_params = {}
        
        path_params["roomID"] = roomID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from energy.json

    @app.get("/api/energy/devices")
    async def getEnergyDevices():
        """
        Energy devices info
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/devices"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/consumption/summary")
    async def getConsumptionSummary(period: str = Query(...)):
        """
        Summary of energy production/consumption
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/consumption/summary"
        query_params = {}
        path_params = {}
        
        if period is not None:
            query_params["period"] = period
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/consumption/metrics")
    async def getConsumptionMetrics():
        """
        Metrics of energy production/consumption
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/consumption/metrics"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/consumption/detail")
    async def getConsumptionDetail(period: str = Query(...)):
        """
        Details of energy production/consumption
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/consumption/detail"
        query_params = {}
        path_params = {}
        
        if period is not None:
            query_params["period"] = period
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/consumption/room/{roomId}/detail")
    async def getConsumptionRoomDetail(roomId: int, period: str = Query(...)):
        """
        Details of energy production/consumption in room
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/consumption/room/{roomId}/detail"
        query_params = {}
        path_params = {}
        
        path_params["roomId"] = roomId
        if period is not None:
            query_params["period"] = period
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/consumption/device/{deviceId}/detail")
    async def getConsumptionDeviceDetail(deviceId: int, periods: str = Query(...)):
        """
        Details of given device energy production/consumption in given periods of time
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/consumption/device/{deviceId}/detail"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        if periods is not None:
            query_params["periods"] = periods
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/billing/summary")
    async def getBillingSummary():
        """
        Summary of energy cost and consumption during current and last billing periods
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/billing/summary"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/billing/periods")
    async def getBillingPeriods():
        """
        List of billing periods
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/billing/periods"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/energy/billing/periods")
    async def postBillingPeriods(request_data: dict = Body(...)):
        """
        Sets new billing period
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/energy/billing/periods"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/billing/tariff")
    async def getBillingTariff():
        """
        Energy billing tariff
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/billing/tariff"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/energy/billing/tariff")
    async def putBillingTariff(request_data: dict = Body(...)):
        """
        Changes energy tariff
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/energy/billing/tariff"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/installationCost")
    async def getInstallationCosts():
        """
        List of energy installation costs
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/installationCost"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/energy/installationCost")
    async def createInstallationCost(request_data: dict = Body(...)):
        """
        Creates installation cost
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/energy/installationCost"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/installationCost/{id}")
    async def getInstallationCostById(id: int):
        """
        Energy installation cost by id
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/installationCost/{id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/energy/installationCost/{id}")
    async def updateInstallationCostById(id: int, request_data: dict = Body(...)):
        """
        Updates energy installation cost with given id.
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/energy/installationCost/{id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/energy/installationCost/{id}")
    async def deleteInstallationCostById(id: int):
        """
        Deletes installation cost with given id. Main installation cost with id 1 cannot deleted.
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/energy/installationCost/{id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/savings/detail")
    async def getSavingsDetail(startDate: str = Query(...), endDate: str = Query(...), intervalType: Optional[str] = Query(None), interval: Optional[str] = Query(None)):
        """
        Details of energy savings
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/savings/detail"
        query_params = {}
        path_params = {}
        
        if startDate is not None:
            query_params["startDate"] = startDate
        if endDate is not None:
            query_params["endDate"] = endDate
        if intervalType is not None:
            query_params["intervalType"] = intervalType
        if interval is not None:
            query_params["interval"] = interval
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/savings/summary")
    async def getSavingsSummary():
        """
        Summary of energy savings
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/savings/summary"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/savings/installation")
    async def getSavingsInstallation():
        """
        Energy savings data from beginning of installation
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/savings/installation"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/ecology/summary")
    async def getEcologySummary():
        """
        Summary of energy ecology
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/ecology/summary"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/ecology/detail")
    async def getEcologyDetail(startDate: str = Query(...), endDate: str = Query(...), intervalType: Optional[str] = Query(None), interval: Optional[str] = Query(None)):
        """
        Details of energy ecology
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/ecology/detail"
        query_params = {}
        path_params = {}
        
        if startDate is not None:
            query_params["startDate"] = startDate
        if endDate is not None:
            query_params["endDate"] = endDate
        if intervalType is not None:
            query_params["intervalType"] = intervalType
        if interval is not None:
            query_params["interval"] = interval
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/energy/consumption")
    async def clearEnergyData(deviceIds: Optional[str] = Query(None), startPeriod: Optional[str] = Query(None), endPeriod: Optional[str] = Query(None), subtractWholeHouseEnergy: Optional[str] = Query(None)):
        """
        Clears energy data. Clears all energy data when no parameters are passed.
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/energy/consumption"
        query_params = {}
        path_params = {}
        
        if deviceIds is not None:
            query_params["deviceIds"] = deviceIds
        if startPeriod is not None:
            query_params["startPeriod"] = startPeriod
        if endPeriod is not None:
            query_params["endPeriod"] = endPeriod
        if subtractWholeHouseEnergy is not None:
            query_params["subtractWholeHouseEnergy"] = subtractWholeHouseEnergy
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/energy/settings")
    async def getSettings():
        """
        Energy related settings
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/settings"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/energy/settings")
    async def updateSettings(request_data: dict = Body(...)):
        """
        Updates energy related settings
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/energy/settings"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from reboot.json

    @app.post("/api/service/reboot")
    async def reboot(request_data: dict = Body(...)):
        """
        Reboot device
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/service/reboot"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from consumption.json

    @app.get("/api/energy/{timestampFrom}/{timestampTo}/{dataSet}/{type}/{unit}/{id}")
    async def getEnergyFromTo(timestampFrom: int, timestampTo: int, dataSet: str, type: str, unit: str, id: int):
        """
        Get energy from/to
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/energy/{timestampFrom}/{timestampTo}/{dataSet}/{type}/{unit}/{id}"
        query_params = {}
        path_params = {}
        
        path_params["timestampFrom"] = timestampFrom
        path_params["timestampTo"] = timestampTo
        path_params["dataSet"] = dataSet
        path_params["type"] = type
        path_params["unit"] = unit
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/panels/energy?id={id}")
    async def getEnergy(id: int):
        """
        Get energy
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/panels/energy?id={id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/coPlot?id={id}&from={timestampFrom}&to={timestampTo}")
    async def getCoFromTo(id: int, timestampFrom: int, timestampTo: int):
        """
        Get co from/to
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/coPlot?id={id}&from={timestampFrom}&to={timestampTo}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        path_params["timestampFrom"] = timestampFrom
        path_params["timestampTo"] = timestampTo
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/temperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/temperature/{id}")
    async def getTemperatureFromTo(timestampFrom: int, timestampTo: int, dataSet: str, type: str, id: int):
        """
        Get temperature from/to
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/temperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/temperature/{id}"
        query_params = {}
        path_params = {}
        
        path_params["timestampFrom"] = timestampFrom
        path_params["timestampTo"] = timestampTo
        path_params["dataSet"] = dataSet
        path_params["type"] = type
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/smokeTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/smoke/{id}")
    async def getSmokeFromTo(timestampFrom: int, timestampTo: int, dataSet: str, type: str, id: int):
        """
        Get smoke from/to
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/smokeTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/smoke/{id}"
        query_params = {}
        path_params = {}
        
        path_params["timestampFrom"] = timestampFrom
        path_params["timestampTo"] = timestampTo
        path_params["dataSet"] = dataSet
        path_params["type"] = type
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/thermostatTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/thermostat/{id}")
    async def getThermostatFromTo(timestampFrom: int, timestampTo: int, dataSet: str, type: str, id: int):
        """
        Get thermostat from/to
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/thermostatTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/thermostat/{id}"
        query_params = {}
        path_params = {}
        
        path_params["timestampFrom"] = timestampFrom
        path_params["timestampTo"] = timestampTo
        path_params["dataSet"] = dataSet
        path_params["type"] = type
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from iosDevices.json

    @app.get("/api/iosDevices")
    async def getIosDevices():
        """
        Get a list of all available iosDevices
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/iosDevices"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from weather.json

    @app.get("/api/weather")
    async def getWeather():
        """
        Get weather object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/weather"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from deviceNotifications.json

    @app.get("/api/deviceNotifications/v1")
    async def getAllDeviceNotificationsSettings():
        """
        Get information about device notifications settings
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/deviceNotifications/v1"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/deviceNotifications/v1/{deviceID}")
    async def updateDeviceNotificationsSettings(deviceID: int, request_data: dict = Body(...)):
        """
        Update notifications settings for given device
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/deviceNotifications/v1/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/deviceNotifications/v1/{deviceID}")
    async def getDeviceNotificationsSettings(deviceID: int):
        """
        Get notifications settings for given device
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/deviceNotifications/v1/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/deviceNotifications/v1/{deviceID}")
    async def deleteNotificationsSettings(deviceID: int):
        """
        Clear notifications settings for given device
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/deviceNotifications/v1/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from sections.json

    @app.get("/api/sections")
    async def getSections():
        """
        Get list of all available sections
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/sections"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/sections")
    async def newSection(request_data: dict = Body(...)):
        """
        Create section
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/sections"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/sections/{sectionID}")
    async def getSection(sectionID: int):
        """
        Get section object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/sections/{sectionID}"
        query_params = {}
        path_params = {}
        
        path_params["sectionID"] = sectionID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/sections/{sectionID}")
    async def modifySection(sectionID: int, request_data: dict = Body(...)):
        """
        Modify section
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/sections/{sectionID}"
        query_params = {}
        path_params = {}
        
        path_params["sectionID"] = sectionID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/sections/{sectionID}")
    async def deleteSection(sectionID: int):
        """
        Delete section
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/sections/{sectionID}"
        query_params = {}
        path_params = {}
        
        path_params["sectionID"] = sectionID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from favoriteColorsV2.json

    @app.get("/api/panels/favoriteColors/v2")
    async def getFavoriteColorsV2(colorComponents: Optional[str] = Query(None)):
        """
        Get favorite colors
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/panels/favoriteColors/v2"
        query_params = {}
        path_params = {}
        
        if colorComponents is not None:
            query_params["colorComponents"] = colorComponents
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/panels/favoriteColors/v2")
    async def newFavoriteColorV2(request_data: dict = Body(...)):
        """
        Create favorite colors object
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/panels/favoriteColors/v2"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/panels/favoriteColors/v2/{favoriteColorID}")
    async def modifyFavoriteColorV2(favoriteColorID: int, request_data: dict = Body(...)):
        """
        Modify favorite colors object
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/panels/favoriteColors/v2/{favoriteColorID}"
        query_params = {}
        path_params = {}
        
        path_params["favoriteColorID"] = favoriteColorID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from networkDiscovery.json

    @app.post("/api/networkDiscovery/arp")
    async def networkDiscoveryAction(request_data: dict = Body(...)):
        """
        Network Discovery
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/networkDiscovery/arp"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from notificationCenter.json

    @app.post("/api/notificationCenter")
    async def createNotification(request_data: dict = Body(...)):
        """
        Create notification
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/notificationCenter"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/notificationCenter/{notificationId}")
    async def getNotification(notificationId: int):
        """
        Notification
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/notificationCenter/{notificationId}"
        query_params = {}
        path_params = {}
        
        path_params["notificationId"] = notificationId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/notificationCenter/{notificationId}")
    async def putNotification(notificationId: int, request_data: dict = Body(...)):
        """
        Edit notification
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/notificationCenter/{notificationId}"
        query_params = {}
        path_params = {}
        
        path_params["notificationId"] = notificationId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/notificationCenter/{notificationId}")
    async def deleteNotification(notificationId: int):
        """
        Delete notification
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/notificationCenter/{notificationId}"
        query_params = {}
        path_params = {}
        
        path_params["notificationId"] = notificationId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from RGBPrograms.json

    @app.get("/api/RGBPrograms")
    async def getRGBPrograms():
        """
        Get a list of all available RGB programs
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/RGBPrograms"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/RGBPrograms")
    async def newRGBProgram(request_data: dict = Body(...)):
        """
        Create RGB program
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/RGBPrograms"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/RGBPrograms/{programID}")
    async def getRGBProgram(programID: int):
        """
        Get RGB program object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/RGBPrograms/{programID}"
        query_params = {}
        path_params = {}
        
        path_params["programID"] = programID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/RGBPrograms/{programID}")
    async def modifyRGBProgram(programID: int, request_data: dict = Body(...)):
        """
        Modify RGB program
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/RGBPrograms/{programID}"
        query_params = {}
        path_params = {}
        
        path_params["programID"] = programID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/RGBPrograms/{programID}")
    async def deleteProgram(programID: int):
        """
        Delete RGB program
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/RGBPrograms/{programID}"
        query_params = {}
        path_params = {}
        
        path_params["programID"] = programID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from quickapp.json

    @app.post("/api/quickApp")
    async def createQuickApp(request_data: dict = Body(...)):
        """
        Create QuickApp device
        Create QuickApp Device by CreateQuickAppRequest data
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/quickApp"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/quickApp/availableTypes")
    async def getQuickAppTypes():
        """
        Get quick apps available types
        Returns device types that can be used when creating new quick app.
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/quickApp/availableTypes"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/quickApp/export/{deviceId}")
    async def exportFile(deviceId: int):
        """
        Export QuickApp Device
        Export QuickApp Device to .fqa file
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/quickApp/export/{deviceId}"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/quickApp/export/{deviceId}")
    async def exportEncryptedFile(deviceId: int, request_data: dict = Body(...)):
        """
        Export QuickApp Device
        Export QuickApp Device to .fqa or .fqax (encrypted) file. Exporting encrypted quick app requires internet connection.
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/quickApp/export/{deviceId}"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/quickApp/import")
    async def importFile(request_data: dict = Body(...)):
        """
        Import QuickApp Device
        Import and create QuickApp device from .fqa file
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/quickApp/import"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/quickApp/{deviceId}/files")
    async def getFiles(deviceId: str):
        """
        Get QuickApp Source Files
        Get files list without content
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/quickApp/{deviceId}/files"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/quickApp/{deviceId}/files")
    async def createFile(deviceId: str, request_data: dict = Body(...)):
        """
        Create QuickApp Source File
        Create quickapp file
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/quickApp/{deviceId}/files"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/quickApp/{deviceId}/files")
    async def updateFiles(deviceId: str, request_data: dict = Body(...)):
        """
        Update QuickApp Source Files
        Update quickapp files
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/quickApp/{deviceId}/files"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/quickApp/{deviceId}/files/{fileName}")
    async def getFileDetails(deviceId: str, fileName: str):
        """
        Get QuickApp Source File
        Get file details
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/quickApp/{deviceId}/files/{fileName}"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        path_params["fileName"] = fileName
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/quickApp/{deviceId}/files/{fileName}")
    async def updateFile(deviceId: str, fileName: str, request_data: dict = Body(...)):
        """
        Update QuickApp Source File
        Update quickapp file
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/quickApp/{deviceId}/files/{fileName}"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        path_params["fileName"] = fileName
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/quickApp/{deviceId}/files/{fileName}")
    async def deleteFile(deviceId: str, fileName: str):
        """
        Delete QuickApp Source File
        Delete file, main file can't be deleted
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/quickApp/{deviceId}/files/{fileName}"
        query_params = {}
        path_params = {}
        
        path_params["deviceId"] = deviceId
        path_params["fileName"] = fileName
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from devices.json

    @app.get("/api/devices")
    async def getDevices(roomID: Optional[int] = Query(None), interface: Optional[str] = Query(None), type_param: Optional[str] = Query(None), viewVersion: Optional[str] = Query(None)):
        """
        Get list of available devices for authenticated user
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/devices"
        query_params = {}
        path_params = {}
        
        if roomID is not None:
            query_params["roomID"] = roomID
        if interface is not None:
            query_params["interface"] = interface
        if type_param is not None:
            query_params["type"] = type_param
        if viewVersion is not None:
            query_params["viewVersion"] = viewVersion
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices")
    async def create(request_data: dict = Body(...)):
        """
        Create plugin
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices/filter")
    async def filterDevices(viewVersion: Optional[str] = Query(None), request_data: dict = Body(...)):
        """
        Get list of filtered devices available for authenticated user
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices/filter"
        query_params = {}
        path_params = {}
        
        if viewVersion is not None:
            query_params["viewVersion"] = viewVersion
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices/addInterface")
    async def addInterface(request_data: dict = Body(...)):
        """
        Add interfaces to devices
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices/addInterface"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices/deleteInterface")
    async def deleteInterface(request_data: dict = Body(...)):
        """
        Delete interfaces from devices
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices/deleteInterface"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/devices?property=[lastLoggedUser,{userId}]")
    async def getMobileDeviceForUser(userId: int):
        """
        Get mobile device list for user with specified id
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/devices?property=[lastLoggedUser,{userId}]"
        query_params = {}
        path_params = {}
        
        path_params["userId"] = userId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices/groupAction/{actionName}")
    async def callGroupAction(actionName: str, request_data: dict = Body(...)):
        """
        Call group action
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices/groupAction/{actionName}"
        query_params = {}
        path_params = {}
        
        path_params["actionName"] = actionName
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/devices/{deviceID}")
    async def getDevice(deviceID: int, viewVersion: Optional[str] = Query(None)):
        """
        Get device object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        if viewVersion is not None:
            query_params["viewVersion"] = viewVersion
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/devices/{deviceID}")
    async def modifyDevice(deviceID: int, request_data: dict = Body(...)):
        """
        Modify device
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/devices/{deviceID}")
    async def delDevice(deviceID: int):
        """
        Delete device
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/slave/{uuid}/api/devices/{deviceID}")
    async def delDeviceProxy(uuid: str, deviceID: int):
        """
        Delete device using master as a proxy for slave
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/slave/{uuid}/api/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["uuid"] = uuid
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/devices/{deviceID}/action/{actionName}")
    async def callAction(deviceID: int, actionName: str, request_data: dict = Body(...)):
        """
        Call action on given device
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/devices/{deviceID}/action/{actionName}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        path_params["actionName"] = actionName
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/devices/action/{timestamp}/{id}")
    async def deleteDelayedAction(timestamp: int, id: int):
        """
        Delete delayed action
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/devices/action/{timestamp}/{id}"
        query_params = {}
        path_params = {}
        
        path_params["timestamp"] = timestamp
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/slave/{uuid}/api/devices/{deviceID}/action/{actionName}")
    async def callActionProxySlave(uuid: str, deviceID: int, actionName: str, request_data: dict = Body(...)):
        """
        Call action using master as a proxy for slave
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/slave/{uuid}/api/devices/{deviceID}/action/{actionName}"
        query_params = {}
        path_params = {}
        
        path_params["uuid"] = uuid
        path_params["deviceID"] = deviceID
        path_params["actionName"] = actionName
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/uiDeviceInfo")
    async def getUIDeviceInfo(roomId: Optional[int] = Query(None), type_param: Optional[str] = Query(None), selectors: Optional[str] = Query(None), source: Optional[str] = Query(None), visible: Optional[str] = Query(None), classification: Optional[str] = Query(None)):
        """
        Get device info
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/uiDeviceInfo"
        query_params = {}
        path_params = {}
        
        if roomId is not None:
            query_params["roomId"] = roomId
        if type_param is not None:
            query_params["type"] = type_param
        if selectors is not None:
            query_params["selectors"] = selectors
        if source is not None:
            query_params["source"] = source
        if visible is not None:
            query_params["visible"] = visible
        if classification is not None:
            query_params["classification"] = classification
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/devices/hierarchy")
    async def getDeviceTypeHierarchy():
        """
        Get device type hierarchy
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/devices/hierarchy"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from additionalInterfaces.json

    @app.get("/api/additionalInterfaces")
    async def getAdditionalInterfaces(deviceId: int = Query(...)):
        """
        Get list of all additional interfaces
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/additionalInterfaces"
        query_params = {}
        path_params = {}
        
        if deviceId is not None:
            query_params["deviceId"] = deviceId
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/additionalInterfaces/{interfaceName}")
    async def getDevicesIdByAdditionalInterfaceName(interfaceName: str):
        """
        Get list of all devices id which can add this additional interface.
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/additionalInterfaces/{interfaceName}"
        query_params = {}
        path_params = {}
        
        path_params["interfaceName"] = interfaceName
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from fti.json

    @app.get("/api/fti/v2")
    async def getFTIModel():
        """
        Get FTI model
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/fti/v2"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/fti/v2/changeStep/{step}")
    async def setFTIStep(step: str):
        """
        Set current FTI step
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/fti/v2/changeStep/{step}"
        query_params = {}
        path_params = {}
        
        path_params["step"] = step
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/fti/v2/finish")
    async def finishFTI():
        """
        Finish FTI
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/fti/v2/finish"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/fti/v2/reset")
    async def resetFTI():
        """
        Reset FTI
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/fti/v2/reset"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from systemStatus.json

    @app.get("/api/service/systemStatus")
    async def systemStatus(lang: str = Query(...), _: int = Query(...)):
        """
        System status
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/systemStatus"
        query_params = {}
        path_params = {}
        
        if lang is not None:
            query_params["lang"] = lang
        if _ is not None:
            query_params["_"] = _
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/service/systemStatus")
    async def setSystemStatus(lang: str = Query(...), request_data: dict = Body(...)):
        """
        Set system status
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/service/systemStatus"
        query_params = {}
        path_params = {}
        
        if lang is not None:
            query_params["lang"] = lang
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/service/restartServices")
    async def clearError(lang: str = Query(...), request_data: dict = Body(...)):
        """
        Clear error
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/service/restartServices"
        query_params = {}
        path_params = {}
        
        if lang is not None:
            query_params["lang"] = lang
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from linkedDevices.json

    @app.get("/api/linkedDevices/v1/devices")
    async def getLinkedDevices(type_param: Optional[str] = Query(None)):
        """
        Get information about linked devices
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/linkedDevices/v1/devices"
        query_params = {}
        path_params = {}
        
        if type_param is not None:
            query_params["type"] = type_param
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/linkedDevices/v1/devices")
    async def createLinkedDevice(request_data: dict = Body(...)):
        """
        Create new linked device
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/linkedDevices/v1/devices"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/linkedDevices/v1/providers")
    async def getLinkedDevicesProviders():
        """
        Get linked devices providers list and information about available links
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/linkedDevices/v1/providers"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/linkedDevices/v1/devices/{deviceID}")
    async def getLinkedDevice(deviceID: int):
        """
        Get information about linked device
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/linkedDevices/v1/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/linkedDevices/v1/devices/{deviceID}")
    async def updateLinkedDevice(deviceID: int, request_data: dict = Body(...)):
        """
        Update linked device
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/linkedDevices/v1/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/linkedDevices/v1/devices/{deviceID}")
    async def deleteLinkedDevice(deviceID: int):
        """
        Delete existing linked device
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/linkedDevices/v1/devices/{deviceID}"
        query_params = {}
        path_params = {}
        
        path_params["deviceID"] = deviceID
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/linkedDevices/v1/inputDevices")
    async def getLinkedDevicesInputs():
        """
        Get id list of all input devices
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/linkedDevices/v1/inputDevices"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from home.json

    @app.get("/api/home")
    async def getHomeInfo():
        """
        Get home info
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/home"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/home")
    async def updateHomeInfo(request_data: dict = Body(...)):
        """
        Update home info
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/home"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from passwordForgotten.json

    @app.get("/api/passwordForgotten")
    async def passwordForgotten(login: str = Query(...), lang: Optional[str] = Query(None)):
        """
        Password Forgotten
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/passwordForgotten"
        query_params = {}
        path_params = {}
        
        if login is not None:
            query_params["login"] = login
        if lang is not None:
            query_params["lang"] = lang
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from gatewayConnection.json

    @app.get("/api/service/discovery/resolve/{type}/{value}")
    async def discoveryResolve(type: str, value: str, options: Optional[str] = Query(None)):
        """
        Gateway connection resolve
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/discovery/resolve/{type}/{value}"
        query_params = {}
        path_params = {}
        
        path_params["type"] = type
        path_params["value"] = value
        if options is not None:
            query_params["options"] = options
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/discovery/search")
    async def discoverySearch(filterMap: Optional[str] = Query(None)):
        """
        Discovery search
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/discovery/search"
        query_params = {}
        path_params = {}
        
        if filterMap is not None:
            query_params["filterMap"] = filterMap
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/resolve/{type}/{value}")
    async def discoveryGateway(type: str, value: str):
        """
        Discover gateway in the network by serial number or ip
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/resolve/{type}/{value}"
        query_params = {}
        path_params = {}
        
        path_params["type"] = type
        path_params["value"] = value
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/gateway/role")
    async def getGatewayRole():
        """
        Gateway role
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/gateway/role"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/service/gateway/role")
    async def switchGatewayRole(request_data: dict = Body(...)):
        """
        Switch role
        Switch role from master to slave.
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/service/gateway/role"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/slaves")
    async def getSlavesList():
        """
        Get list of slaves
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/slaves"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/service/slaves")
    async def addNewSlave(request_data: dict = Body(...)):
        """
        
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/service/slaves"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/slaves/{id}/password")
    async def slavePassword(id: str):
        """
        Slave login and password (Base64 encoded)
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/slaves/{id}/password"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.put("/api/service/slaves/{id}")
    async def replaceSlave(id: str, request_data: dict = Body(...)):
        """
        Replace slave
        
        """
        # Prepare data for Lua hook
        method = "PUT"
        path = "/api/service/slaves/{id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/service/slaves/{id}")
    async def deleteSlave(id: str):
        """
        Delete slave
        
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/service/slaves/{id}"
        query_params = {}
        path_params = {}
        
        path_params["id"] = id
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/service/slaves/{serialOrId}/ip")
    async def getSlaveIp(serialOrId: str, rediscover: Optional[str] = Query(None)):
        """
        Get slave IP address
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/service/slaves/{serialOrId}/ip"
        query_params = {}
        path_params = {}
        
        path_params["serialOrId"] = serialOrId
        if rediscover is not None:
            query_params["rediscover"] = rediscover
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/remoteGateway/verifyGateway")
    async def verifyGateway(ip: Optional[str] = Query(None), serial: Optional[str] = Query(None)):
        """
        Verify the serial of given gateway
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/remoteGateway/verifyGateway"
        query_params = {}
        path_params = {}
        
        if ip is not None:
            query_params["ip"] = ip
        if serial is not None:
            query_params["serial"] = serial
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from userActivity.json

    @app.get("/api/userActivity")
    async def getUserActivity():
        """
        Get user activity list
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/userActivity"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from loginStatus.json

    @app.get("/api/loginStatus")
    async def getLoginStatus():
        """
        Get login status
        Produces different response when not logged in (optional parameters not included).
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/loginStatus"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/loginStatus")
    async def callLoginAction(action: str = Query(...), tosAccepted: Optional[str] = Query(None)):
        """
        Call login action
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/loginStatus"
        query_params = {}
        path_params = {}
        
        if action is not None:
            query_params["action"] = action
        if tosAccepted is not None:
            query_params["tosAccepted"] = tosAccepted
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from plugins.json

    @app.get("/api/plugins")
    async def getPlugins():
        """
        Get all plugins object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/callUIEvent")
    async def callUIEvent(deviceID: int = Query(...), elementName: str = Query(...), eventType: str = Query(...), value: Optional[str] = Query(None)):
        """
        Call UiEvent Action
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/callUIEvent"
        query_params = {}
        path_params = {}
        
        if deviceID is not None:
            query_params["deviceID"] = deviceID
        if elementName is not None:
            query_params["elementName"] = elementName
        if eventType is not None:
            query_params["eventType"] = eventType
        if value is not None:
            query_params["value"] = value
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/createChildDevice")
    async def createChildDevice(request_data: dict = Body(...)):
        """
        Create child device
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/createChildDevice"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/getView")
    async def getView(id: Optional[int] = Query(None), name: Optional[str] = Query(None), type_param: Optional[str] = Query(None), version: Optional[str] = Query(None)):
        """
        Get plugin view
        Get plugin view. Required parameters:
 * **id** - get plugin view by id 
 * **name**, **Accept** and **Accept-Language** - get plugin view by type, parameter **type** is optional.
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/getView"
        query_params = {}
        path_params = {}
        
        if id is not None:
            query_params["id"] = id
        if name is not None:
            query_params["name"] = name
        if type_param is not None:
            query_params["type"] = type_param
        if version is not None:
            query_params["version"] = version
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/installed")
    async def getInstalledPlugins():
        """
        Get installed plugins
        Get installed plugins
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/installed"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/installed")
    async def installPlugin(type_param: Optional[str] = Query(None)):
        """
        Install plugin
        Install plugin. Valid only for HC2. In HC3 each plugin is being installed during the adding.
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/installed"
        query_params = {}
        path_params = {}
        
        if type_param is not None:
            query_params["type"] = type_param
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.delete("/api/plugins/installed")
    async def deletePlugin(type_param: Optional[str] = Query(None)):
        """
        Delete plugin
        Delete plugin
        """
        # Prepare data for Lua hook
        method = "DELETE"
        path = "/api/plugins/installed"
        query_params = {}
        path_params = {}
        
        if type_param is not None:
            query_params["type"] = type_param
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/interfaces")
    async def interfaces(request_data: dict = Body(...)):
        """
        Add or remove interfaces
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/interfaces"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/ipCameras")
    async def getIPCameras():
        """
        Get all IP cameras object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/ipCameras"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/publishEvent")
    async def pluginPublishEvent(request_data: dict = Body(...)):
        """
        Publish event
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/publishEvent"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/restart")
    async def restartPlugin(request_data: dict = Body(...)):
        """
        Restart plugin
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/restart"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/types")
    async def getPluginsTypes():
        """
        Get information about plugins in system
        Get information about plugins in system
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/types"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/updateProperty")
    async def updateProperty(request_data: dict = Body(...)):
        """
        Update property
        
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/updateProperty"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.post("/api/plugins/updateView")
    async def updateView(request_data: dict = Body(...)):
        """
        Update plugin view
        Update plugin view
        """
        # Prepare data for Lua hook
        method = "POST"
        path = "/api/plugins/updateView"
        query_params = {}
        path_params = {}
        
        body_data = request_data

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

    @app.get("/api/plugins/v2")
    async def getPluginsV2():
        """
        Get all plugins object
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/api/plugins/v2"
        query_params = {}
        path_params = {}
        
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        # Endpoints from fibaro/json.json

    @app.get("/fibaro/json/{parametersTemplate}.json")
    async def getDeviceParametersTemplate(parametersTemplate: str):
        """
        Get device parameters template
        
        """
        # Prepare data for Lua hook
        method = "GET"
        path = "/fibaro/json/{parametersTemplate}.json"
        query_params = {}
        path_params = {}
        
        path_params["parametersTemplate"] = parametersTemplate
        body_data = None

        # Call Fibaro API hook in Lua
        try:
            result = interpreter.lua.globals()._PY.fibaro_api_hook(
                method, path, path_params, query_params, body_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in Fibaro API hook for {method} {path}: {e}")
            return {"error": "Internal server error", "message": str(e)}

        logger.info(f"Created 194 Fibaro API endpoints")
