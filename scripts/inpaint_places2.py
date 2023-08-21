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

import cv2
import numpy as np
import tensorflow as tf
import neuralgym as ng
from inpaint_model import InpaintCAModel
from PIL import Image
import io
import time
import obj_constant

# run places2 模型 擦除效果
async def generate_places2_256_run(image_file, mask_file):
    for basedir in basedirs:
        sys.path.extend([
            basedir + '/scripts',
            basedir + '/extensions/sd-webui-clear-object/scripts',
        ])
    print('clear object Start to run the server.')
    clearobj_output = obj_constant.init_finder()

    fileName = time.strftime('%Y%m%d%H%M%S')
    image_file_new = f'{clearobj_output}/image_{fileName}.png'
    mask_file_new = f'{clearobj_output}/mask_{fileName}.png'
    output_file_new = f'{clearobj_output}/places2_256_outputs_{fileName}.png'

    try:
        # 原始图片
        image_file_bytes = await image_file.read()
        Image.open(io.BytesIO(image_file_bytes)).save(image_file_new)
        is_image_file_new = open(image_file_new, "r")
        print(f'clear object --- 0 {is_image_file_new}')

        # mask图片
        mask_file_bytes = await mask_file.read()
        Image.open(io.BytesIO(mask_file_bytes)).save(mask_file_new)
        is_mask_file_new = open(mask_file_new, "r")
        print(f'clear object --- 0 {is_mask_file_new}')

        print('clear object --- 0')

        # 读取配置信息
        FLAGS = ng.Config(f'{current_directory}/inpaint.yml')

        # 加载模型
        model = InpaintCAModel()
        image = cv2.imread(image_file_new)
        mask = cv2.imread(mask_file_new)
        # mask = cv2.resize(mask, (0,0), fx=0.5, fy=0.5)

        print('clear objec --- 1')

        assert image.shape == mask.shape

        h, w, _ = image.shape
        grid = 8
        image = image[:h // grid * grid, :w // grid * grid, :]
        mask = mask[:h // grid * grid, :w // grid * grid, :]
        print('Shape of image: {}'.format(image.shape))

        image = np.expand_dims(image, 0)
        mask = np.expand_dims(mask, 0)
        input_image = np.concatenate([image, mask], axis=2)

        print('clear objec --- 2')

        sess_config = tf.compat.v1.ConfigProto()
        sess_config.gpu_options.allow_growth = True
        with tf.compat.v1.Session(config=sess_config) as sess:
            input_image = tf.constant(input_image, dtype=tf.float32)
            output = model.build_server_graph(FLAGS, input_image)
            output = (output + 1.) * 127.5
            output = tf.reverse(output, [-1])
            output = tf.saturate_cast(output, tf.uint8)
            # load pretrained model
            vars_list = tf.compat.v1.get_collection(tf.compat.v1.GraphKeys.GLOBAL_VARIABLES)
            assign_ops = []
            for var in vars_list:
                vname = var.name
                from_name = vname
                checkpoint_dir = f'{current_directory}/model_logs/release_places2_256'
                var_value = tf.train.load_variable(checkpoint_dir, from_name)
                assign_ops.append(tf.compat.v1.assign(var, var_value))
            sess.run(assign_ops)
            print('Model loaded.')
            print('clear objec --- 3')
            result = sess.run(output)

            # 保存结果
            cv2.imwrite(output_file_new, result[0][:, :, ::-1])
            print('output:1 {}'.format(output_file_new))
            print('clear objec --- 4')

        print('clear objec --- 5')
    finally:
        print('clear objec --- 6 - finish')

    return output_file_new
