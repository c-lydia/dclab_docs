---
title: Localization with Livox MID-360 — A Study of the Options
excerpt: Comparing the roles of LiDAR odometry, map-based relocalization, and sensor fusion while studying localization for mobile robots.
tags: [DCLab, Research & Study Notes, Robotics, Localization, Livox]
publish: true
---
# Localization with Livox MID-360 — A Study of the Options

By Chheng Lydiya

## The question

How should I approach localization with a 3D LiDAR such as the Livox MID-360?

This literature study grew from my DCLab robotics work. It compares the responsibilities and assumptions of several approaches; it is not a hardware benchmark or a claim that every package listed here works unchanged with the MID-360.

## Separate the jobs

My reading questions fall into three groups: estimating motion as new scans arrive, locating the sensor in an existing map, and combining estimates from other sensors. Keeping those questions separate helps me decide what evidence to look for in each package.

| Approach | What I am studying | Compatibility or evaluation question |
| --- | --- | --- |
| FAST-LIO2 | Direct LiDAR–inertial estimation and incremental mapping | Are sensor timing, message fields, and extrinsics configured for the selected implementation? |
| LIO-SAM | Factor-graph estimation combining LiDAR and IMU information, with GPS constraints available | Does the chosen implementation support the sensor's scan format and IMU? |
| Livox relocalization | Matching against an existing map | How close must the initial pose be, and what sensor produced the map? |

FAST-LIO2's direct registration and incremental map structure led me to a [separate focused study](FAST-LIO2%20Study.md). The algorithm and implementation are credited to their [original authors](https://github.com/hku-mars/FAST_LIO).

## Check assumptions before comparing results

The original LIO-SAM documentation requires point timing and ring information and describes specific IMU expectations. It also distinguishes its original ROS implementation from its ROS 2 branch. I treat it as an architectural reference here, rather than assuming the original setup transfers directly to MID-360. See [LIO-SAM's sensor requirements](https://github.com/TixiaoShan/LIO-SAM#prepare-lidar-data).

Livox's relocalization example loads a map made with a Mid-40. Its documentation says the initial pose must remain close to the original trajectory, particularly in rotation. That makes it useful for understanding map-based localization, while leaving sensor adaptation and initialization as separate questions. See [Livox relocalization](https://github.com/Livox-SDK/livox_relocalization).

## What I would evaluate next

For a MID-360 implementation, I would record the exact software version, sensor configuration, timing, and frame conventions, then compare estimates against a known trajectory. Stationary stability, drift over a route, initialization failures, and processing time would answer different parts of the question.

The main takeaway from this study is a clearer evaluation plan: establish the role of each estimator, verify its input assumptions, and distinguish published results from measurements on my own setup. Related engineering work is on my [robotics portfolio](https://chheng-lydiya-portfolio.vercel.app/#/projects).
