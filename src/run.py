import base64
import datetime
import io
import json
import os
import random
import urllib.request
import uuid
from decouple import config
from flask import Flask, request, url_for, send_from_directory
from flask_cors import CORS
from config.flask import *
from helpers.github import Github
from helpers.transforms import get_random_id
from core.compiler import Compiler
from storage.redis_store import RedisStore
import requests
from urllib.parse import quote, urlencode

github_api = Github(config('GITHUB_TOKEN', default='no_key'))

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={r"/*": {"origins": "*"}})
    return app


def init():
    debug = config('DEBUG', default=True, cast=bool)
    get_config_mode = 'Debug' if debug else 'Production'

    try:
        # Load the configuration using the default values
        app_config = config_dict[get_config_mode.capitalize()]
    except KeyError:
        raise Exception('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

    app = create_app(app_config)
    return app, app_config


if __name__ == "__main__":
    app, config = init()


    @app.route("/")
    def index():
        return "up"

    @app.route("/project/list")
    def get_all_projects():
        return {
            "status": True,
            "projects": [{
                "name": "crunch",
                "id": 1
            }]
        }

    @app.route("/project/save", methods=["GET", "POST"])
    def save_project():
        project_url = request.json.get("url")
        project_id = get_random_id()

        project_url = github_api.get_project(project_url)
        new_tree = github_api.fetch_files(project_url, file="")
        # save reference to project
        RedisStore.set(project_id, new_tree)

        return {
            "status": True,
            "project": new_tree
        }


    @app.route("/project/")
    def get_project():
        project_id = request.json.get("id")
        project = RedisStore.get(project_id)
        if not project:
            return {
                "status": False,
                "project": None
            }

        # obtain

        return {
            "status": True,
            "project": project
        }





    # @app.route("/test")
    # def test():
    #     generated_image_id = "test_example"
    #     canvas_size = 1024
    #     prompt = "A valley full of red flowers with a waterfall in the background, hyper realistic, artstation, award-winning"
    #
    #     result0 = automatic.txt2img(
    #         prompt=prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=canvas_size,
    #         height=canvas_size,
    #         cfg_scale=7.5,
    #         # seed=seed_value,
    #         denoising_strength=0.75,
    #         steps=20,
    #     )
    #
    #     final_layer = result0.image.convert("RGBA")
    #     final_layer.save(config.UPLOAD_FOLDER + f"/{generated_image_id}.png")
    #     return {
    #         "url": config.UPLOAD_FOLDER + f"/{generated_image_id}.png"
    #     }
    #
    #
    # # we need to make an endpoint that receives a
    # @app.route("/api/product-design/", methods=["POST"])
    # def product_design():
    #     print(request.files)
    #     print(request.form)
    #     image = request.files["image"]
    #     scene_prompt = request.form["prompt"]
    #
    #     image = Image.open(image).convert("RGB").resize((512, 512))
    #     image.save(config.UPLOAD_FOLDER + "/product_design_orig.png")
    #
    #     image_desc = automatic.interrogate(image=image).info
    #     print(image_desc)
    #     subject = image_desc.split(",")[0]
    #     image_desc = scene_prompt.replace("{subject}", subject) + ", " + ",".join(image_desc.split(",")[-3:])
    #     print(image_desc)
    #
    #     image_new_mask = automatic.remove_background(image).image
    #     image_new_mask.save(config.UPLOAD_FOLDER + "/product_design_rem.png")
    #     # image_segmentation = automatic.auto_sam(image)
    #     # print(image_segmentation)
    #     # image_segmentation.save(config.UPLOAD_FOLDER + "/product_design_segm.png")
    #
    #     # image_mask = automatic.depth_to_grayscale(automatic.depth(image).image).convert("L")
    #     # image_mask = image_mask.filter(ImageFilter.GaussianBlur(radius=5))
    #     # image_mask = image_mask.filter(
    #     #     ImageFilter.MaxFilter(size=11)
    #     #     # ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
    #     # )
    #     # # image_mask = ImageOps.posterize(image_mask, 2)
    #     # image_mask = ImageOps.autocontrast(image_mask, cutoff=20)
    #     #
    #     # image_mask_blur = image_mask.filter(ImageFilter.GaussianBlur(radius=20))
    #     # image_mask_blur = ImageOps.autocontrast(image_mask_blur, cutoff=20)
    #     #
    #     # image_mask = ImageChops.multiply(image_mask_blur, image_mask)
    #     # image_mask = ImageOps.autocontrast(image_mask, cutoff=30)
    #     # image_mask = image_mask.filter(ImageFilter.SHARPEN)
    #     # image_mask = image_mask.filter(ImageFilter.SHARPEN)
    #     # image_mask.save(config.UPLOAD_FOLDER + "/product_design_mask.png")
    #
    #     # print("Show extrema of the image for thresholding purposes", image_mask.b)
    #     # print("Mask image mode", image_mask)
    #     # image = image.convert("RGBA")
    #     edge_base = image.filter(ImageFilter.EMBOSS).convert("L").convert("RGB")
    #     edge_base.save(config.UPLOAD_FOLDER + "/product_design_edge.png")
    #
    #
    #     image_base = automatic.img2img(
    #         images=[edge_base],
    #         prompt=scene_prompt,
    #         seed_resize_from_h=image.width,
    #         seed_resize_from_w=image.height,
    #         width=image.width,
    #         height=image.height,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=8,
    #         denoising_strength=0.8,
    #         sampler_name="DPM++ 2M Karras",
    #         steps=25,
    #     ).image.convert("RGBA")
    #
    #     final_layer = Image.new("RGBA", image.size)
    #     print(final_layer.size, image_base.size)
    #     final_layer = Image.alpha_composite(final_layer, image_base)
    #     image = image.convert("RGBA")
    #     image.putalpha(image_new_mask)
    #     final_layer = Image.alpha_composite(final_layer, image).convert("RGB")
    #
    #     image = automatic.img2img(
    #         images=[final_layer],
    #         mask_image=image_new_mask,
    #         # mask_blur=3,
    #         inpainting_fill=2,
    #         inpainting_mask_invert=1,
    #         inpaint_full_res=False,
    #         prompt=scene_prompt,
    #         # seed=seed_value,
    #         seed_resize_from_h=image.width,
    #         seed_resize_from_w=image.height,
    #         width=image.width,
    #         height=image.height,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=8,
    #         denoising_strength=0.8,
    #         sampler_name="DPM++ 2M Karras",
    #         # initial_noise_multiplier=0.0,
    #         # cfg_scale=6,
    #         # denoising_strength=0.55,
    #         # initial_noise_multiplier=0.95,
    #         steps=25,
    #         # cfg_scale=5,
    #         # denoising_strength=0.2,
    #         # initial_noise_multiplier=0.3
    #     ).image
    #
    #     # image.putalpha(image_mask)
    #
    #     image.save(config.UPLOAD_FOLDER + "/product_design.png")
    #     print("This is the image", image)
    #
    #     # if image:
    #
    #     # if image:
    #     #     with urllib.request.urlopen(image) as image_file:
    #     #         data = image_file.read()
    #     #         data = Image.open(BytesIO(data))
    #     #         print(data)
    #     #
    #     return {
    #         "status": "ok"
    #     }
    #
    #
    # @app.route("/api/search/<term>")
    # def lexica(term):
    #     logger.debug(f"term {term}")
    #
    #     search_params = urlencode({
    #         "q": term
    #     })
    #
    #     lexica_data = requests.get(f"https://lexica.art/api/v1/search?{search_params}")
    #
    #     if lexica_data.status_code != 200:
    #         return {
    #             "status": False,
    #             "msg": "No examples available"
    #         }
    #
    #     lexica_data = lexica_data.json()
    #     prompts = [lexica_elem.get("prompt") for lexica_elem in lexica_data.get("images", [])]
    #     return {
    #         "status": True,
    #         "data": prompts
    #     }
    #
    #
    # @app.route("/api/prompts/")
    # def prompts():
    #     with open(f"{FLASK_PROJECT_DIR}/static/prompts.json") as prompts_json:
    #         prompts_data = json.load(prompts_json)
    #         return prompts_data
    #
    #
    # @app.route("/api/depth/", methods=["POST", ])
    # def depth():
    #     canvas_prompt = request.json.get("prompt")
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     seed_value = random.randint(0, 9999)
    #     generated_image_id = str(uuid.uuid4())
    #
    #     rel_canvas_width, rel_canvas_height = image_scale(canvas_width, canvas_height, GEN_SIZE)
    #     prompt = f"A photo of {canvas_prompt}"
    #     result0 = automatic.txt2img(
    #         prompt=prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=3,
    #         seed=seed_value,
    #         denoising_strength=0.6,
    #         steps=15
    #     )
    #
    #     original = result0.image
    #
    #     width, height = original.size
    #
    #     original_filename = f'/original_{generated_image_id}.png'
    #     original.save(config.UPLOAD_FOLDER + original_filename)
    #
    #     # settings = automatic.depth_opts()
    #     # logger.debug(f"GEN SETTINGS {settings}")
    #
    #     image0 = automatic.depth(original)
    #     # image0 = ImageOps.grayscale(image0.image)
    #     image0 = image0.image.resize(original.size)
    #     image0 = automatic.depth_to_grayscale(image0)
    #
    #     filename = f'/depth_{generated_image_id}.png'
    #     image0.save(config.UPLOAD_FOLDER + filename)
    #
    #     original = original.convert("RGBA")
    #     # image0 = image0.convert("L")
    #     original.putalpha(image0)
    #     or_with_depth = f"/canvas_{generated_image_id}.png"
    #     original.save(config.UPLOAD_FOLDER + or_with_depth)
    #
    #     # req = requests.post(url, json=body)
    #     # res = json.loads(req.text)
    #     # im = base64.b64decode(res['images'][0])
    #     # im = Image.open(io.BytesIO(im))
    #     # im.save(filename)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": or_with_depth,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/new-simple-gen/", methods=["POST", ])
    # def new_simple_gen():
    #     start_time = datetime.datetime.now()
    #     inputs = request.json.get("inputs")
    #     canvas_prompt = request.json.get("prompt")
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     seed_value = random.randint(0, 9999)
    #     generated_image_id = str(uuid.uuid4())
    #
    #     input_string = ' and '.join([f"{input_data.get('text')}" for input_data in inputs])
    #
    #     canvas_style = canvas_prompt.split(',')
    #     canvas_prompt = canvas_style[0]
    #     canvas_style = [] if len(canvas_style) == 0 else [style.strip() for style in canvas_style[1:]]
    #     canvas_style = ", ".join(canvas_style)
    #
    #     rel_canvas_width, rel_canvas_height = image_scale(canvas_width, canvas_height, GEN_SIZE)
    #
    #     prompt = f"A photo of {canvas_prompt}, {canvas_style}"
    #
    #     result0 = automatic.txt2img(
    #         prompt=prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=3,
    #         seed=seed_value,
    #         denoising_strength=0.6,
    #         steps=15
    #     )
    #
    #     image0 = result0.image.convert("RGBA").resize((canvas_width, canvas_height))
    #
    #     final_layer = Image.new("RGBA", (canvas_width, canvas_height))
    #     final_layer = Image.alpha_composite(final_layer, image0)
    #
    #     composite_mask = Image.new("L", (canvas_width, canvas_height))
    #     noise = Image.open(config.UPLOAD_FOLDER + "/noise.jpg").convert("RGBA").resize(
    #         (rel_canvas_width, rel_canvas_height))
    #     masking = Image.open(config.UPLOAD_FOLDER + "/masking_blur.png").convert("L")
    #
    #     for idx, input_data in enumerate(inputs):
    #         logger.debug(f"Input number {idx} is processed")
    #
    #         # in [{canvas_prompt}]
    #         # , a background with {canvas_prompt}
    #         image_prompt = f"{input_data.get('text')}, ({canvas_style})"
    #         # image_prompt = f"a photo of one centered {input_data.get('text')} very close to camera, {canvas_style}"
    #         # image_prompt = f"an image of one centered {input_data.get('text')} (very close to camera), black and white"
    #
    #         x = input_data.get("x")
    #         y = input_data.get("y")
    #         width = input_data.get("width", 512)
    #         height = input_data.get("height", 512)
    #
    #         rel_width, rel_height = image_scale(width, height, GEN_SIZE)
    #
    #         # image_background = image0.crop((x, y, x + width, y + height)).resize((rel_width, rel_height))
    #         # _, gen_mask = image_with_blur(image_background)
    #
    #         result = automatic.txt2img(
    #             # images=[image_background],
    #             # inpaint_full_res=False,
    #             # inpainting_fill=1,
    #             # mask_image=image_background_mask,
    #             # mask_blur=10,
    #             prompt=image_prompt,
    #             negative_prompt=f"{NEG_PROMPT}",
    #             width=rel_width,
    #             height=rel_height,
    #             seed_resize_from_h=rel_canvas_width,
    #             seed_resize_from_w=rel_canvas_height,
    #             seed=seed_value,
    #             cfg_scale=8,
    #             denoising_strength=0.9,
    #             # initial_noise_multiplier=0.8,
    #             steps=15,
    #             # n_iter=2
    #         )
    #
    #         image = result.image
    #         image_background_mask = automatic.depth(image)
    #         image_background_mask = automatic.depth_to_grayscale(image_background_mask.image)
    #         image_background_mask = ImageOps.invert(image_background_mask)
    #
    #         image = image.resize((width, height))
    #         masking_elem = masking.resize((width, height))
    #
    #         # image = image.convert("RGBA")
    #         # image.putalpha(masking_elem)
    #
    #         image_background_mask = image_background_mask.resize((width, height))
    #         image_background_mask = ImageChops.multiply(image_background_mask, masking_elem)
    #
    #         # image_background_mask.save(config.UPLOAD_FOLDER + f"/mask{idx}_{generated_image_id}.png")
    #         mask_layer = Image.new("L", (canvas_width, canvas_height), color=BLACK)
    #         bg_mask_enhance = ImageEnhance.Contrast(image_background_mask)
    #         image_background_mask = bg_mask_enhance.enhance(1.5)
    #
    #         mask_layer.paste(image_background_mask, (x, y))
    #         mask_layer.save(config.UPLOAD_FOLDER + f"/mask{idx}_{generated_image_id}.png")
    #
    #         # image_background_mask = image_background_mask.point(lambda p: 255 if p > 128 else 0)
    #         image_background_mask = ImageChops.multiply(image_background_mask, masking_elem)
    #         composite_mask.paste(image_background_mask, (x, y))
    #
    #         foreground = Image.new("RGBA", (canvas_width, canvas_height))
    #         foreground.paste(image, (x, y))
    #         foreground.putalpha(mask_layer)
    #         final_layer = Image.alpha_composite(final_layer, foreground)
    #
    #     composite_mask = composite_mask.convert("RGBA").resize((rel_canvas_width, rel_canvas_height))
    #     noise.putalpha(64)
    #
    #     # composite_mask = composite_mask.filter(ImageFilter.GaussianBlur(radius=20))
    #     logger.debug(f"Noise mode: {noise.mode} {noise.size} Composite: {composite_mask.mode} {composite_mask.size}")
    #
    #     # final_layer = color_dilution(final_layer)
    #     # final_layer = final_layer.convert(final_layer.mode)
    #     final_layer = final_layer.resize((rel_canvas_width, rel_canvas_height))
    #     final_layer.save(config.UPLOAD_FOLDER + f"/ncanvas_{generated_image_id}.png")
    #
    #     # get depth mask for final and compare to the composite mask
    #     final_layer_mask = automatic.depth(final_layer)
    #     final_layer_mask = automatic.depth_to_grayscale(final_layer_mask.image)
    #     bg_mask_enhance = ImageEnhance.Contrast(final_layer_mask)
    #     final_layer_mask = bg_mask_enhance.enhance(1.5)
    #     # final_layer_mask = ImageChops.multiply(final_layer_mask, composite_mask.convert("L"))
    #     final_layer_mask.save(config.UPLOAD_FOLDER + f"/allmask_{generated_image_id}.png")
    #     image0 = image0.resize((rel_canvas_width, rel_canvas_height))
    #     final_layer = Image.composite(image0, final_layer, final_layer_mask)
    #     # image0.putalpha(final_layer_mask)
    #
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #     composite_mask.save(config.UPLOAD_FOLDER + f"/mask_{generated_image_id}.png")
    #
    #     composite_mask = composite_mask.filter(ImageFilter.MinFilter(size=3))
    #     composite_mask = ImageChops.overlay(noise, composite_mask).convert("L")
    #
    #     # composite_mask = composite_mask.filter(ImageFilter.GaussianBlur(radius=3))
    #     composite_mask.save(config.UPLOAD_FOLDER + f"/nmask_{generated_image_id}.png")
    #
    #     description = f"{input_string} with {canvas_prompt} in the background, ({canvas_style})"
    #     logger.debug(f"NEW DESCRIPTION: {description}")
    #
    #     # final_result
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         mask_image=composite_mask,
    #         # mask_blur=3,
    #         inpainting_fill=2,
    #         inpainting_mask_invert=1,
    #         inpaint_full_res=False,
    #         prompt=f"A photo of {canvas_prompt}, ({canvas_style})",
    #         seed=seed_value,
    #         seed_resize_from_h=rel_canvas_width,
    #         seed_resize_from_w=rel_canvas_height,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=10,
    #         denoising_strength=0.8,
    #         initial_noise_multiplier=0.0,
    #         # cfg_scale=6,
    #         # denoising_strength=0.55,
    #         # initial_noise_multiplier=0.95,
    #         steps=20,
    #         # cfg_scale=5,
    #         # denoising_strength=0.2,
    #         # initial_noise_multiplier=0.3
    #     )
    #
    #     final_result = final_result.image.convert("RGBA")
    #
    #     # final_result = Image.alpha_composite(final_result, noise)
    #     # composite_mask = ImageOps.invert(composite_mask).filter(ImageFilter.GaussianBlur(radius=3))
    #     #
    #     # final_result = automatic.img2img(
    #     #     images=[final_result],
    #     #     mask_image=composite_mask,
    #     #     mask_blur=0,
    #     #     inpainting_fill=1,
    #     #     inpaint_full_res=False,
    #     #     seed_resize_from_h=rel_canvas_width,
    #     #     seed_resize_from_w=rel_canvas_height,
    #     #     prompt=final_prompt,
    #     #     seed=seed_value,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     cfg_scale=2,
    #     #     denoising_strength=0.3,
    #     #     # styles=["cybertech"],
    #     #     steps=10,
    #     # )
    #     #
    #     # final_result = final_result.image
    #
    #     # final_result = final_result.resize((canvas_width, canvas_height))
    #     filename_image = f"/final_{generated_image_id}.png"
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     logger.debug(f"Time elapsed: {(datetime.datetime.now() - start_time).seconds} seconds")
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/test/", methods=["POST", ])
    # def prompt_test():
    #     seed_value = random.randint(0, 9999)
    #     generated_image_id = str(uuid.uuid4())
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     prompt = "A tranquil mountain landscape unfolds beneath a vibrant, painted sky. The sun, in the style of impressionism, casts a warm, golden hue across the scene. Rolling hills covered in lush greenery lead to a majestic, snow-capped peak that stands proudly in the distance. In the foreground, a playful cat and a loyal dog share a peaceful moment of friendship. Their fluffy fur is captured with delicate brushstrokes, blending seamlessly with the dreamlike surroundings. This masterpiece conveys the essence of nature's beauty, drenched in the mesmerizing colors and light of impressionist art."
    #     # prompt="A magical fairytale landscape with rolling hills on the right side, a sparkling river on the left side, and a majestic castle in the distance. The sky is a soft pink and purple gradient, with fluffy clouds floating by. In the foreground, there is a lush forest with towering trees and a small pond. Butterflies flutter around and birds sing sweetly in the trees. The castle is surrounded by a moat and has turrets and spires reaching towards the sky. The landscape is filled with a sense of wonder and enchantment."
    #
    #     # prompt = "A gorgeous landscape of a mountain in the background with one black dog in the foreground, one white cat in the background and a majestic sun in the distance."
    #     # prompt = "Render an alternate reality where technology has surpassed nature, depicting a futuristic city with towering skyscrapers and advanced machines"
    #     rel_canvas_width, rel_canvas_height = image_scale(width=canvas_width, height=canvas_height, size=GEN_SIZE)
    #     # final_result = Image.new("RGBA", (rel_canvas_width, rel_canvas_height))
    #     final_result = automatic.txt2img(
    #         prompt=prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=7.5,
    #         denoising_strength=0.7,
    #         seed=seed_value,
    #         steps=30,
    #     )
    #
    #     final_result = final_result.image
    #     final_result = final_result.resize((canvas_width, canvas_height))
    #     final_result.save(config.UPLOAD_FOLDER + f"/final_{generated_image_id}.png")
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": f"/final_{generated_image_id}.png",
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/subject-image/", methods=["POST", "GET"])
    # def subject_image():
    #     generated_image_id = str(uuid.uuid4())
    #     inputs = request.json.get("inputs")
    #
    #     canvas_prompt = request.json.get("prompt", "")
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     if not canvas_width or not canvas_height:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     seed_value = random.randint(0, 9999)
    #
    #     # sort inputs here by depth
    #     inputs.sort(key=lambda x: x.get("depth", 0))
    #     # logger.debug(f"Sorted inputs {[elem.get('depth') for elem in inputs]}")
    #
    #     input_info = [(input_data.get("text"), input_data.get("weight", 0), input_data.get("depth", 0)) for input_data
    #                   in inputs if input_data.get("text")]
    #
    #     input_string = ', '.join(['a ' +
    #                               (text if depth != 0 else f"({text})")
    #                               for text, _, depth in input_info])
    #
    #     # first, construct the background from the overall prompt + the background inputs
    #     background_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == -1])
    #     # subject_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == 0])
    #     # foreground_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == 1])
    #
    #     final_prompt = f"A gorgeous photo of {canvas_prompt}, {input_string}"
    #
    #     # {background_text}
    #     background_prompt = f"A gorgeous photo of {canvas_prompt if canvas_prompt else background_text}"
    #
    #     # use the function to make a proportional canvas to given sizes
    #     rel_canvas_width, rel_canvas_height = image_scale(width=canvas_width, height=canvas_height, size=GEN_SIZE)
    #
    #     # extract subject images + create general mask
    #     final_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height), color=(255, 0, 0, 0))
    #     subject_mask = Image.new("L", (rel_canvas_width, rel_canvas_height), color="#000000")
    #     subject_mask_draw = ImageDraw.Draw(subject_mask)
    #
    #     rel_per_width = 1 / canvas_width * rel_canvas_width
    #     rel_per_height = 1 / canvas_height * rel_canvas_height
    #
    #     # select only the subject input and outpaint till it fills the canvas
    #     subject_input = [input_data for input_data in inputs if input_data.get("subject")][0]
    #     subject_image = data_uri_to_image(subject_input.get("subject"))
    #
    #     x = subject_input.get("x")
    #     y = subject_input.get("y")
    #     width = subject_input.get("width", canvas_width)
    #     height = subject_input.get("height", canvas_height)
    #
    #     rel_width = int(width * rel_per_width)
    #     rel_height = int(height * rel_per_height)
    #     rel_x = int(x * rel_per_width)
    #     rel_y = int(y * rel_per_height)
    #
    #     subject_width, subject_height = subject_image.size
    #     subject_ar = subject_width / subject_height
    #
    #     if subject_ar > 1:
    #         subject_width = rel_width
    #         subject_height = int(subject_width / subject_ar)
    #     else:
    #         subject_height = rel_height
    #         subject_width = int(subject_height * subject_ar)
    #
    #     subject_image = subject_image.resize((subject_width, subject_height))
    #     subject_x = ((rel_width - subject_width) // 2) + rel_x
    #     subject_y = ((rel_height - subject_height) // 2) + rel_y
    #
    #     # this is the important part: keep constructing the image around the subject and make the shape of the mask
    #     # smaller and smaller every time
    #     subject_mask_shape = get_bbox(subject_x, subject_y, subject_width, subject_height, 0.2)
    #     subject_mask_draw.rectangle(subject_mask_shape, fill="#ffffff")
    #     # final_layer.paste(subject_image, (subject_x, subject_y))
    #
    #     # description = automatic.interrogate(image=subject_image).info
    #     # subjects_style = [*description.split(",")[1:]]
    #     # subjects_style = [style.strip() for style in subjects_style]
    #     # subjects_style = ",".join(subjects_style)
    #
    #     diff_w = final_layer.size[0] - subject_image.size[0]
    #     diff_h = final_layer.size[1] - subject_image.size[1]
    #
    #     # final_result = subject_image.copy()
    #
    #     construction_masks = []
    #     for i in range(0, 3):
    #         subject_mask = Image.new("L", (rel_canvas_width, rel_canvas_height), color="#ffffff")
    #         subject_mask_shape = get_bbox(subject_x, subject_y, subject_width, subject_height, 0.045 * (i + 1))
    #         subject_mask_draw = ImageDraw.Draw(subject_mask)
    #         subject_mask_draw.rectangle(subject_mask_shape, fill="#000000")
    #         subject_mask = subject_mask.filter(ImageFilter.GaussianBlur(radius=10 * (i + 1)))
    #         # subject_mask.putalpha(255 * (3 - i))
    #         # subject_mask = subject_mask.convert("RGB").convert("L")
    #         subject_mask.save(config.UPLOAD_FOLDER + f"/mask{i}_{generated_image_id}.png")
    #         construction_masks.append(subject_mask)
    #
    #     alpha = subject_image.split()[-1]
    #
    #     # subject_mask_sm = ImageOps.invert(subject_mask)
    #     # subject_mask_sm = subject_mask_sm.filter(
    #     #     ImageFilter.GaussianBlur(radius=int(min(subject_width, subject_height) * 0.15)))
    #     #
    #     # subject_mask_sm.save(config.UPLOAD_FOLDER + f"/masksm_{generated_image_id}.png")
    #     #
    #     # subject_mask_lg = ImageOps.invert(subject_mask)
    #     # subject_mask_lg = subject_mask_lg.filter(
    #     #     ImageFilter.GaussianBlur(radius=int(min(subject_width, subject_height) * 0.1)))
    #     #
    #     # subject_mask_lg.save(config.UPLOAD_FOLDER + f"/masklg_{generated_image_id}.png")
    #
    #     final_result = Image.new("RGBA", (rel_canvas_width, rel_canvas_height))
    #     subject_image_blurred = subject_image.filter(ImageFilter.GaussianBlur(radius=20))
    #     subject_image_blurred = subject_image_blurred.resize((rel_canvas_width, rel_canvas_height))
    #     final_result.paste(subject_image_blurred)
    #     final_result.putalpha(construction_masks[1])
    #
    #     intermediate_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height), color=(255, 255, 255, 0))
    #     intermediate_layer.paste(subject_image_blurred)
    #     intermediate_layer.paste(subject_image, (subject_x, subject_y))
    #     intermediate_layer.putalpha(construction_masks[0])
    #     final_result = Image.alpha_composite(final_result, intermediate_layer)
    #
    #     # paste blurred and initial image
    #     # final_result.paste(subject_image, (subject_x, subject_y))
    #
    #     # final_result = automatic.img2img(
    #     #     images=[final_result],
    #     #     prompt=subjects_style,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     cfg_scale=4,
    #     #     denoising_strength=0.5,
    #     #     seed=seed_value,
    #     #     script_name="outpainting mk2",
    #     #     script_args=[None, diff_w // 2, 10, ["left", "right"], 1, 0.05]
    #     # )
    #     #
    #     # final_result = final_result.image
    #     # final_result = final_result.resize((rel_canvas_width, rel_canvas_height))
    #     # final_result.paste(subject_image, subject_mask_shape)
    #     # final_result.save(config.UPLOAD_FOLDER + f"/lateral_{generated_image_id}.png")
    #     #
    #
    #     # final_result = final_result.image
    #     # final_result = final_result.resize((rel_canvas_width, rel_canvas_height))
    #     # final_result.paste(subject_image, subject_mask_shape)
    #     # final_result.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #     # subject_mask.save(config.UPLOAD_FOLDER + f"/mask_{generated_image_id}.png")
    #
    #     # subject_mask = ImageOps.invert(subject_mask)
    #
    #     # final_result = final_result.filter(ImageFilter.GaussianBlur(radius=20))
    #     final_result = automatic.txt2img(
    #         prompt=canvas_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=10,
    #         denoising_strength=0.8,
    #         seed=seed_value,
    #         steps=15,
    #     )
    #
    #     final_result.image.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     # final_result = automatic.img2img(
    #     #     images=[final_result],
    #     #     # mask_image=construction_masks[0],
    #     #     # mask_blur=1,
    #     #     initial_noise_multiplier=1.6,
    #     #     prompt=f"{canvas_prompt}",
    #     #     negative_prompt=NEG_PROMPT,
    #     #     # inpainting_fill=1,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     cfg_scale=10,
    #     #     denoising_strength=0.8,
    #     #     seed=seed_value,
    #     #     steps=15,
    #     #     script_name="outpainting mk2",
    #     #     script_args=[None, diff_h // 2, 10, ["up", "down"], 1, 0.05]
    #     # )
    #
    #     # final_result = final_result.image
    #     #
    #     # final_result = automatic.img2img(
    #     #     images=[final_result],
    #     #     # mask_image=construction_masks[0],
    #     #     # mask_blur=1,
    #     #     initial_noise_multiplier=1.6,
    #     #     prompt=f"{canvas_prompt}",
    #     #     negative_prompt=NEG_PROMPT,
    #     #     # inpainting_fill=1,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     cfg_scale=10,
    #     #     denoising_strength=0.8,
    #     #     seed=seed_value,
    #     #     steps=15,
    #     #     script_name="outpainting mk2",
    #     #     script_args=[None, diff_w // 2, 10, ["left", "right"], 1, 0.05]
    #     # )
    #
    #     # final_result = automatic.img2img(
    #     #     images=[final_result],
    #     #     mask_image=construction_masks[0],
    #     #     mask_blur=1,
    #     #     initial_noise_multiplier=1.5,
    #     #     prompt=f"{canvas_prompt}",
    #     #     negative_prompt=NEG_PROMPT,
    #     #     inpainting_fill=1,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     cfg_scale=8,
    #     #     denoising_strength=0.8,
    #     #     seed=seed_value,
    #     #     steps=15,
    #     # )
    #
    #     intermediate_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height), color=(255, 255, 255, 0))
    #     intermediate_layer.paste(subject_image_blurred)
    #     intermediate_layer.paste(subject_image, (subject_x, subject_y))
    #
    #     final_result = final_result.image.convert("RGBA")
    #     final_result = final_result.resize((rel_canvas_width, rel_canvas_height))
    #     final_result.putalpha(construction_masks[0])
    #     intermediate_layer.putalpha(ImageOps.invert(construction_masks[1]))
    #     # intermediate_layer.putalpha(128)
    #     final_result = Image.alpha_composite(final_result, intermediate_layer)
    #     final_result.save(config.UPLOAD_FOLDER + f"/int1_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_result],
    #         mask_image=construction_masks[1],
    #         mask_blur=1,
    #         prompt=f"{canvas_prompt}",
    #         negative_prompt=NEG_PROMPT,
    #         initial_noise_multiplier=1.3,
    #         inpainting_fill=1,
    #         inpaint_full_res=False,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=7.5,
    #         denoising_strength=0.6,
    #         seed=seed_value,
    #         steps=15,
    #     )
    #
    #     intermediate_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height), color=(255, 255, 255, 0))
    #     intermediate_layer.paste(subject_image_blurred)
    #     intermediate_layer.paste(subject_image, (subject_x, subject_y))
    #
    #     final_result = final_result.image.convert("RGBA")
    #     final_result = final_result.resize((rel_canvas_width, rel_canvas_height))
    #     # final_result.putalpha(construction_masks[1])
    #     intermediate_layer.putalpha(ImageOps.invert(construction_masks[2]))
    #     # final_result = Image.alpha_composite(final_result, intermediate_layer)
    #
    #     # final_result.paste(subject_image, (subject_x, subject_y))
    #     # compose initial mask with secondary mask
    #
    #     final_result.save(config.UPLOAD_FOLDER + f"/int2_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_result],
    #         mask_image=construction_masks[2],
    #         mask_blur=1,
    #         prompt=f"{canvas_prompt}",
    #         negative_prompt=NEG_PROMPT,
    #         initial_noise_multiplier=1.1,
    #         inpainting_fill=1,
    #         inpaint_full_res=False,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=7,
    #         denoising_strength=0.6,
    #         seed=seed_value,
    #         steps=30,
    #     )
    #
    #     final_result = final_result.image.convert("RGBA")
    #     final_result = final_result.resize((rel_canvas_width, rel_canvas_height))
    #     # intermediate_layer.putalpha(ImageOps.invert(subject_mask_sm))
    #     # intermediate_layer.putalpha(64)
    #     # final_result = Image.alpha_composite(final_result, intermediate_layer)
    #     # final_result = ImageEnhance.Sharpness(final_result).enhance(1.05)
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result,
    #         upscaling_resize_w=rel_canvas_width * 2,
    #         upscaling_resize_h=rel_canvas_height * 2,
    #         upscaler_1="R-ESRGAN 4x+",
    #         codeformer_visibility=0.5,
    #         codeformer_weight=0.5,
    #     )
    #
    #     subject_image = final_result.image
    #     metadata = PngInfo()
    #     metadata.add_text("RememberTag", "produced data")
    #     subject_image.save(config.UPLOAD_FOLDER + f"/final_{generated_image_id}.png", pngInfo=metadata)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": f"/final_{generated_image_id}.png",
    #         "seed": seed_value
    #     }}
    #
    #     # extract subjects style
    #     # for input_data in inputs:
    #     #     subject = input_data.get('subject')
    #     #     if subject:
    #     #         subject_image = data_uri_to_image(subject)
    #     #         # we need to scale the image to fit the selected container
    #     #         logger.debug(f"image size {subject_image.size}")
    #     #         # extract width and height and adjust to the given space
    #     #         x = input_data.get("x")
    #     #         y = input_data.get("y")
    #     #         width = input_data.get("width", canvas_width)
    #     #         height = input_data.get("height", canvas_height)
    #     #         rel_width = int(width * rel_per_width)
    #     #         rel_height = int(height * rel_per_height)
    #     #         rel_x = int(x * rel_per_width)
    #     #         rel_y = int(y * rel_per_height)
    #     #         logger.debug(f"normal sizes {width} {height} {x} {y}")
    #     #         logger.debug(f"transformed sizes {rel_width} {rel_height} {rel_x} {rel_y}")
    #     #
    #     #         # resize and center image to the container keeping the aspect ratio
    #     #         # keep the smaller dim
    #     #         subject_width, subject_height = subject_image.size
    #     #         subject_ar = subject_width / subject_height
    #     #
    #     #         if subject_ar > 1:
    #     #             subject_width = rel_width
    #     #             subject_height = int(subject_width / subject_ar)
    #     #         else:
    #     #             subject_height = rel_height
    #     #             subject_width = int(subject_height * subject_ar)
    #     #
    #     #         subject_image = subject_image.resize((subject_width, subject_height))
    #     #         subject_x = ((rel_width - subject_width) // 2) + rel_x
    #     #         subject_y = ((rel_height - subject_height) // 2) + rel_y
    #     #
    #     #         # outpaint to fill the canvas
    #     #
    #     #         subject_mask_shape = get_bbox(subject_x, subject_y, subject_width, subject_height, 0.05)
    #     #         logger.debug(f"Subject size {subject_width} {subject_height} {subject_x} {subject_y}")
    #     #
    #     #         subject_mask_draw.rectangle(subject_mask_shape, fill="#ffffff")
    #     #         final_layer.paste(subject_image, (subject_x, subject_y))
    #     #         logger.debug("we have subject")
    #
    #     description = automatic.interrogate(image=final_layer).info
    #     subjects_style = [*description.split(",")[1:], *canvas_style.split(",")]
    #     subjects_style = [style.strip() for style in subjects_style]
    #     logger.debug(f"Loaded subject has the following description:\n{subjects_style}")
    #
    #     subject_mask = ImageOps.invert(subject_mask)
    #     # .filter(ImageFilter.GaussianBlur(radius=10))
    #     subject_mask.save(config.UPLOAD_FOLDER + f"/su_mask_{generated_image_id}.png")
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         mask_image=subject_mask,
    #         mask_blur=10,
    #         prompt=f"{canvas_prompt}, {', '.join(subjects_style)}",
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         inpainting_fill=1,
    #         initial_noise_multiplier=1.2,
    #         inpaint_full_res=False,
    #         cfg_scale=10,
    #         denoising_strength=1.2,
    #         seed=seed_value,
    #         restore_faces=True
    #     )
    #
    #     final_result.image.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_result.image],
    #         # mask_image=subject_mask,
    #         # mask_blur=10,
    #         # prompt=f"{canvas_prompt}, {', '.join(subjects_style)}",
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         # inpainting_fill=0,
    #         # initial_noise_multiplier=1.2,
    #         # inpaint_full_res=False,
    #         cfg_scale=5,
    #         denoising_strength=0.5,
    #         seed=seed_value,
    #         # pixels, mask_blur, inpainting_fill, direction
    #         # script_name="poor man's outpainting",
    #         # script_args=[128, 10, "latent noise", ["left", "right", "up", "down"]]
    #         script_name="outpainting mk2",
    #         script_args=[None, 128, 10, ["left", "right", "up", "down"], 1, 0.05]
    #     )
    #
    #     # final_result = final_result.image
    #
    #     # final_result = automatic.extra_single_image(
    #     #     image=final_result,
    #     #     upscaling_resize_w=rel_canvas_width * 4,
    #     #     upscaling_resize_h=rel_canvas_height * 4,
    #     #     upscaler_1="R-ESRGAN 4x+",
    #     #     # upscaler_2="ESRGAN",
    #     #     # extras_upscaler_2_visibility=0.2,
    #     #     codeformer_visibility=0.5,
    #     #     codeformer_weight=0.5,
    #     # )
    #
    #     final_result = final_result.image
    #     final_result = ImageEnhance.Sharpness(final_result).enhance(1.2)
    #     filename_image = f"/final_{generated_image_id}.png"
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #     logger.info(f"Generation information rel size {rel_canvas_width}:{rel_canvas_height}")
    #     result0 = automatic.txt2img(
    #         prompt=background_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=5,
    #         seed=seed_value,
    #         denoising_strength=0.2,
    #         steps=12,
    #     )
    #     # the text2img function approximate the relative values to some resolution, so we update the relative values
    #     # and we will rescale the image at the end of the process
    #
    #     final_layer = result0.image.convert("RGBA")
    #     rel_canvas_width, rel_canvas_height = final_layer.size
    #     logger.debug(f"Final layer size {final_layer.size}")
    #     final_layer.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     # make three different layers for the subject, foreground
    #     subject_layer = Image.new("RGBA", final_layer.size)
    #     foreground_layer = Image.new("RGBA", final_layer.size)
    #     background_layer = Image.new("RGBA", final_layer.size)
    #
    #     for idx, input_data in enumerate(inputs):
    #         depth = input_data.get("depth", 0)
    #         # if depth != -1:
    #         logger.debug(f"Input number {idx} is processed")
    #         image_prompt = input_data.get('text')
    #
    #         x = input_data.get("x")
    #         y = input_data.get("y")
    #         width = input_data.get("width", canvas_width)
    #         height = input_data.get("height", canvas_height)
    #
    #         # here we shouldn't match the scale in the canvas, but the relative scale to the GEN_SIZE
    #         rel_width = int(width / canvas_width * rel_canvas_width)
    #         rel_height = int(height / canvas_height * rel_canvas_height)
    #         rel_x = int(x / canvas_width * rel_canvas_width)
    #         rel_y = int(y / canvas_height * rel_canvas_height)
    #
    #         # mask invert and paste on new layer
    #         logger.info(f"Canvas {canvas_width} {canvas_height}")
    #         mask_layer = Image.new("L", (rel_canvas_width, rel_canvas_height))
    #         mask_layer_draw = ImageDraw.Draw(mask_layer)
    #         logger.debug(f"Mask size {mask_layer.size}")
    #         # if depth == 1, then the element is a subject and we call img2text for better generated elements
    #         if depth == 0:
    #             mask_shape = (rel_x, rel_y, (rel_x + rel_width) * 1.1, (rel_y + rel_height) * 1.1)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=20))
    #             # rel_gen_width, rel_gen_height = image_scale(width, height, GEN_SIZE)
    #             # result = automatic.txt2img(
    #             #     prompt=f"gorgeous {image_prompt}, white background, full body, in frame, all around light",
    #             #     negative_prompt=NEG_PROMPT,
    #             #     width=rel_gen_width,
    #             #     height=rel_gen_height,
    #             #     cfg_scale=7.5,
    #             #     styles=["cybertech"],
    #             #     denoising_strength=0.6,
    #             #     seed=seed_value,
    #             # )
    #             # single_elem = result.image.resize((rel_width, rel_height))
    #             # elem_layer = Image.new("RGBA", mask_layer.size, color="#FFFFFF")
    #             # elem_layer.paste(single_elem, (x, y))
    #             # elem_layer = elem_layer.filter(ImageFilter.GaussianBlur(radius=20))
    #             # elem_layer.paste(single_elem, (x + 10, y + 10))
    #             # elem_layer.putalpha(mask_layer)
    #             # subject_layer = Image.alpha_composite(subject_layer, elem_layer)
    #             padding = int(rel_width * EXPAND_SIZE * EXPAND_SIZE)
    #             result = automatic.img2img(
    #                 images=[final_layer],
    #                 mask_image=mask_layer,
    #                 mask_blur=3,
    #                 prompt=f"one gorgeous {image_prompt}, centered, in frame, full body, full body photo, front view, sharp focus, {canvas_style}",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=1.2,
    #                 inpaint_full_res_padding=padding,
    #                 inpaint_full_res=False,
    #                 cfg_scale=9,
    #                 denoising_strength=1.2,
    #                 seed=seed_value,
    #             )
    #
    #             # increase selected section
    #             # mask_shape = (x - (EXPAND_SIZE * rel_width), y - (EXPAND_SIZE * rel_height), (x + rel_width) * (1 + EXPAND_SIZE), (y + rel_height) * (1 + EXPAND_SIZE))
    #             # mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # global_mask_draw.rectangle(mask_shape, fill="#ffffff")
    #
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=3))
    #             elem_layer = result.image
    #
    #             logger.debug(f"mask {mask_layer.size} elem {elem_layer.size} padding {padding}")
    #             elem_layer.putalpha(mask_layer)
    #             subject_layer = Image.alpha_composite(subject_layer, elem_layer)
    #         else:
    #             mask_shape = (rel_x, rel_y, rel_x + rel_width, rel_y + rel_height)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # global_mask_draw.rectangle(mask_shape, fill="#ffffff")
    #
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #             result = automatic.img2img(
    #                 images=[final_layer],
    #                 mask_image=mask_layer,
    #                 mask_blur=2,
    #                 prompt=f"one gorgeous {image_prompt}, {canvas_style}",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=1,
    #                 inpaint_full_res=False,
    #                 cfg_scale=6,
    #                 denoising_strength=1,
    #                 seed=seed_value,
    #             )
    #             elem_layer = result.image
    #             elem_layer.putalpha(mask_layer)
    #             if depth == 1:
    #                 foreground_layer = Image.alpha_composite(foreground_layer, elem_layer)
    #             else:
    #                 background_layer = Image.alpha_composite(background_layer, elem_layer)
    #
    #         # final_layer = Image.alpha_composite(final_layer, elem_layer)
    #
    #         # else:
    #         #     mask_shape = (x, y, x + rel_width, y + rel_height)
    #         #     mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #         #
    #         #     mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #         #     result = automatic.img2img(
    #         #         images=[final_layer],
    #         #         mask_image=mask_layer,
    #         #         prompt=f"one gorgeous {image_prompt}, {canvas_style}",
    #         #         negative_prompt=NEG_PROMPT,
    #         #         width=GEN_SIZE,
    #         #         height=GEN_SIZE,
    #         #         inpainting_fill=1,
    #         #         initial_noise_multiplier=1.5,
    #         #         inpaint_full_res=False,
    #         #         cfg_scale=9,
    #         #         denoising_strength=0.8,
    #         #         seed=seed_value,
    #         #     )
    #         #     elem_layer = result.image
    #         #     elem_layer.putalpha(mask_layer)
    #         #     background_layer = Image.alpha_composite(background_layer, elem_layer)
    #
    #     # save foreground, subject
    #     subject_layer.save(config.UPLOAD_FOLDER + f"/su_{generated_image_id}.png")
    #     foreground_layer.save(config.UPLOAD_FOLDER + f"/fg_{generated_image_id}.png")
    #     background_layer.save(config.UPLOAD_FOLDER + f"/bg_{generated_image_id}.png")
    #
    #     final_layer = Image.alpha_composite(final_layer, background_layer)
    #     final_layer = Image.alpha_composite(final_layer, subject_layer)
    #     final_layer = Image.alpha_composite(final_layer, foreground_layer)
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #
    #     description = automatic.interrogate(
    #         image=final_layer
    #     )
    #
    #     description = f"{description.info.split(',')[0]}, {canvas_style}"
    #
    #     logger.debug(f"This is the description {description}")
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         prompt=description,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         seed=seed_value,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=5,
    #         denoising_strength=0.2,
    #         steps=40,
    #         initial_noise_multiplier=1.2,
    #         restore_faces=True,
    #     )
    #
    #     # TODO add quality factor
    #     final_result = final_result.image
    #     final_result = ImageEnhance.Sharpness(final_result).enhance(1.2)
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result,
    #         upscaling_resize_w=rel_canvas_width * 4,
    #         upscaling_resize_h=rel_canvas_height * 4,
    #         upscaler_1="R-ESRGAN 4x+",
    #         # upscaler_2="ESRGAN",
    #         # extras_upscaler_2_visibility=0.2,
    #         codeformer_visibility=0.5,
    #         codeformer_weight=0.5,
    #     )
    #
    #     final_result = final_result.image
    #     # final_result = final_result.filter(ImageFilter.EDGE_ENHANCE)
    #
    #     filename_image = f"/final_{generated_image_id}.png"
    #     # apply the aspect ratio transformation
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/simple/", methods=["POST", ])
    # def simple_gen():
    #     generated_image_id = str(uuid.uuid4())
    #     seed_value = random.randint(0, 9999)
    #
    #     inputs = request.json.get("inputs", [])
    #     canvas_prompt = request.json.get("prompt", "")
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     if not canvas_width or not canvas_height:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     input_string = ""
    #
    #     rel_canvas_width, rel_canvas_height = image_scale(width=canvas_width, height=canvas_height, size=GEN_SIZE)
    #     background = automatic.txt2img(
    #         prompt=canvas_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=5,
    #         seed=seed_value,
    #         denoising_strength=0.2,
    #         steps=12,
    #     )
    #     background = background.image.convert("RGBA")
    #     rel_canvas_width, rel_canvas_height = background.size
    #
    #     background.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     # init objects layer
    #     object_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height))
    #     object_layer_mask = Image.new("L", (rel_canvas_width, rel_canvas_height), color=WHITE)
    #     object_layer_mask_draw = ImageDraw.Draw(object_layer_mask)
    #
    #     padding_size = 30
    #
    #     for input_elem in inputs:
    #         text = input_elem.get('text')
    #
    #         # add text to text strin
    #         input_string += f"one ({text}), "
    #
    #         position = (input_elem.get("x", 0), input_elem.get("y", 0))
    #         size = (input_elem.get("width", canvas_width), input_elem.get("height", canvas_height))
    #
    #         # rescale information
    #         position = (int(position[0] * rel_canvas_width / canvas_width),
    #                     int(position[1] * rel_canvas_width / canvas_height))
    #
    #         size = (int(size[0] * rel_canvas_width / canvas_width),
    #                 int(size[1] * rel_canvas_height / canvas_height))
    #
    #         # now we firstly make the generation for the image
    #         gen_rel_width, gen_rel_height = image_scale(*size, GEN_SIZE)
    #         subject = automatic.txt2img(
    #             prompt=f"one gorgeous (({text})) in [{canvas_prompt}], hyper realism, highest quality",
    #             negative_prompt=NEG_PROMPT,
    #             width=gen_rel_width,
    #             height=gen_rel_height,
    #             seed=seed_value,
    #             seed_resize_from_h=size[0],
    #             seed_resize_from_w=size[1],
    #             cfg_scale=7,
    #             denoising_strength=0.5,
    #             steps=10
    #         )
    #
    #         padded_box = get_bbox_pad(position, size, padding_size)
    #         pad_size = (padded_box[2] - padded_box[0], padded_box[3] - padded_box[1])
    #         pad_pos = (padded_box[0], padded_box[1])
    #
    #         subject = subject.image.convert("RGBA").resize(pad_size)
    #         subject = subject.filter(ImageFilter.DETAIL)
    #
    #         subject_mask = Image.new("L", (rel_canvas_width, rel_canvas_height), color=BLACK)
    #         subject_mask_draw = ImageDraw.Draw(subject_mask)
    #
    #         mask_shape = (position[0], position[1], position[0] + size[0], position[1] + size[1])
    #         subject_mask_draw.rounded_rectangle(mask_shape, radius=padding_size, fill=WHITE)
    #         subject_mask = subject_mask.filter(ImageFilter.GaussianBlur(radius=padding_size // 2))
    #
    #         unpad_box = get_bbox_pad(position, size, -(1.5 * padding_size))
    #         object_layer_mask_draw.rounded_rectangle(unpad_box, radius=padding_size, fill=BLACK)
    #
    #         intermediate_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height))
    #         intermediate_layer.paste(subject, pad_pos)
    #         intermediate_layer.putalpha(subject_mask)
    #         object_layer = Image.alpha_composite(object_layer, intermediate_layer)
    #
    #     # object_layer_blurred = object_layer.filter(ImageFilter.GaussianBlur(radius=100))
    #     # object_layer = Image.alpha_composite(object_layer_blurred, object_layer)
    #     filename_image = f"/original_{generated_image_id}.png"
    #
    #     # apply the aspect ratio transformation
    #     object_layer.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     # blur mask
    #     # object_layer_mask_blurred = object_layer_mask.filter(ImageFilter.GaussianBlur(radius=padding_size // 2))
    #
    #     # background.putalpha(object_layer_mask)
    #     final_layer = Image.alpha_composite(background, object_layer)
    #
    #     final_layer = final_layer.convert("RGB")
    #     # ImageFilter.UnsharpMask(radius=2, percent=90)
    #     # .filter(ImageFilter.DETAIL)
    #     final_layer = final_layer.filter(ImageFilter.SMOOTH)
    #     # final_layer_gray = final_layer.convert("L").convert("RGB")
    #     # final_layer_gray = ImageEnhance.Contrast(final_layer_gray).enhance(0.6)
    #
    #     # filename_image = f"/edges_{generated_image_id}.png"
    #     # final_layer = ImageChops.subtract(final_layer, final_layer.convert("L").convert("RGB"))
    #
    #     # red, green, blue = final_layer.split()
    #     # red = red.filter(ImageFilter.GaussianBlur(radius=padding_size * 2))
    #     # green = green.filter(ImageFilter.GaussianBlur(radius=padding_size * 2))
    #     # blue = blue.filter(ImageFilter.GaussianBlur(radius=padding_size * 2))
    #     #
    #     # diff_color = ImageChops.subtract(final_layer_gray, Image.merge("RGB", (red, green, blue)))
    #     # final_layer = ImageChops.subtract(final_layer, diff_color)
    #     # final_layer = ImageEnhance.Brightness(final_layer).enhance(1.6)
    #     # final_layer = ImageChops.multiply(final_layer_gray, final_layer)
    #     # final_layer = final_layer.filter(ImageFilter.SHARPEN)
    #     # final_layer_gray = final_layer_gray.filter(ImageFilter.GaussianBlur(radius=20))
    #     # final_layer = ImageChops.add(final_layer_gray, final_layer)
    #     # final_layer = ImageChops.multiply(, final_layer)
    #
    #     # background.putalpha(16)
    #     # final_layer = Image.alpha_composite(final_layer.convert("RGBA"), background)
    #
    #     # object_layer_mask = object_layer_mask.filter(ImageFilter.GaussianBlur(radius=padding_size * 2))
    #     # object_layer_mask = ImageOps.invert(object_layer_mask)
    #
    #     # background.putalpha(200)
    #     # final_layer.paste(background, mask=object_layer_mask)
    #
    #     filename_image = f"/canvas_{generated_image_id}.png"
    #     final_layer.save(config.UPLOAD_FOLDER + filename_image)
    #     # {input_string}
    #     final_layer = automatic.img2depth(
    #         images=[final_layer],
    #         prompt=f"[{canvas_prompt}]",
    #         mask_image=object_layer_mask,
    #         mask_blur=padding_size // 3,
    #         inpainting_fill=1,
    #         seed_resize_from_w=final_layer.size[0],
    #         seed_resize_from_h=final_layer.size[1],
    #         negative_prompt="blurred, artifacts, cropped, collage, wrong perspective",
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         initial_noise_multiplier=1.1,
    #         seed=seed_value,
    #         cfg_scale=4,
    #         denoising_strength=0.5,
    #         steps=40,
    #     )
    #
    #     # script_name = "depthmap",
    #     # script_args = ['GPU', 'res101', False, True, True,
    #     #                '∯COMPUTE_DEVICE∯MODEL_TYPE∯BOOST∯NET_SIZE_MATCH∯DO_OUTPUT_DEPTH'],
    #
    #     logger.debug(f"{final_layer}")
    #     final_layer = final_layer.image
    #
    #     final_layer = automatic.extra_single_image(
    #         image=final_layer,
    #         upscaling_resize_w=rel_canvas_width * 2,
    #         upscaling_resize_h=rel_canvas_height * 2,
    #         upscaler_1="R-ESRGAN 4x+",
    #         codeformer_visibility=0.5,
    #         codeformer_weight=0.5,
    #     )
    #
    #     # final_layer = final_layer.image
    #     # filename_image = f"/int1_{generated_image_id}.png"
    #     # final_layer.save(config.UPLOAD_FOLDER + filename_image)
    #     #
    #     # final_layer = automatic.img2img(
    #     #     images=[final_layer],
    #     #     prompt=f"{input_string}",
    #     #     inpainting_fill=1,
    #     #     negative_prompt="blurred, artifacts, cropped, collage, wrong perspective",
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     # initial_noise_multiplier=1.1,
    #     #     seed=seed_value,
    #     #     cfg_scale=3,
    #     #     denoising_strength=0.2,
    #     #     steps=30
    #     # )
    #
    #     final_layer = final_layer.image
    #     final_layer = final_layer.resize((canvas_width, canvas_height))
    #     filename_image = f"/final_{generated_image_id}.png"
    #     final_layer.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/simple-gen-image/", methods=["POST", ])
    # def simple_gen_image():
    #     generated_image_id = str(uuid.uuid4())
    #     seed_value = random.randint(0, 9999)
    #
    #     inputs = request.json.get("inputs")
    #     canvas_prompt = request.json.get("prompt", "")
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     if not canvas_width or not canvas_height:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     # sort inputs here by depth
    #     inputs.sort(key=lambda x: x.get("depth", 0))
    #     # logger.debug(f"Sorted inputs {[elem.get('depth') for elem in inputs]}")
    #
    #     input_info = [(input_data.get("text"), input_data.get("weight", 0), input_data.get("depth", 0)) for input_data
    #                   in inputs if input_data.get("text")]
    #
    #     input_string = ', '.join([f"one ({text})" for text, _, depth in input_info])
    #     # input_string = ""
    #
    #     # {background_text}
    #     final_prompt = f"A gorgeous photo of {canvas_prompt}"
    #
    #     # logger.debug(f"Bg prompt {background_prompt}")
    #     # logger.debug(f"Final prompt {final_prompt}")
    #
    #     # use the function to make a proportional canvas to given sizes
    #     rel_canvas_width, rel_canvas_height = image_scale(width=canvas_width, height=canvas_height, size=GEN_SIZE)
    #     logger.info(f"Generation information rel size {rel_canvas_width}:{rel_canvas_height}")
    #     result0 = automatic.txt2img(
    #         prompt=final_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=5,
    #         seed=seed_value,
    #         denoising_strength=0.2,
    #         steps=12,
    #     )
    #
    #     final_prompt = f"{final_prompt}, {input_string}"
    #
    #     final_layer = result0.image.convert("RGBA")
    #     rel_canvas_width, rel_canvas_height = final_layer.size
    #     final_layer = Image.new("RGBA", (rel_canvas_width, rel_canvas_height), color="#FFFFFF")
    #     logger.debug(f"Final layer size {final_layer.size}")
    #     final_layer.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     global_mask = Image.new("L", (rel_canvas_width, rel_canvas_height), color="#000000")
    #     global_mask_draw = ImageDraw.Draw(global_mask)
    #     # global_mask = Image.new("")
    #
    #     for idx, input_data in enumerate(inputs):
    #         # if depth != -1:
    #         logger.debug(f"Input number {idx} is processed")
    #         image_prompt = input_data.get('text')
    #
    #         x = input_data.get("x", 0)
    #         y = input_data.get("y", 0)
    #         width = input_data.get("width", canvas_width)
    #         height = input_data.get("height", canvas_height)
    #
    #         # input_string = input_string + f"one ({image_prompt}) in the {get_position(canvas_width, canvas_height, x, y)}, "
    #
    #         rel_width = int(width / canvas_width * rel_canvas_width)
    #         rel_height = int(height / canvas_height * rel_canvas_height)
    #         rel_x = int(x / canvas_width * rel_canvas_width)
    #         rel_y = int(y / canvas_height * rel_canvas_height)
    #
    #         # relative size to the final layer here
    #         logger.debug(f"Width {rel_width} Height {rel_height} X {rel_x} Y {rel_y}")
    #
    #         # mask invert and paste on new layer
    #         mask_layer = Image.new("L", (rel_canvas_width, rel_canvas_height), color="#000000")
    #         mask_layer_draw = ImageDraw.Draw(mask_layer)
    #
    #         mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, 0.1)
    #         mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #         mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=10))
    #
    #         gen_rel_width, gen_rel_height = image_scale(rel_width, rel_height, GEN_SIZE)
    #         logger.debug(f"Size used for generation {gen_rel_width} {gen_rel_height}")
    #         result = automatic.txt2img(
    #             prompt=f"one gorgeous ({image_prompt}) front view with [{canvas_prompt}] in the background, portrait, photography",
    #             negative_prompt=NEG_PROMPT,
    #             width=gen_rel_width,
    #             height=gen_rel_height,
    #             seed=seed_value,
    #             # seed_resize_from_h=GEN_SIZE,
    #             # seed_resize_from_w=GEN_SIZE,
    #             cfg_scale=7,
    #             denoising_strength=0.5,
    #             steps=10
    #         )
    #
    #         # mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, -0.05)
    #         # mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #         # mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=20))
    #
    #         elem_layer = result.image.resize((rel_width, rel_height))
    #
    #         # prepare final layer
    #         final_layer.paste(final_layer, (0, 0), mask=mask_layer)
    #
    #         mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, 0)
    #         logger.debug(f"Mask {mask_layer.size} final {final_layer.size}")
    #         final_layer.paste(elem_layer, (rel_x, rel_y), mask=mask_layer.crop(mask_shape))
    #         mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, 0.2)
    #         global_mask_draw.rectangle(mask_shape, fill="#ffffff")
    #
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #     global_mask = global_mask.filter(ImageFilter.GaussianBlur(radius=10))
    #     global_mask.save(config.UPLOAD_FOLDER + f"/gm_{generated_image_id}.png")
    #     # {input_string} with [{canvas_prompt}], highest quality, masterpiece
    #     # final_result = automatic.img2img(
    #     #     images=[final_layer],
    #     #     prompt=f"{input_string}",
    #     #     mask_image=global_mask,
    #     #     mask_blur=10,
    #     #     inpainting_fill=1,
    #     #     inpaint_full_res=False,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     seed=seed_value,
    #     #     cfg_scale=5,
    #     #     denoising_strength=0.6,
    #     #     initial_noise_multiplier=1.2,
    #     #     steps=15,
    #     # )
    #
    #     # final_result.image.save(config.UPLOAD_FOLDER + f"/it_{generated_image_id}.png")
    #
    #     # final_result = automatic.img2img(
    #     #     images=[final_layer],
    #     #     prompt=f"{input_string}, {canvas_prompt} in the background",
    #     #     mask_image=global_mask,
    #     #     mask_blur=5,
    #     #     inpainting_fill=1,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     seed=seed_value,
    #     #     cfg_scale=7,
    #     #     denoising_strength=0.7,
    #     #     steps=10
    #     # )
    #     #
    #     #
    #     # int_result = final_result.image.convert("RGBA")
    #     # int_result.save(config.UPLOAD_FOLDER + f"/int1_{generated_image_id}.png")
    #     #
    #     # int_result.putalpha(128)
    #     # final_layer = Image.alpha_composite(final_layer, int_result)
    #     #
    #     # final_result = automatic.img2img(
    #     #     images=[final_layer],
    #     #     prompt=f"{input_string}, {canvas_prompt} in the background",
    #     #     mask_image=global_mask,
    #     #     mask_blur=5,
    #     #     inpainting_fill=1,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     seed=seed_value,
    #     #     cfg_scale=7,
    #     #     denoising_strength=0.7,
    #     #     steps=10
    #     # )
    #     #
    #     # int_result = final_result.image.convert("RGBA")
    #     # int_result.save(config.UPLOAD_FOLDER + f"/int2_{generated_image_id}.png")
    #     #
    #     # int_result.putalpha(128)
    #     # final_layer = Image.alpha_composite(final_layer, int_result)
    #     #
    #
    #     # description = automatic.interrogate(final_layer).info
    #     # logger.debug(f"This is the final result description {description}")
    #
    #     # description = f"{canvas_prompt} {','.join([description.split(',')][1:])}"
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         prompt=f"{canvas_prompt}",
    #         mask_image=ImageOps.invert(global_mask),
    #         mask_blur=0,
    #         inpainting_fill=1,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         initial_noise_multiplier=1.2,
    #         seed=seed_value,
    #         cfg_scale=7,
    #         denoising_strength=1.6,
    #         steps=30
    #     )
    #
    #     final_layer = final_result.image
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result,
    #         upscaling_resize_w=rel_canvas_width * 2,
    #         upscaling_resize_h=rel_canvas_height * 2,
    #         upscaler_1="R-ESRGAN 4x+",
    #         codeformer_visibility=0.5,
    #         codeformer_weight=0.5,
    #     )
    #
    #     final_layer = final_result.image
    #
    #     # final_result = automatic.img2img(
    #     #     images=[final_layer],
    #     #     prompt=f"{input_string}, {canvas_prompt}",
    #     #     inpainting_fill=1,
    #     #     negative_prompt=NEG_PROMPT,
    #     #     width=rel_canvas_width,
    #     #     height=rel_canvas_height,
    #     #     seed=seed_value,
    #     #     cfg_scale=7,
    #     #     denoising_strength=0.2,
    #     #     steps=40
    #     # )
    #     #
    #     # final_layer = final_result.image
    #
    #     # TODO add quality factor
    #     final_result = final_layer.resize((rel_canvas_width, rel_canvas_height))
    #     # final_result = ImageEnhance.Sharpness(final_result).enhance(1.1)
    #
    #     logger.debug("Upscaling step")
    #     # final_result = automatic.extra_single_image(
    #     #     image=final_result,
    #     #     upscaling_resize_w=rel_canvas_width * 2,
    #     #     upscaling_resize_h=rel_canvas_height * 2,
    #     #     upscaler_1="R-ESRGAN 4x+",
    #     #     # upscaler_2="ESRGAN",
    #     #     # extras_upscaler_2_visibility=0.2,
    #     #     # codeformer_visibility=0.5,
    #     #     # codeformer_weight=0.5,
    #     # )
    #     #
    #     # final_result = final_result.image
    #     filename_image = f"/final_{generated_image_id}.png"
    #
    #     # apply the aspect ratio transformation
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/iterative-image/", methods=["POST", ])
    # def iterative_image():
    #     generated_image_id = str(uuid.uuid4())
    #
    #     inputs = request.json.get("inputs")
    #
    #     # logger.debug(f"{request.js}")
    #     # logger.debug("Subject search here")
    #     # for inputElem in inputs:
    #     #     # with request.urlopen(data_uri) as response:
    #     #     #     data = response.read()
    #     #     subject = inputElem.get('subject')
    #     #     if subject:
    #     #         logger.debug(f"file is {subject}")
    #     #         with urllib.request.urlopen(subject) as subject_file:
    #     #             data = subject_file.read()
    #     #             data = Image.open(BytesIO(data))
    #     #             logger.debug(f"Received image size is {data.size}")
    #
    #     # if we have a subject, the generation step will be different
    #     # first, we should interrogate clip to know what s in the image and create something that respect what s in
    #     # the image
    #
    #     # for input_elem in inputs:
    #     #     subject = input_elem.get('subject')
    #     #     logger.debug(f"Subject {subject}")
    #     #     if input_elem.get("subject"):
    #     # with open(os.path.abspath(f'{subject}'), 'rb') as f:
    #     #     f.write(file.content)
    #     # result = requests.get(subject)
    #     # logger.debug(f"{result}")
    #     # f = urllib.request.Request(urllib.parse.quote())
    #     # f = urllib.request.urlopen(f)
    #     # logger.debug(f"{f.read()}")
    #
    #     canvas_prompt = request.json.get("prompt", "")
    #     canvas_style = request.json.get("style", "")
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     if not canvas_width or not canvas_height:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     seed_value = random.randint(0, 9999)
    #
    #     # sort inputs here by depth
    #     inputs.sort(key=lambda x: x.get("depth", 0))
    #     # logger.debug(f"Sorted inputs {[elem.get('depth') for elem in inputs]}")
    #
    #     input_info = [(input_data.get("text"), input_data.get("weight", 0), input_data.get("depth", 0)) for input_data
    #                   in inputs if input_data.get("text")]
    #
    #     input_string = ', '.join(['a ' +
    #                               (text if depth != 0 else f"({text})")
    #                               for text, _, depth in input_info])
    #
    #     # first, construct the background from the overall prompt + the background inputs
    #     background_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == -1])
    #     # subject_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == 0])
    #     # foreground_text = " AND ".join([f"one {text}" for text, _, depth in input_info if depth == 1])
    #
    #     final_prompt = f"A gorgeous photo of {canvas_prompt}, {input_string}, {canvas_style}"
    #
    #     # {background_text}
    #     background_prompt = f"A gorgeous photo of {canvas_prompt if canvas_prompt else background_text}, {canvas_style}"
    #
    #     # logger.debug(f"Bg prompt {background_prompt}")
    #     # logger.debug(f"Final prompt {final_prompt}")
    #
    #     # use the function to make a proportional canvas to given sizes
    #     rel_canvas_width, rel_canvas_height = image_scale(width=canvas_width, height=canvas_height, size=GEN_SIZE)
    #     logger.info(f"Generation information rel size {rel_canvas_width}:{rel_canvas_height}")
    #     result0 = automatic.txt2img(
    #         prompt=background_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         cfg_scale=5,
    #         seed=seed_value,
    #         denoising_strength=0.2,
    #         steps=12,
    #     )
    #     # the text2img function approximate the relative values to some resolution, so we update the relative values
    #     # and we will rescale the image at the end of the process
    #
    #     final_layer = result0.image.convert("RGBA")
    #     rel_canvas_width, rel_canvas_height = final_layer.size
    #     logger.debug(f"Final layer size {final_layer.size}")
    #     final_layer.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #
    #     # make three different layers for the subject, foreground
    #     subject_layer = Image.new("RGBA", final_layer.size)
    #     foreground_layer = Image.new("RGBA", final_layer.size)
    #     background_layer = Image.new("RGBA", final_layer.size)
    #
    #     for idx, input_data in enumerate(inputs):
    #         depth = input_data.get("depth", 0)
    #         # if depth != -1:
    #         logger.debug(f"Input number {idx} is processed")
    #         image_prompt = input_data.get('text')
    #
    #         x = input_data.get("x")
    #         y = input_data.get("y")
    #         width = input_data.get("width", canvas_width)
    #         height = input_data.get("height", canvas_height)
    #
    #         # here we shouldn't match the scale in the canvas, but the relative scale to the GEN_SIZE
    #         rel_width = int(width / canvas_width * rel_canvas_width)
    #         rel_height = int(height / canvas_height * rel_canvas_height)
    #         rel_x = int(x / canvas_width * rel_canvas_width)
    #         rel_y = int(y / canvas_height * rel_canvas_height)
    #
    #         # mask invert and paste on new layer
    #         logger.info(f"Canvas {canvas_width} {canvas_height}")
    #         mask_layer = Image.new("L", (rel_canvas_width, rel_canvas_height))
    #         mask_layer_draw = ImageDraw.Draw(mask_layer)
    #         logger.debug(f"Mask size {mask_layer.size}")
    #         # if depth == 1, then the element is a subject and we call img2text for better generated elements
    #         if depth == 0:
    #             mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, 0.1)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=20))
    #             # rel_gen_width, rel_gen_height = image_scale(width, height, GEN_SIZE)
    #             # result = automatic.txt2img(
    #             #     prompt=f"gorgeous {image_prompt}, white background, full body, in frame, all around light",
    #             #     negative_prompt=NEG_PROMPT,
    #             #     width=rel_gen_width,
    #             #     height=rel_gen_height,
    #             #     cfg_scale=7.5,
    #             #     styles=["cybertech"],
    #             #     denoising_strength=0.6,
    #             #     seed=seed_value,
    #             # )
    #             # single_elem = result.image.resize((rel_width, rel_height))
    #             # elem_layer = Image.new("RGBA", mask_layer.size, color="#FFFFFF")
    #             # elem_layer.paste(single_elem, (x, y))
    #             # elem_layer = elem_layer.filter(ImageFilter.GaussianBlur(radius=20))
    #             # elem_layer.paste(single_elem, (x + 10, y + 10))
    #             # elem_layer.putalpha(mask_layer)
    #             # subject_layer = Image.alpha_composite(subject_layer, elem_layer)
    #
    #             final_layer_h = final_layer.copy()
    #             final_layer_h.putalpha(mask_layer)
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #             result = automatic.img2img(
    #                 images=[final_layer],
    #                 mask_image=mask_layer,
    #                 prompt=f"one gorgeous ({image_prompt})",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=1.2,
    #                 inpaint_full_res=False,
    #                 cfg_scale=10,
    #                 denoising_strength=1,
    #                 seed=seed_value,
    #             )
    #
    #             # increase selected section
    #             # mask_shape = (x - (EXPAND_SIZE * rel_width), y - (EXPAND_SIZE * rel_height), (x + rel_width) * (1 + EXPAND_SIZE), (y + rel_height) * (1 + EXPAND_SIZE))
    #             # mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # global_mask_draw.rectangle(mask_shape, fill="#ffffff")
    #
    #             mask_shape = get_bbox(rel_x, rel_y, rel_width, rel_height, -0.3)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #             elem_layer = result.image
    #             elem_layer.putalpha(mask_layer)
    #             subject_layer = Image.alpha_composite(subject_layer, elem_layer)
    #         else:
    #             mask_shape = (rel_x, rel_y, rel_x + rel_width, rel_y + rel_height)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             # global_mask_draw.rectangle(mask_shape, fill="#ffffff")
    #
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #             result = automatic.img2img(
    #                 images=[final_layer],
    #                 mask_image=mask_layer,
    #                 mask_blur=2,
    #                 prompt=f"one gorgeous ({image_prompt}) in a {canvas_prompt}, close up, in frame, full body, front view, sharp focus",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=1,
    #                 inpaint_full_res=False,
    #                 cfg_scale=6,
    #                 denoising_strength=1,
    #                 seed=seed_value,
    #             )
    #             elem_layer = result.image
    #             elem_layer.putalpha(mask_layer)
    #             if depth == 1:
    #                 foreground_layer = Image.alpha_composite(foreground_layer, elem_layer)
    #             else:
    #                 background_layer = Image.alpha_composite(background_layer, elem_layer)
    #
    #     # save foreground, subject
    #     subject_layer.save(config.UPLOAD_FOLDER + f"/su_{generated_image_id}.png")
    #     foreground_layer.save(config.UPLOAD_FOLDER + f"/fg_{generated_image_id}.png")
    #     background_layer.save(config.UPLOAD_FOLDER + f"/bg_{generated_image_id}.png")
    #
    #     final_layer = Image.alpha_composite(final_layer, background_layer)
    #     final_layer = Image.alpha_composite(final_layer, subject_layer)
    #     final_layer = Image.alpha_composite(final_layer, foreground_layer)
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         prompt=final_prompt,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         seed=seed_value,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=6,
    #         denoising_strength=0.4,
    #         steps=20,
    #         initial_noise_multiplier=1.1,
    #         restore_faces=True,
    #     )
    #
    #     # TODO add quality factor
    #     final_result = final_result.image
    #     # final_result = ImageEnhance.Sharpness(final_result).enhance(1.2)
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result,
    #         upscaling_resize_w=rel_canvas_width * 2,
    #         upscaling_resize_h=rel_canvas_height * 2,
    #         upscaler_1="R-ESRGAN 4x+",
    #         # upscaler_2="ESRGAN",
    #         # extras_upscaler_2_visibility=0.2,
    #         # codeformer_visibility=0.5,
    #         # codeformer_weight=0.5,
    #     )
    #
    #     final_result = final_result.image
    #     # final_result = final_result.filter(ImageFilter.EDGE_ENHANCE)
    #
    #     filename_image = f"/final_{generated_image_id}.png"
    #     # apply the aspect ratio transformation
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/inpaint-image/", methods=["POST", ])
    # def inpaint_image():
    #     inputs = request.json.get("inputs")
    #
    #     canvas_prompt = request.json.get("prompt", "")
    #     canvas_style = request.json.get("style", "")
    #
    #     canvas_width = request.json.get("width")
    #     canvas_height = request.json.get("height")
    #
    #     initial_image_id = request.json.get("id")
    #     generated_image_id = str(uuid.uuid4())
    #
    #     initial_seed = request.json.get("seed")
    #     seed_value = random.randint(0, 9999)
    #
    #     if not canvas_width or not canvas_height:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     if not initial_seed:
    #         return {"status": False, "msg": "No seed was given"}
    #
    #     # sort inputs here by depth
    #     inputs.sort(key=lambda x: x.get("depth", 0))
    #     input_info = [(input_data.get("text"), input_data.get("weight", 0), input_data.get("depth", 0)) for
    #                   input_data
    #                   in inputs if input_data.get("text")]
    #
    #     input_string = ', '.join(['a ' + (text if depth != 0 else f"({text})") for text, _, depth in input_info])
    #     final_prompt = f"A gorgeous photo of {input_string}, {canvas_prompt}, {canvas_style}"
    #
    #     # we should grab the original canvas now
    #     original_layer = Image.open(config.UPLOAD_FOLDER + f"/original_{initial_image_id}.png").convert("RGBA")
    #     try:
    #         logger.debug(f"Text for original image nothing")
    #     except Exception as e:
    #         logger.debug(f"No text was found in original image {e.args[0]}")
    #     subject_layer = Image.open(config.UPLOAD_FOLDER + f"/su_{initial_image_id}.png").convert("RGBA")
    #     background_layer = Image.open(config.UPLOAD_FOLDER + f"/bg_{initial_image_id}.png").convert("RGBA")
    #     foreground_layer = Image.open(config.UPLOAD_FOLDER + f"/fg_{initial_image_id}.png").convert("RGBA")
    #
    #     rel_canvas_width, rel_canvas_height = original_layer.size
    #
    #     for idx, input_data in enumerate(inputs):
    #         depth = input_data.get("depth", 0)
    #         image_prompt = input_data.get('text')
    #
    #         x = input_data.get("x")
    #         y = input_data.get("y")
    #         width = input_data.get("width", canvas_width)
    #         height = input_data.get("height", canvas_height)
    #
    #         rel_width = int(width / canvas_width * rel_canvas_width)
    #         rel_height = int(height / canvas_height * rel_canvas_height)
    #         rel_x = int(x / canvas_width * rel_canvas_width)
    #         rel_y = int(y / canvas_height * rel_canvas_height)
    #
    #         mask_layer = Image.new("L", (rel_canvas_width, rel_canvas_height))
    #         mask_layer_draw = ImageDraw.Draw(mask_layer)
    #         logger.debug(f"Mask size {mask_layer.size}")
    #
    #         # if depth == 1, then the element is a subject and we call img2text for better generated elements
    #         if depth == 0:
    #             mask_shape = (rel_x, rel_y, (rel_x + rel_width) * 1.1, (rel_y + rel_height) * 1.1)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #
    #             padding = int(rel_width * EXPAND_SIZE * EXPAND_SIZE)
    #             result = automatic.img2img(
    #                 images=[original_layer],
    #                 mask_image=mask_layer,
    #                 mask_blur=3,
    #                 prompt=f"one gorgeous {image_prompt}, centered, in frame, full body, full body photo, front view, sharp focus, {canvas_style}",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=1.5,
    #                 inpaint_full_res_padding=padding,
    #                 inpaint_full_res=False,
    #                 cfg_scale=10,
    #                 denoising_strength=1.6,
    #                 seed=seed_value,
    #                 steps=30
    #             )
    #
    #             elem_layer = result.image
    #             elem_layer.putalpha(mask_layer)
    #             subject_layer = Image.alpha_composite(subject_layer, elem_layer)
    #         else:
    #             mask_shape = (rel_x, rel_y, rel_x + rel_width, rel_y + rel_height)
    #             mask_layer_draw.rectangle(mask_shape, fill="#ffffff")
    #             mask_layer = mask_layer.filter(ImageFilter.GaussianBlur(radius=5))
    #             result = automatic.img2img(
    #                 images=[original_layer],
    #                 mask_image=mask_layer,
    #                 mask_blur=2,
    #                 prompt=f"one gorgeous {image_prompt}",
    #                 negative_prompt=NEG_PROMPT,
    #                 width=rel_canvas_width,
    #                 height=rel_canvas_height,
    #                 inpainting_fill=1,
    #                 initial_noise_multiplier=2,
    #                 inpaint_full_res=False,
    #                 cfg_scale=10,
    #                 denoising_strength=2,
    #                 seed=seed_value,
    #                 steps=30,
    #             )
    #
    #             elem_layer = result.image
    #             elem_layer.putalpha(mask_layer)
    #             if depth == 1:
    #                 foreground_layer = Image.alpha_composite(foreground_layer, elem_layer)
    #             else:
    #                 background_layer = Image.alpha_composite(background_layer, elem_layer)
    #
    #     original_layer.save(config.UPLOAD_FOLDER + f"/original_{generated_image_id}.png")
    #     subject_layer.save(config.UPLOAD_FOLDER + f"/su_{generated_image_id}.png")
    #     foreground_layer.save(config.UPLOAD_FOLDER + f"/fg_{generated_image_id}.png")
    #     background_layer.save(config.UPLOAD_FOLDER + f"/bg_{generated_image_id}.png")
    #
    #     final_layer = Image.alpha_composite(original_layer, background_layer)
    #     final_layer = Image.alpha_composite(final_layer, subject_layer)
    #     final_layer = Image.alpha_composite(final_layer, foreground_layer)
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #
    #     description = automatic.interrogate(
    #         image=final_layer
    #     )
    #
    #     description = f"{description.info.split(',')[0]}, {canvas_style}"
    #
    #     logger.debug(f"This is the description {description}")
    #     logger.debug("dsvkfgjbnotnbogrn")
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         prompt=description,
    #         width=rel_canvas_width,
    #         height=rel_canvas_height,
    #         seed=initial_seed,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=3,
    #         denoising_strength=0.2,
    #         initial_noise_multiplier=1.2,
    #         steps=20,
    #     )
    #
    #     # TODO add quality factor
    #     final_result = final_result.image
    #     final_result = ImageEnhance.Sharpness(final_result).enhance(1.2)
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result,
    #         upscaling_resize_w=rel_canvas_width * 4,
    #         upscaling_resize_h=rel_canvas_height * 4,
    #         upscaler_1="R-ESRGAN 4x+",
    #         codeformer_visibility=0.5,
    #         codeformer_weight=0.5,
    #     )
    #
    #     final_result = final_result.image
    #     filename_image = f"/final_{generated_image_id}.png"
    #     # apply the aspect ratio transformation
    #     final_result.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route("/api/generate-image/", methods=["POST", ])
    # def generate_image():
    #     # with this update, we should generate the background, then the subject,
    #     # then the foreground and order elements generation-wise
    #
    #     # there is no canvas prompt anymore, so we should just construct all the elements and add them all in a single
    #     # image
    #     inputs = request.json.get("inputs")
    #     canvas_prompt = request.json.get("prompt", "")
    #     canvas_size = request.json.get("size")
    #
    #     if not canvas_size:
    #         return {"status": False, "msg": "No canvas size was received"}
    #
    #     canvas_box = (canvas_size, canvas_size)
    #
    #     seed_value = random.randint(0, 9999)
    #     prompt = "A gorgeous photo" + f" of {canvas_prompt}" if canvas_prompt else " "
    #     logger.debug(f"{inputs}")
    #
    #     # sort inputs here by depth
    #     inputs.sort(key=lambda x: x.get("depth", 0))
    #
    #     # if additional weight is not zero, then we should process the new value of emphasis
    #     default_emphasis = 1.1
    #     input_info = [(input_data.get("text"), input_data.get("weight", 0), input_data.get("depth", 0)) for input_data
    #                   in inputs if input_data.get("text")]
    #     # weight_sum = sum([weight for text, weight in input_info])
    #
    #     input_string = ', '.join([
    #         # "(" + text + ":" + str(round((weight / weight_sum * default_emphasis), 2)) + ")"
    #         text if depth != 0 else f"({text})"
    #         for text, _, depth in input_info])
    #
    #     final_prompt = prompt + input_string + "\nBREAK\n".join([f"one {text}" for text, _, _ in input_info])
    #     # final_prompt = prompt + f" with {input_string}"
    #
    #     logger.info(final_prompt)
    #
    #     result0 = automatic.txt2img(
    #         prompt=final_prompt,
    #         negative_prompt=NEG_PROMPT,
    #         width=GEN_SIZE,
    #         height=GEN_SIZE,
    #         cfg_scale=7,
    #         seed=seed_value,
    #         denoising_strength=0.6,
    #         steps=30,
    #         styles=["cybertech"]
    #     )
    #     #
    #
    #     # image0 = image0.convert("P").quantize(colors=128,
    #     #                                       method=Quantize.MEDIANCUT,
    #     #                                       kmeans=2,
    #     #                                       dither=Dither.FLOYDSTEINBERG).convert(image0.mode)
    #
    #     # print("image info", imagine[0][1])
    #     # canvas = difussion.image_as_bytes(canvas)
    #     # canvas = Image.open(canvas).resize((canvas_size, canvas_size))
    #     # canvas = canvas.convert("RGBA")
    #     # canvas = canvas.filter(ImageFilter.GaussianBlur(radius=3))
    #
    #     final_layer = result0.image.convert("RGBA").resize(canvas_box)
    #     # canvas = Image.alpha_composite(foreground, canvas)
    #     # final_layer = Image.alpha_composite(final_layer, image0)
    #     # final_layer = image_with_blur(final_layer)
    #
    #     for idx, input_data in enumerate(inputs):
    #         logger.debug(f"Input number {idx} is processed")
    #         image_prompt = input_data.get('text')
    #
    #         # calc bbox
    #         x = input_data.get("x")
    #         y = input_data.get("y")
    #         width = input_data.get("width", 512)
    #         height = input_data.get("height", 512)
    #
    #         rel_width, rel_height = image_scale(width, height, GEN_SIZE)
    #         image_background = final_layer.crop((x, y, x + width, y + height)).resize((rel_width, rel_height))
    #
    #         # result = automatic.txt2img(
    #         #     prompt=f"gorgeous {image_prompt} with transparent background, full body, in frame",
    #         #     negative_prompt=negative_prompt,
    #         #     width=rel_width,
    #         #     height=rel_height,
    #         #     cfg_scale=7,
    #         #     styles=["cybertech"],
    #         #     denoising_strength=0.6,
    #         #     seed=seed_value,
    #         # )
    #
    #         #  stock image, centered, full view
    #
    #         # imagine = difussion.imagine(image_prompt, width=relative_width, height=relative_height)
    #         # image = result.image.convert("RGBA").resize((width, height))
    #
    #         image = Image.new("RGBA", (width, height))
    #
    #         # image = image.convert("P").quantize(colors=128,
    #         #                                     method=Quantize.MEDIANCUT,
    #         #                                     kmeans=2,
    #         #                                     dither=Dither.FLOYDSTEINBERG).convert(image.mode)
    #
    #         # now we should update the image with blur to work on images with different aspect ratios
    #         image, mask = image_with_blur(image, canvas_size)
    #         # retransform to initial dimensions
    #         image = image.resize((width, height))
    #
    #         # mask invert and paste on new layer
    #         expanded_size = (int(width * (1 + EXPAND_SIZE)), int(height * (1 + EXPAND_SIZE)))
    #         expanded_pos = (int(x - (width * EXPAND_SIZE / 2)), int(y - (height * EXPAND_SIZE / 2)))
    #         mask = mask.resize(expanded_size)
    #         mask_layer = Image.new("L", canvas_box)
    #         mask_layer.paste(mask, expanded_pos, mask=mask)
    #
    #         result = automatic.img2img(
    #             images=[final_layer],
    #             mask_image=mask_layer,
    #             prompt=f"gorgeous {image_prompt} with transparent background, full body, in frame",
    #             negative_prompt=NEG_PROMPT,
    #             width=GEN_SIZE,
    #             height=GEN_SIZE,
    #             inpainting_fill=1,
    #             initial_noise_multiplier=1.2,
    #             inpaint_full_res=False,
    #             cfg_scale=7,
    #             styles=["cybertech"],
    #             denoising_strength=0.6,
    #             seed=seed_value,
    #         )
    #
    #         # foreground = Image.new(image.mode, canvas_box)
    #         # foreground.paste(image, (x, y), mask=image)
    #         # foreground.putalpha(mask_layer)
    #         #
    #         # final_layer.paste(foreground, (0, 0), mask=mask_layer)
    #
    #         # final_layer = Image.alpha_composite(final_layer, foreground)
    #         final_layer = result.image
    #
    #     generated_image_id = str(uuid.uuid4())
    #     final_layer.save(config.UPLOAD_FOLDER + f"/canvas_{generated_image_id}.png")
    #
    #     final_result = automatic.img2img(
    #         images=[final_layer],
    #         prompt=final_prompt,
    #         seed=seed_value,
    #         negative_prompt=NEG_PROMPT,
    #         cfg_scale=7,
    #         denoising_strength=0.6,
    #         restore_faces=True,
    #         # steps=40,
    #         # sampler_name="DPM++ 2M SDE Heun Karras",
    #         styles=["cybertech"],
    #     )
    #
    #     # filename_image = f"/original_{generated_image_id}.png"
    #     # final_result.image.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     final_result = automatic.extra_single_image(
    #         image=final_result.image,
    #         upscaling_resize=2,
    #         upscaler_1="R-ESRGAN 4x+",
    #     )
    #
    #     filename_image = f"/final_{generated_image_id}.png"
    #     final_result.image.save(config.UPLOAD_FOLDER + filename_image)
    #
    #     return {"status": True, "data": {
    #         "id": generated_image_id,
    #         "image": filename_image,
    #         "seed": seed_value
    #     }}
    #
    #
    # @app.route('/api/get-image/<path:image>')
    # def get_image(image):
    #     print(image)
    #     return send_from_directory('static', f"media/{image}")

    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=8080)
