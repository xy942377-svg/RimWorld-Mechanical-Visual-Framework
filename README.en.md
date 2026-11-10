# RimWorld Mechanical Visual Framework

[中文首页](README.md) · [Quick start](docs/quickstart.en.md) · [Model format](docs/model-format.en.md) · [API](docs/api.en.md) · [Maintenance guide](docs/handoff.en.md)

This framework displays moving mechanical models in RimWorld. Mod authors can set a pivot for each part and create turret turning, barrel elevation and recoil, lifting platforms and folding mechanisms. Parent-child relationships keep attached parts together: a barrel moves with the turret it is mounted on.

At runtime, the framework projects the 3D model onto the map using each part's current position and angle. It shades each face according to its orientation and draws thick outlines.

Framework version: **0.1.0-candidate1**, for RimWorld **1.6 / 1.7**. Package revision **workshop1** adds the Workshop cover, bilingual listing descriptions and upload instructions. Author: Grey·Oviin/OpenAI Assisted.

## Download and install

- [Runtime](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-workshop1-Workshop.zip): extract the `MechanicalVisualFramework` folder into the game's `Mods` directory.
- [Animation examples](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-workshop1-Examples.zip): extract `RMVFExamples` into `Mods` to try the rotating arm, lifting and folding mechanism, and triple turret.
- **Full authoring project:** use **Code → Download ZIP** on this repository page for sources, models, tools and tutorials. Extract the download before running the tools.

Load **Core → Mechanical Visual Framework → RMVF · Mechanical examples**. The runtime requires Core; the examples require the framework. The framework supplies rendering and animation, while mods using it add buildings and gameplay.

The Steam Workshop listing has not yet been published. Downloads are available in this repository.

## Try the examples and create a model

Build examples under **Misc**, select a building and open **Animation controls**. The triple turret demonstrates continuous turning, independent elevation of its three barrels and recoil. It does not fire projectiles.

To make your own mod:

1. Download and extract the full project. On Windows, double-click `Start.cmd` to open the toolbox.
2. Choose **Configure paths** and enter your Python executable, such as `C:/Python312/python.exe`.
3. Open the toolbox again and choose **New mod**. Enter the new mod's output directory, unique package ID and name.
4. Edit `Authoring/model.json` in the generated mod. Use the command in the [quick start](docs/quickstart.en.md) to generate the files the game reads.
5. Put the new mod in the game's `Mods` directory and enable it after the framework. Restart the game after rebuilding changed model assets.

Players can use the precompiled runtime files. Model authoring needs Python 3.10+; changing framework C# sources also requires Roslyn and the matching game assemblies. The toolbox uses English. Game buttons and descriptions are available in English and Simplified Chinese.

## Features and examples

| Feature | Purpose |
|---|---|
| Parts and pivots | Parent-child relationships, local coordinates and independent rotation centers |
| Animation parameters | Turn speed, elevation, translation and uniform scaling |
| Clips | Playback, looping, pausing and concurrent clips using separate parameters |
| API and saves | Gameplay-driven animation, anchors such as muzzles, and saved pose and playback state |
| Authoring tools | Mod generation, JSON compilation, supported GLB import, validation and packaging |
| In-game examples | Rotating arm with 100 triangles, folding mechanism with 380, and triple turret with 5344 |
| [Shield modeling case](Modeling/ShieldGenerator/README.en.md) | Four corners built from one shared part, with separate base and orb exports |

The framework suits machines made from rigid parts. Parts can rotate, translate and scale; skinning, flexible deformation and inverse kinematics are not implemented. The consuming mod implements firing, power generation and shield interception. See the [GLB import steps](docs/quickstart.en.md#4-import-from-modeling-software) for supported input.

## Documentation and license

All detailed guides have Chinese and English versions. Use the link at the top of each page to switch languages.

| Guide | Contents |
|---|---|
| [Quick start](docs/quickstart.en.md) | Installation, creating a mod, editing models and importing GLB |
| [Model format](docs/model-format.en.md) | Coordinates, hierarchy, parameters, clips and compiled assets |
| [API](docs/api.en.md) | Gameplay calls, anchors, resource ownership and saving |
| [Architecture](docs/architecture.en.md) | Loading, animation, rendering buffers and performance measurement |
| [Maintenance guide](docs/handoff.en.md) | Environment setup, builds, tests and maintenance conventions |
| [Releases and downloads](docs/release.en.md) | Getting files, packaging and Workshop publication |
| [Current status](docs/status.en.md) | Version, publication status and further work |
| [Verification record](docs/verification.en.md) | Test environments, checks and verified scope |

`Mod/` contains the framework and its sources; `Examples/` contains the game examples; `Authoring/` contains their source models; `Modeling/` contains modeling cases; `Templates/` supplies a starter model; `Tools/` contains authoring tools; `docs/` and `Verification/` contain guides and tests.

Original code, tools, documentation and examples use [MIT](LICENSE). Modification, redistribution and reuse in other mods are allowed with the copyright and license notices retained. See [NOTICE](NOTICE.md) for attribution and the [verification record](docs/verification.en.md) for tested versions and scope.
