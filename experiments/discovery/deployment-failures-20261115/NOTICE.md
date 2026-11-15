# Derived data images

The three PNG contact sheets in `visual/` are derived from the public ArmnetBench v0.1
single-arm SO-101 dataset, published by Armnet:

https://huggingface.co/datasets/armnet/armnetbench_v01_lerobot_so101/tree/1db69c82b589c7172ee31a6b8f7ef58d1fc2c663

The pinned dataset card declares Apache-2.0. The license text is included in
`LICENSE-data-Apache-2.0.txt`; these source images are not relicensed under this
repository's MIT software license.

Modifications: fixed-time frame extraction, resizing, arrangement into contact
sheets, and labels showing dataset episode/outcome/time. No image generation or
object/robot alteration was performed. Outcomes are the dataset operator's labels.

`visual-samples-manifest.json` binds the source video, exact samples and hashes.
The original video, native extracted frames, third-party papers and source code
remain in the ignored research cache. This is an analysis of public records, not a
claim that embodied-cogcal conducted these real-robot trials.
