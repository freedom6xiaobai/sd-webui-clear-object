import sys, os

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)


# 初始化根目录
def init_finder():
    ROOT_PATH = f'{current_directory}/../../../'
    print(f'clear object ROOT_PATH: {ROOT_PATH}')
    clearobj_output = os.path.join(ROOT_PATH, 'outputs/clearobjc')
    print(f'clear object clearobj_output: {clearobj_output}')
    os.makedirs(clearobj_output, exist_ok=True)
    return clearobj_output
