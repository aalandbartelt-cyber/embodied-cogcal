# Derived public-data images

The seven PNG sheets in `visual/` derive from Armnet's public ArmnetBench v0.1 SO-101 dataset:
https://huggingface.co/datasets/armnet/armnetbench_v01_lerobot_so101/tree/1db69c82b589c7172ee31a6b8f7ef58d1fc2c663

The pinned dataset card declares Apache-2.0; the source license is included as
`LICENSE-data-Apache-2.0.txt`. These images are not relicensed under the repository's MIT license.
Modifications: fixed 3-second grid frame extraction plus author-trimmed final frames,
resizing, arrangement, and episode/time/camera labels. No generated or altered objects/robots.
The original outcome labels remain the dataset operator's labels.

`samples-manifest.json` binds the exact source videos, PTS, native frame hashes and sheets.
Original video and native frames stay in ignored cache. These are existing public robot
records, not new hardware trials conducted by this project.
