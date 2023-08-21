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

import gradio as gr
import os
from modules import script_callbacks


def read_last_n_lines(file_path, n):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            last_n_lines = lines[-n:]
            return ''.join(last_n_lines)
    else:
        return "File not found."


def log_content():
    last_n_lines = read_last_n_lines(f'{current_directory}/../../../webui.log', 100)
    print('Refreshed log')
    return last_n_lines


def run_view():
    btn = gr.Button("Refresh")
    log_string = gr.Textbox(label='Log', lines=100)
    btn.click(log_content, outputs=[log_string])


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as mylogs_interface:
        components = {}
        with gr.Column():
            run_view()
    return [(mylogs_interface, "mylogs", "mylogs_interface")]


def on_ui_settings():
    pass


print('Registering log tab')
script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_ui_settings(on_ui_settings)
