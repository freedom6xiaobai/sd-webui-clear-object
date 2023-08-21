# import sys, os
#
# basedirs = [os.getcwd()]
# if 'google.colab' in sys.modules:
#     basedirs.append(
#         '/content/gdrive/MyDrive/sd/stable-diffusion-webui')  # hardcode as TheLastBen's colab seems to be the primal source
#
# for basedir in basedirs:
#     deforum_paths_to_ensure = [
#         basedir + '/extensions/sd-webui-clear-object/scripts',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/utils',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/sttn',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/bin',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/models',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/models/ade20k',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/saicinpainting',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/saicinpainting/evaluation',
#         basedir + '/extensions/sd-webui-clear-object/scripts/Inpaint_Anything/lama/saicinpainting/training',
#         basedir + '/extensions/sd-webui-clear-object/scripts/CodeFormer',
#         basedir + '/extensions/sd-webui-clear-object/scripts/insight_face',
#         basedir + '/extensions/sd-webui-clear-object/scripts/segment_anything',
#
#         basedir,
#     ]
#
#     for deforum_scripts_path_fix in deforum_paths_to_ensure:
#         if not deforum_scripts_path_fix in sys.path:
#             sys.path.extend([deforum_scripts_path_fix])
#
# current_directory = os.path.dirname(os.path.abspath(__file__))
# if current_directory not in sys.path:
#     sys.path.append(current_directory)
#
# print(f'clearobj_any_api_current_directory: {current_directory}')
#
# import numpy as np
# from PIL import Image
# import time
# from copy_www.generate_sources import copy_file_to_www
# from Inpaint_Anything.utils.utils import save_array_to_img, dilate_mask, show_mask, show_points
# from Inpaint_Anything.lama_inpaint import build_lama_model, inpaint_img_with_builded_lama, inpaint_img_with_lama
# from Inpaint_Anything.stable_diffusion_inpaint import fill_img_with_sd, replace_img_with_sd
# from Inpaint_Anything.segment_anything.segment_anything import SamPredictor, sam_model_registry
# from modules.shared import opts, devices, state
#
#
# devices.torch_gc()
# device = devices.get_optimal_device()
# # build models
# model = {}
# # build the sam model
# model_type = "vit_h"
# ckpt_p = f'{current_directory}/Inpaint_Anything/pretrained_models/sam_vit_h_4b8939.pth'
# model_sam = sam_model_registry[model_type](checkpoint=ckpt_p)
# model_sam.to(device=device)
# model['sam'] = SamPredictor(model_sam)
#
# # build the lama model
# lama_config = f'{current_directory}/Inpaint_Anything/lama/configs/prediction/default.yaml'
# lama_ckpt = f'{current_directory}/Inpaint_Anything/pretrained_models/big-lama'
# model['lama'] = build_lama_model(lama_config, lama_ckpt, device=device)
# print('inpaint anything models are built.')
#
#
# # 初始化根目录
# def init_finder():
#     ROOT_PATH = f'{current_directory}/../../../'
#     print(f'clear object ROOT_PATH: {ROOT_PATH}')
#     clearobj_output = os.path.join(ROOT_PATH, 'outputs/clearobjc')
#     print(f'clear object clearobj_output: {clearobj_output}')
#     os.makedirs(clearobj_output, exist_ok=True)
#     return clearobj_output
#
#
# # 清除物体
# def get_inpainted_clear_img(image_file, masks_file):
#     try:
#         print('inpaint anything Start to run the server.1')
#
#         # 读取图片
#         img_o = Image.open(image_file.file).convert("RGBA")
#         img_list_np = np.array(img_o)
#         image_np = img_list_np.astype(np.uint8)
#         image_np_rgb = image_np[..., :3]
#         print(f'image_np: {image_np.shape}')
#         print(f'image_np_rgb: {image_np_rgb.shape}')
#
#         # 读取mask
#         mask_o = Image.open(masks_file.file).convert("L")
#         mask_list_np = np.array(mask_o)
#         mask_np = mask_list_np.astype(np.uint8)
#         print(f'mask_np: {mask_np.shape}')
#
#         print('run the server.2')
#
#         clearobj_output = init_finder()
#         fileName = time.strftime('%Y%m%d%H%M%S')
#         output_file_name = f'{fileName}_mask_inpainted.png'
#         img_output_rm_path = f'{clearobj_output}/{output_file_name}'
#         img_inpainted = inpaint_img_with_lama(image_np_rgb, mask_np, lama_config, lama_ckpt, device=device)
#         save_array_to_img(img_inpainted, img_output_rm_path)
#
#         png = copy_file_to_www(img_output_rm_path)
#         if png is not None:
#             return png
#         return None
#     except Exception as e:
#         print(f'error: {e}')
#         return None
#
#
# # 替换物体
# def get_inpainted_clear_img_fill(image_file, masks_file, prompt):
#     try:
#         print('inpaint anything Start to run the server.1')
#         # 读取图片
#         img_o = Image.open(image_file.file).convert("RGBA")
#         img_list_np = np.array(img_o)
#         image_np = img_list_np.astype(np.uint8)
#         image_np_rgb = image_np[..., :3]
#         print(f'image_np: {image_np.shape}')
#         print(f'image_np_rgb: {image_np_rgb.shape}')
#
#         # 读取mask
#         mask_o = Image.open(masks_file.file).convert("L")
#         mask_list_np = np.array(mask_o)
#         mask_np = mask_list_np.astype(np.uint8)
#         print(f'mask_np: {mask_np.shape}')
#
#         print('run the server.2')
#         # 替换物体
#         clearobj_output = init_finder()
#
#         print(f'prompt: {prompt}')
#         fileName = time.strftime('%Y%m%d%H%M%S')
#         output_file_name = f'{fileName}_mask_inpainted_fill.png'
#         img_output_rm_path = f'{clearobj_output}/output/{output_file_name}'
#         img_filled = fill_img_with_sd(image_np_rgb, mask_np, prompt, device=device)
#         print('run the server.4')
#         print(f'img_filled: {img_filled.shape}')
#         save_array_to_img(img_filled, img_output_rm_path)
#
#         png = copy_file_to_www(img_output_rm_path)
#         if png is not None:
#             return png
#         return None
#     except Exception as e:
#         print(f'error: {e}')
#         return None
