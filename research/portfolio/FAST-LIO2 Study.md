---
title: FAST-LIO2 — Understanding LiDAR–Inertial Odometry
excerpt: A focused study of direct scan-to-map matching, IMU motion compensation, and incremental mapping, with assumptions and limits made explicit.
tags: [DCLab, Research & Study Notes, Robotics, Localization, FAST-LIO2]
publish: true
---
# FAST-LIO2 — Understanding LiDAR–Inertial Odometry

By Chheng Lydiya

## The question

How can a moving robot estimate its position and orientation from LiDAR scans and IMU measurements without first extracting hand-designed edge features?

This is a reading study connected to my DCLab robotics work. My contribution here is explaining the method and its engineering assumptions. FAST-LIO2 is the work of Wei Xu, Yixi Cai, Dongjiao He, Jiarong Lin, and Fu Zhang; this article presents no new algorithm or independently measured benchmark.

## Following the estimate

FAST-LIO2 combines an iterated Kalman filter with direct registration of LiDAR points against a map. IMU propagation supplies a motion estimate and supports scan de-skewing. The filter then uses point-to-plane residuals to refine the state.

Its incremental k-d tree, **ikd-Tree**, supports map-point insertion, deletion, downsampling, and rebalancing. This makes map maintenance part of the estimation loop rather than rebuilding a static search structure for every scan. See the [original paper, sections III–V](https://arxiv.org/html/2107.06829v1).

## What the inputs must mean

The implementation documentation emphasizes synchronized LiDAR and IMU measurements, usable per-point timestamps, and the transform between the sensors. These are prerequisites for interpreting motion consistently, not optional details to fix after a map looks wrong. See the [official implementation's sensor guidance](https://github.com/hku-mars/FAST_LIO#3-directly-run).

## Reading the evidence

The paper evaluates accuracy and processing time across datasets and hardware. Those measurements belong to the authors' experiments. A published rate is not a performance promise for a different sensor, computer, or scene. See [the benchmark and experiment sections](https://arxiv.org/html/2107.06829v1#S6).

## What I take into further work

The scope is pose estimation and mapping. Driving motors, following waypoints, avoiding obstacles, and planning routes require other parts of a robot system. Local odometry also needs separate global constraints if long-term drift is to be corrected.

My next evaluation questions are whether a stationary estimate stays stable, how it follows a measured trajectory, and what changes when timing or scene geometry becomes less favorable. I would report the setup and reference measurements alongside any accuracy claim.

For the broader localization questions that motivated this study, read [Localization with Livox MID-360 — A Study of the Options](Livox%20MID-360%20Localization%20Study.md). Related work appears on my [robotics portfolio](https://chheng-lydiya-portfolio.vercel.app/#/projects).
