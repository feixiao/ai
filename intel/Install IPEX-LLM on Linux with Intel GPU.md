### Install IPEX-LLM on Linux with Intel GPU
##### 平台
Ubuntu 22.04

##### 下载Intel GPU驱动
```shell
sudo apt-get install -y gpg-agent wget
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
sudo gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg

echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy client" | \
sudo tee /etc/apt/sources.list.d/intel-gpu-jammy.list

sudo apt-get update

# Install out-of-tree driver
sudo apt-get -y install \
    gawk \
    dkms \
    linux-headers-$(uname -r) \
    libc6-dev
sudo apt install intel-i915-dkms intel-fw-gpu


sudo apt-get install -y udev \
    intel-opencl-icd intel-level-zero-gpu level-zero \
    intel-media-va-driver-non-free libmfx1 libmfxgen1 libvpl2 \
    libegl-mesa0 libegl1-mesa libegl1-mesa-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri \
    libglapi-mesa libgles2-mesa-dev libglx-mesa0 libigdgmm12 libxatracker2 mesa-va-drivers \
    mesa-vdpau-drivers mesa-vulkan-drivers va-driver-all vainfo
    
sudo reboot



# 配置权限
sudo gpasswd -a ${USER} render
newgrp render

# Verify the device is working with i915 driver
sudo apt-get install -y hwinfo
hwinfo --display
```

#### 验证
```shell
conda create -n llm python=3.11
conda activate llm
pip install --pre --upgrade "ipex-llm[xpu]" --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/cn/

python -m pip install torch==2.1.0.post2 torchvision==0.16.0.post2 torchaudio==2.1.0.post2 intel-extension-for-pytorch==2.1.30.post0 oneccl_bind_pt==2.1.300+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/

source /opt/intel/oneapi/setvars.sh

python
> from ipex_llm.transformers import AutoModel, AutoModelForCausalLM

# 没有报错就正常了
```

#### Runtime Configurations
```shell
 Configure oneAPI environment variables. Required step for APT or offline installed oneAPI.
# Skip this step for PIP-installed oneAPI since the environment has already been configured in LD_LIBRARY_PATH.
source /opt/intel/oneapi/setvars.sh

# Recommended Environment Variables for optimal performance
export USE_XETLA=OFF
export SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
export SYCL_CACHE_PERSISTENT=1
```

#### 准备demo
```python
# Copy/Paste the contents to a new file demo.py
import torch
from ipex_llm.transformers import AutoModelForCausalLM
from transformers import AutoTokenizer, GenerationConfig
generation_config = GenerationConfig(use_cache = True)

tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b", trust_remote_code=True)
# load Model using ipex-llm and load it to GPU
model = AutoModelForCausalLM.from_pretrained(
    "tiiuae/falcon-7b", load_in_4bit=True, cpu_embedding=True, trust_remote_code=True)
model = model.to('xpu')

# Format the prompt
question = "What is AI?"
prompt = " Question:{prompt}\n\n Answer:".format(prompt=question)
# Generate predicted tokens
with torch.inference_mode():
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to('xpu')
    # warm up one more time before the actual generation task for the first run, see details in `Tips & Troubleshooting`
    # output = model.generate(input_ids, do_sample=False, max_new_tokens=32, generation_config = generation_config)
    output = model.generate(input_ids, do_sample=False, max_new_tokens=32, generation_config = generation_config).cpu()
    output_str = tokenizer.decode(output[0], skip_special_tokens=True)
    print(output_str)
```

#### 运行demo
```shell
conda activate llm
python demo.py
```

#### 参考资料
+ [《Install IPEX-LLM on Linux with Intel GPU》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/install_linux_gpu.md)