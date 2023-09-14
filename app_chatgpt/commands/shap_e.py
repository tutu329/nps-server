import torch

from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
xm = load_model('transmitter', device=device)
model = load_model('text300M', device=device)
diffusion = diffusion_from_config(load_config('diffusion'))
batch_size = 4
guidance_scale = 15.0
prompt = "a shark"

latents = sample_latents(
    batch_size=batch_size,
    model=model,
    diffusion=diffusion,
    guidance_scale=guidance_scale,
    model_kwargs=dict(texts=[prompt] * batch_size),
    progress=True,
    clip_denoised=True,
    use_fp16=True,
    use_karras=True,
    karras_steps=64,
    sigma_min=1e-3,
    sigma_max=160,
    s_churn=0,
)
render_mode = 'nerf' # you can change this to 'stf'
size = 64 # this is the size of the renders; higher values take longer to render.

cameras = create_pan_cameras(size, device)
for i, latent in enumerate(latents):
    images = decode_latent_images(xm, latent, cameras, rendering_mode=render_mode)
    display(gif_widget(images))
# Example of saving the latents as meshes.
from shap_e.util.notebooks import decode_latent_mesh

for i, latent in enumerate(latents):
    t = decode_latent_mesh(xm, latent).tri_mesh()
    with open(f'example_mesh_{i}.ply', 'wb') as f:
        t.write_ply(f)
    with open(f'example_mesh_{i}.obj', 'w') as f:
        t.write_obj(f)

# 1、前往"https://github.com/openai/shap-e"下载源码
# 2、在解压后的shap-e-main（有setup.py文件)下执行"pip install -e ."
# 3、安装完成后，将shap-e-main下的shap_e文件夹复制到希望的文件夹下
# 4、编制一个python文件，如shap_e.py，和shap_e文件夹放在一起（就可以"from shap_e.diffusion.xxx import"了）
# 5、在shap_e.py所在文件夹下运行: python shap_e.py（会新建shap_e_model_cache文件夹，并生成3G左右的3D模型有关文件；随后如果调用cpu则运行过程将长达数个小时（如果调用高档GPU，可以几分钟内完成））
# 6、关于部署：服务器上要租用GPU通常非常昂贵，如果家里有含GPU的PC，由于固定域名等问题，可以考虑家里PC以client方式向服务器后台发起request并让server逆向调用GPU资源。（类似微软开源的visual-gpt也可考虑这样部署）