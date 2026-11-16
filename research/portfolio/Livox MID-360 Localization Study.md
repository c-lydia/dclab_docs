---
title: Localization with Livox MID-360 — A Study of the Options
excerpt: A technical comparison of LiDAR odometry, relocalization, and sensor fusion, with scan-matching equations, IMU preintegration, worked examples, and an evaluation plan for MID-360.
tags: [DCLab, Research & Study Notes, Robotics, Localization, Livox]
publish: true
---
# Localization with Livox MID-360 — A Study of the Options

By Chheng Lydiya

## The question

How can a mobile robot estimate its position and orientation with a 3D LiDAR such as the Livox MID-360, and which parts of that problem do different localization methods actually solve?

This is a technical reading study developed from my DCLab notes. My contribution is the comparison, explanation, and mathematical checks. The cited algorithms belong to their original authors. The calculations below are illustrative; this article does not report a comparative hardware benchmark or claim that every package works unchanged with MID-360.

## Pose, odometry, and a map reference

A spatial pose contains three translation and three rotation degrees of freedom. One convenient representation is $T=(R,t)\in SE(3)$, with $R\in SO(3)$ and $t\in\mathbb R^3$. A LiDAR return $p_L$ becomes a point in a world or map frame through

$$
p_W=R p_L+t.
$$

The frame labels matter as much as the numbers. A consistent estimate relative to the sensor's starting pose does not automatically give a position in an existing building map.

I separate three tasks when reading the methods:

- **Odometry:** estimate motion as measurements arrive. Error can accumulate over time.
- **Map-based localization:** align measurements with a known map, including an initial-pose or relocalization problem.
- **Sensor fusion:** combine available measurements or estimates while respecting their frames, timestamps, and uncertainty.

Mapping constructs or updates the representation against which scans are compared. Loop closure adds a constraint when a place is revisited. These pieces can be combined, but choosing a Kalman filter or a factor graph does not by itself supply missing global information.

## Comparing the approaches

| Approach | Main idea in this study | What needs separate attention |
| --- | --- | --- |
| LOAM-Livox | Odometry and mapping designed around small-field-of-view, irregularly sampled LiDAR data | Scene geometry, feature quality, and differences between the studied sensor and MID-360 |
| FAST-LIO2 | Direct scan-to-map registration with LiDAR–IMU estimation and an incremental map structure | Timing, extrinsics, initialization, and long-term drift |
| LIO-SAM | A factor graph combining LiDAR and IMU constraints, with GPS and loop-closure factors | Sensor/IMU requirements and which global constraints are actually present |
| Livox relocalization | Matching against an existing map | Map compatibility and a sufficiently close initial pose |
| `robot_localization` | EKF/UKF fusion of supported state measurements | Measurement selection, covariance, frames, and correlated inputs |

