
![Saibyo Logo](/assets/images/saibyo-logo.png)



<p align="center">
  <!-- PyPI -->
  <a href="https://pypi.org/project/saibyo/">
    <img src="https://img.shields.io/pypi/v/saibyo?logo=pypi&logoColor=white&label=PyPI&style=for-the-badge" alt="PyPI Version"/>
  </a>
  <!-- Release -->
<a href="https://github.com/alrodsa/saibyo/releases">
  <img src="https://img.shields.io/github/v/release/alrodsa/saibyo?label=Release&logo=github&logoColor=white&style=for-the-badge" alt="Latest Release"/>
</a>
  <!-- Coverage -->
  <a href="https://codecov.io/gh/alrodsa/saibyo">
    <img src="https://img.shields.io/codecov/c/github/alrodsa/saibyo?logo=codecov&logoColor=white&style=for-the-badge" alt="Coverage"/>
  </a>
  <!-- Python version -->
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white&style=for-the-badge" alt="Python Version"/>
  <!-- Linter -->
  <img src="https://img.shields.io/badge/linter-ruff-yellow?logo=ruff&logoColor=white&style=for-the-badge" alt="Linter"/>
  <!-- Lint -->
  <a href="https://github.com/alrodsa/saibyo/actions/workflows/python-ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/alrodsa/saibyo/python-ci.yml?branch=main&label=Lint&logo=github&logoColor=white&style=for-the-badge" alt="Lint Status"/>
  </a>
  <!-- CI workflow -->
  <a href="https://github.com/alrodsa/saibyo/actions/workflows/python-ci.yml">
  <img src="https://img.shields.io/github/actions/workflow/status/alrodsa/saibyo/python-ci.yml?label=CI&logo=githubactions&logoColor=white&style=for-the-badge" alt="CI Status"/>
  </a>
  <!-- License -->
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-green?logo=open-source-initiative&logoColor=white&style=for-the-badge" alt="License: MIT"/>
  </a>
  <!-- Demo Video -->
  <a href="https://youtu.be/NByIRUQXoUE">
    <img src="https://img.shields.io/badge/Video-Demo-red?logo=youtube&logoColor=white&style=for-the-badge" al
    t="Demo Video"/>
  </a>
</p>


![Saibyo Demo](/assets/images/demo.gif)

> ⚠️ **IMPORTANT:** Above gif could not show the full potential of Saibyo fps boost,
check out the video for a better understanding in the [YouTube Demo](https://youtu.be/NByIRUQXoUE).

> 📝 **NOTE:** It is important to mention that due to youtube restrictions, the maximum fps of a video is 60fps. Even do, you will be able to feel the difference in smoothness with higher fps videos.

## 📖 Overview

**_Saibyo_**[^1] is a **deep learning video frame interpolation library** built on top of **RIFE** and `PyTorch`, enabling fast FPS upscaling, slow-motion generation and visual comparison tools.

[^1]: The name comes from stylized Japanese components: **Sai** (彩 / 再), which can evoke “color,” “detail,” or “redo”; and **Byō** (描 / 秒), which can suggest “to draw” or even “second (fps).” Combined, **Saibyo** roughly conveys the idea of “redrawing the seconds,” which aligns perfectly with a system focused on frame interpolation and visual refinement.

### What Saibyo offers:

- **Easy-to-use CLI and Python API** for video frame interpolation.
- **Multiple configuration options**: config files, environment variables, direct parameters.
- **Built-in comparison modes** to visualize interpolation results.
- **Extensible architecture** for future models and features.


## 🚀 Installation

Saibyo has been published to `PyPI` to facilitate easy installation. It can be installed using `pip` command:

```bash
pip install saibyo
```

> 📚 For more installation documentation, including optional dependencies and troubleshooting, check out the installation guide located at [`docs/installation.md`](docs/installation.md)


## ⚡ Quick Usage

There are two primary ways to use Saibyo: via the Command Line Interface (CLI) or through the Python API.

### Command Line Interface (CLI)

Once Saibyo is installed, you can use the `saibyo` command in your terminal to interpolate a video. The basic syntax is as follows:

```bash
saibyo interpolate video.mp4 output_directory/
```

By default, the name of the output file will be
```{original_video_name}_x{fps_multiplier}_{new_fps}.mp4```, where `fps_multiplier` is the factor by which the original FPS is increased.

> 📚 For more CLI options and usage examples, refer to the CLI documentation at [`docs/cli.md`](docs/cli.md)

### Python API

Saibyo can also be integrated into Python scripts for more customized workflows. Here is a simple example of how to use the Python API to interpolate a video:

```python
from saibyo.base.conf.app import configure
from saibyo.conf.conf import SaibyoConf
from saibyo.constants.app import APP_NAME, ROOT_DIR
from saibyo.core.interpolation.rife import RifeInterpolator

conf = configure(APP_NAME, ROOT_DIR, SaibyoConf)
Interpolator(conf).run(
    input_path=input_path,
    output_folder=output_folder,
)
Comparator(conf.comparator).compare(
    video_a=input_path,
    video_b=output_path,
    output_path="path/to/comparison_output.mp4"
```

> 📚 For more Python API options, refer to the Python API documentation [`docs/python-api.md`](docs/python-api.md) and [`docs/comparison-modes.md`](docs/comparison-modes.md)

## ⚙️ Configuration

By default, Saibyo uses parameters preset in the `Pydantic` configuration schemas located in `saibyo/conf/conf.py`. These parameters can be overridden using:

- Environment variables.
- Setting values directly to `SaibyoConf` instance.

> 📚 For more detailed configuration options, refer to the configuration documentation at [`docs/configuration.md`](docs/configuration.md)

## 🎨 Comparison Modes

Saibyo includes built-in comparison utilities, allowing users to visualize the differences between the original and interpolated videos. The available comparison modes are:

- side_by_side
- top_bottom
- split_half_vertical
- split_half_horizontal

> 📚 For more detailed comparison mode options and how to run this command, refer to the comparison modes documentation at [`docs/comparison-modes.md`](docs/comparison-modes.md)

## 🗺️ Roadmap

Planned features and improvements for future releases include:

### ONNX inference

Actually, Saibyo uses `PyTorch` for model inference, that makes it less portable to other platforms, more resource-demanding and harder to deploy in cloud environments. `ONNX` is an open format built to represent machine learning models, that allows models to be used across different frameworks and platforms. This feature will enable:

- Lighter models.
- Easier deployment.
- Broader compatibility.

### Batching support

Currently, Saibyo processes videos taking one pair of frames at a time, which can be inefficient for longer videos or higher resolutions. Batching support will allow the processing of multiple frame pairs simultaneously, leading to:

- Improved performance.
- Reduced processing time.
- Better resource utilization.

### Advanced ML models (IFRNet, FLAVR)

Expanding the range of supported machine learning models for frame interpolation will provide users with more options to choose from, depending on their specific needs and preferences. This will include:

- Integration of state-of-the-art models like IFRNet and FLAVR.
- Enhanced interpolation quality.
- More customization options for users.

### Output video compression

To optimize storage space and improve video playback performance, Saibyo will introduce options for compressing output videos without significant loss of quality. This feature will offer:

- Various compression algorithms.
- User-defined quality settings.
- Reduced file sizes.

## 📄 License

Saibyo is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## 👤 Author

- **Alvaro R.** - [alrodsa](https://github.com/alrodsa)
