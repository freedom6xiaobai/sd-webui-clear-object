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
from inpaint_places2 import generate_places2_256_run
from copy_www.generate_sources import copy_file_to_www
# from inpaint_any_api import get_inpainted_clear_img, get_inpainted_clear_img_fill

logger = logging.getLogger(__name__)

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)

print(f"clearobj_current_directory: {current_directory}")


def get_clearobject_version():
    return '1.0'


def clearobjc_api(_, app: FastAPI):
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

    # 擦除 places2模型
    @app.post("/clearobj/inpaint_erase_places2")
    async def inpaint_erase_places2(image: UploadFile = File(...), mask: UploadFile = File(...)):
        print(f"SAM API /sam/inpaint_erase_places2-run received")
        output_image = await generate_places2_256_run(image, mask)
        png = copy_file_to_www(output_image)
        if png is not None:
            return JSONResponse(content={"image": png})
        else:
            return JSONResponse(content={"error": 'copy error failed'}, status_code=500)

    # # 擦除 lama模型
    # @app.post("/clearobj/inpaint_erase_lama")
    # async def inpaint_erase_lama(image: UploadFile = File(...), mask: UploadFile = File(...)):
    #     print(f"SAM API /sam/inpaint_erase_lama-run received")
    #     generate_png = get_inpainted_clear_img(image, mask)
    #     if generate_png is not None:
    #         return JSONResponse(content={"image": generate_png})
    #     else:
    #         return JSONResponse(content={"error": f'error failed'}, status_code=500)
    #
    # # 擦除 替换物体 lama模型
    # @app.post("/clearobj/inpaint_erase_lama_fill")
    # async def inpaint_erase_lama_fill(image: UploadFile = File(...), mask: UploadFile = File(...),
    #                                   prompt: str = ''):
    #     print(f"SAM API /sam/inpaint_erase_lama_fill-run received")
    #     generate_png = get_inpainted_clear_img_fill(image, mask, prompt, )
    #     if generate_png is not None:
    #         return JSONResponse(content={"image": generate_png})
    #     else:
    #         return JSONResponse(content={"error": f'error failed'}, status_code=500)


try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(clearobjc_api)
    logger.debug("SD-Webui clearobj API layer loaded")
except ImportError:
    logger.debug("Unable to import script callbacks.XXX")
