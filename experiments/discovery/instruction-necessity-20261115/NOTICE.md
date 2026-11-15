# Third-party attribution for the recorded scene override

`physical/scene-override.xml` is a generated, flattened derivative of
`FERBIN12/so101-manipulation-eval` revision
`b02b8b2e300733dbe76cead4f3a57425c37955fe`, `assets/so101/sim_replay.xml`
and its included SO-101 model. The upstream project identifies its code as
MIT (copyright 2026 Ferbin Richard) and the SO-101 model/meshes as Apache-2.0
from TheRobotStudio/SO-ARM100. See the two license files in this directory.

Modifications on 2026-11-15: move the original cube's model default to the
fixed A initial position, add a second free cube with the same mass, size,
collision and contact-pair parameters and a green visual color, and serialize
the compiled MuJoCo specification. Robot kinematics and contact parameters
were preserved. No original upstream XML or meshes were changed.

Meshes are referenced from the fixed external checkout; they are not copied
here. The generated XML is an execution record. To rerun, use the runner,
which reads and verifies the original checkout and regenerates the scene.

The scoring probes load inspected Apache-2.0 definitions from fixed
HorizonRobotics/RoboOrchardSim sources cached outside version control.
Those external source files are not redistributed in this directory.
