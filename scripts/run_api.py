import sys, os

basedirs = [os.getcwd()]
if 'google.colab' in sys.modules:
    basedirs.append(
        '/content/gdrive/MyDrive/sd/stable-diffusion-webui')  # hardcode as TheLastBen's colab seems to be the primal source

for basedir in basedirs:
    deforum_paths_to_ensure = [basedir + '/extensions/sd-webui-clear-object/scripts', basedir]

    for deforum_scripts_path_fix in deforum_paths_to_ensure:
        if not deforum_scripts_path_fix in sys.path:
            sys.path.extend([deforum_scripts_path_fix])

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)

import logging
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)


def get_clearobject_version():
    return '1.0'


def t2v_api(_, app: FastAPI):
    logger.debug(f"clearobj extension for auto1111 webui")
    logger.debug(f"Git commit: {get_clearobject_version()}")
    logger.debug("Loading clearobj API endpoints")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.get("/clearobj/api_version")
    async def clearobj_api_version():
        return JSONResponse(content={"version": '1.0'})

    @app.get("/clearobj/version")
    async def clearobj_version():
        return JSONResponse(content={"version": get_clearobject_version()})

    @app.post("/clearobj/run")
    async def clearobj_run(image: UploadFile = File(...), mask: UploadFile = File(...)):
        print(f"SAM API /sam/clearobj-run received")

        origin_image_bytes = await image.read()
        mask_image_bytes = await  mask.read()

        print(f"origin_image_bytes: {len(origin_image_bytes)}")
        print(f"mask_image_bytes: {len(mask_image_bytes)}")

        return JSONResponse(content={"image_name": image.filename, "mask_name": mask.filename})


try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(t2v_api)
    logger.debug("SD-Webui clearobj API layer loaded")
except ImportError:
    logger.debug("Unable to import script callbacks.XXX")
