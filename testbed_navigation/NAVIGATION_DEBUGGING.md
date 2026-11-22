# Navigation debugging notes

See `../../RELIABILITY_FIXES.md` for the full source-level investigation,
including the Gazebo `test_room` world-pose discrepancy and the revised
validation commands.

The global planner has been observed returning exact goal endpoints, while
AMCL's estimated map pose differed by 13–16 cm from Gazebo world position.
A wall/map alignment bug was identified and corrected in the world file.
The previous DWB experiment and subsequent RPP experiment both reproduced
near-goal failures **before the world alignment correction**, so neither
controller alone explained the behavior.

The current navigation configuration uses RPP, a non-stateful 5 cm XY and
0.1 rad yaw checker, and an angular-aware `PoseProgressChecker`. It must
be tested after a full Gazebo restart. Never infer 5 cm physical accuracy
from `FollowPath` action success alone.