The [LOAM-Livox paper](https://arxiv.org/abs/1909.06700) is relevant to the effects of irregular sampling and limited visible geometry. Its sensor setting should not be treated as a MID-360 specification. The [LIO-SAM paper](https://arxiv.org/abs/2007.00258) provides a contrasting formulation in which multiple measurement sources constrain a trajectory through a graph.

## From a scan to a pose constraint

A useful way to study the front end is to follow the data through four stages.

1. **Select usable returns.** Feature-based methods identify local edges or planar regions; direct methods can avoid a separate hand-designed feature extraction stage. Either way, invalid returns and unsuitable correspondences must be handled.
2. **Compensate motion within the scan.** Points arrive at different times. A motion estimate brings them into a common temporal frame before registration.
3. **Associate points with map geometry.** Nearest-neighbor search supplies candidates, but proximity alone is not proof that they represent the same surface.
4. **Update the pose or state.** Residuals express geometric disagreement. Optimization or filtering combines them with other information and uncertainty.

The distinction between feature-based and direct registration is not the presence or absence of geometry. A direct point-to-plane method still needs local surface information to build its residuals. My [FAST-LIO2 study](FAST-LIO2%20Study.md) develops that case in more detail.

## Geometry and notation

For a point $p=[x,y,z]^T$ expressed in meters, its distance from the sensor origin is

$$
D(p)=\sqrt{x^2+y^2+z^2}.
$$

The angle away from the positive $x$ axis can be written as

$$
\phi(p)=\operatorname{atan2}\left(\sqrt{y^2+z^2},x\right).
$$

The square root is necessary: both arguments of $\operatorname{atan2}$ have units of length. The direction is undefined at the origin. This is an angle relative to a coordinate axis; a beam's incidence angle additionally requires the orientation of the surface it hits.

### Point-to-line distance

Let $p_W$ be a transformed scan point and $a,b$ two distinct points defining a map line. The perpendicular distance is

$$
r_{\mathrm{line}}=
\frac{\|(p_W-a)\times(p_W-b)\|}{\|b-a\|}.
$$

The numerator has units of square meters and the denominator meters, so the residual is a distance. The denominator must be nonzero. In practice, neighboring points should support a line fit; merely choosing two neighbors does not establish that a stable edge exists.

### Point-to-plane distance

Let $a,b,c$ be non-collinear map points. Define the unit normal

$$
n=\frac{(b-a)\times(c-a)}{\|(b-a)\times(c-a)\|}.
$$

Then the signed distance from $p_W$ to the plane is

$$
r_{\mathrm{plane}}=n^T(p_W-a).
$$

Reversing the normal reverses the sign but not the magnitude. Nearly collinear points make the normal poorly determined. A fitted neighborhood with a planarity check is more meaningful than assuming any nearby triple is a reliable surface. These distance relationships are the geometric basis for the scan-matching discussion in [LIO-SAM, section III-C](https://arxiv.org/html/2007.00258v3#S3.SS3).

### Worked check: what one plane tells us

Choose $a=[0,0,0]^T$, $b=[1,0,0]^T$, and $c=[0,1,0]^T$ meters. The normal is $n=[0,0,1]^T$. For $p_W=[0.4,0.2,0.05]^T$ meters,

$$
r_{\mathrm{plane}}=0.05\,\mathrm{m}.
$$

A vertical correction can reduce this residual. A horizontal displacement leaves it unchanged. Even many perfect observations of this same plane do not directly determine translation parallel to it. More points can improve a constrained direction without making every other direction observable.

For a line along the $x$ axis with $a=[0,0,0]^T$ and $b=[1,0,0]^T$, the point $[0.5,0.2,0]^T$ has a line distance of $0.2\,\mathrm{m}$. Translating it along the line does not change that distance. These examples explain why the arrangement of scene geometry matters, not just the number of returns.

## IMU motion compensation and preintegration

The IMU measures angular velocity and specific force at a higher temporal resolution than a complete scan. Its measurements can supply a motion prediction for de-skewing. This requires consistent timestamps, sensor-frame calibration, and a model of bias and noise.

An illustrative timing check: at a constant angular speed of $90^\circ/\mathrm{s}$, a timestamp offset of $0.01\,\mathrm{s}$ corresponds to an orientation mismatch of $0.9^\circ$, or about $0.0157$ radians. At a range of $5\,\mathrm{m}$, the small-angle lateral displacement is roughly

$$
e\approx d\,\delta\theta=5(0.0157)\approx0.079\,\mathrm{m}.
$$

That calculation isolates a timing effect; it is not a prediction of total localization error or a MID-360 measurement.

### Relative motion between two times

Let $R_i,p_i,v_i$ and $R_j,p_j,v_j$ be world-frame orientations, positions, and velocities at times $i$ and $j$. Let $\Delta t=t_j-t_i$ and $g$ be the world-frame gravity vector. Under the usual constant-gravity model, the ideal relative quantities are

$$
\Delta R_{ij}=R_i^T R_j,
$$

$$
\Delta v_{ij}=R_i^T(v_j-v_i-g\Delta t),
$$

$$
\Delta p_{ij}=R_i^T\left(p_j-p_i-v_i\Delta t-\frac12g\Delta t^2\right).
$$

These express the endpoint relationships against which IMU-derived quantities can be compared. Actual preintegration also carries bias dependence and uncertainty; these three equations are not a complete preintegration implementation. See [LIO-SAM, section III-B](https://arxiv.org/html/2007.00258v3#S3.SS2).

The gravity term in the velocity equation is $g\Delta t$, with units of meters per second. The position equation uses $\tfrac12g\Delta t^2$, with units of meters. This dimensional check prevents accidentally carrying the squared time term into the velocity relationship.

For an ideal stationary, level sensor with $R_i=I$, $g=[0,0,-9.81]^T\,\mathrm{m/s^2}$, zero endpoint velocity, and $\Delta t=0.1\,\mathrm{s}$, the equations give

$$
\Delta v_{ij}=[0,0,0.981]^T\,\mathrm{m/s},\qquad
\Delta p_{ij}=[0,0,0.04905]^T\,\mathrm{m}.
$$

Those nonzero preintegrated quantities are consistent with the accelerometer's upward specific force while stationary. They are not the sensor's world-frame displacement. Restoring the gravity terms in the endpoint equations gives zero motion.

## Filter fusion and graph constraints

An EKF or UKF recursively maintains a state estimate and covariance. A factor graph represents states and the measurements constraining them; suitable optimization can revise a connected trajectory as constraints arrive. These are estimation formulations, not guarantees of accuracy.

The `robot_localization` EKF/UKF state includes 15 variables: position, orientation, linear velocity, angular velocity, and linear acceleration. Written with angular-velocity components $\omega_x,\omega_y,\omega_z$, it is

$$
x=\left[x,y,z,\phi,\theta,\psi,
 v_x,v_y,v_z,\omega_x,\omega_y,\omega_z,
 a_x,a_y,a_z\right]^T.
$$

The package consumes supported pose, twist, odometry, and IMU messages. It does not perform point-cloud registration itself. Its state is also different from the LiDAR–IMU bias/gravity/extrinsic state discussed in the FAST-LIO2 study. See the [official package documentation source](https://github.com/cra-ros-pkg/robot_localization/blob/noetic-devel/doc/index.rst).

A fusion design should explain where each input came from. For example, treating an odometry estimate and the same IMU already used to generate it as independent evidence can misrepresent uncertainty if their correlation is ignored. More input topics do not automatically mean more independent information.

## Compatibility and failure modes

The original [LIO-SAM implementation](https://github.com/TixiaoShan/LIO-SAM#prepare-lidar-data) documents point timing, ring information, and IMU requirements. A method-level comparison is therefore not a claim that its original input pipeline accepts MID-360 data unchanged; the exact branch or adaptation must be checked.

[Livox relocalization](https://github.com/Livox-SDK/livox_relocalization) demonstrates localization with a Mid-40 map and requires an initial pose near the original trajectory, especially in rotation. This is different from unrestricted global localization from an arbitrary unknown pose.

Other failure modes follow directly from the assumptions:

- A corridor or dominant plane can leave some motion directions weakly constrained.
- Moving objects can produce correspondences inconsistent with a static map.
- Incorrect extrinsics can turn rotation into apparent translation.
- Incorrect timing can distort the geometry before matching begins.
- A smooth-looking trajectory can still drift when no independent reference constrains it.

## Interpreting performance evidence

The original papers use different sensors, trajectories, hardware, and available constraints. A processing rate, endpoint error, or drift percentage should remain attached to that experimental setup. For example, a result using GPS or loop closure does not establish the performance of an otherwise similar system without those constraints.

I would not rank the methods by combining headline numbers from separate papers. A controlled comparison needs the same inputs, a stated reference trajectory, the same alignment convention, and clear accounting of which measurements each method receives. A map that looks clean is useful qualitative evidence, but it is not an accuracy metric.

## Evaluation plan and open questions

| Experiment | What to record | Question it answers |
| --- | --- | --- |
| Stationary startup | Pose variation, initialization time, and failures | Does the estimator settle consistently? |
| Known translation and rotation | Reference pose, estimate, and timing | Does the trajectory follow measured motion? |
| Longer route with a return | Error along the route and at the endpoint | How does drift develop? |
| Repetitive or sparse geometry | Tracking loss and recovery behavior | Which scene assumptions are fragile? |
| Existing-map startup | Initial-pose offset and success/failure | What initialization range is usable? |
| Runtime under load | Latency distribution and queue growth | Does processing keep pace with incoming data? |

These experiments remain proposed work in this article. The remaining questions are how reliable local correspondences are in the intended scene, what independent position reference is available, and which software version supports the chosen sensor representation.

My current direction is to study FAST-LIO2's local estimator in depth while treating map-based initialization and global correction as separate design decisions. That is a study choice, not a claim that one method is universally best. Related engineering work is on my [robotics portfolio](https://chheng-lydiya-portfolio.vercel.app/#/projects).

## Reading map

- Jiarong Lin and Fu Zhang, [LOAM-Livox](https://arxiv.org/abs/1909.06700): small-field-of-view and irregular-sampling challenges.
- Wei Xu, Yixi Cai, Dongjiao He, Jiarong Lin, and Fu Zhang, [FAST-LIO2](https://arxiv.org/abs/2107.06829): direct registration and incremental mapping.
- Tixiao Shan, Brendan Englot, Drew Meyers, Wei Wang, Carlo Ratti, and Daniela Rus, [LIO-SAM](https://arxiv.org/abs/2007.00258): preintegration, scan matching, and factor-graph constraints.
- [Livox relocalization](https://github.com/Livox-SDK/livox_relocalization): an existing-map localization example and its initialization limits.
- [robot_localization documentation](https://github.com/cra-ros-pkg/robot_localization/blob/noetic-devel/doc/index.rst): state-estimation nodes and supported measurement types.
