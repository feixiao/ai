## Spleeter

### 安装和使用

1. Install TF using Rosetta using the guide here:

https://drive.google.com/drive/folders/1oSipZLnoeQB0Awz8U68KYeCPsULy_dQ7?usp=sharing

2. git clone https://github.com/Deezer/spleeter && cd spleeter
3. pip install poetry
4. in pyproject.toml, change tensorflow version to TF version installed on Rosetta (us: TF 2.4.1)
5. run: poetry update requests toml (change numpy versions in pyproject.toml if need be; for us "<1.20.0,>=1.19.2")
6. poetry install
7. poetry build
8. pip install dist/spleeter-2.2.2-py3-none-any.whl (uninstall local spleeter version beforehand)

And voila! Run "spleeter separate -p spleeter:2stems -o output audio_example.mp3" to check spleeter setup.

```shell
python3.8 -m pip install spleeter
spleeter separate -p spleeter:2stems -o output test.mp3

# illegal hardware instruction
https://github.com/deezer/spleeter/issues/607
```
