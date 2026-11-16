---
title: FAST-LIO2 — Understanding LiDAR–Inertial Odometry
excerpt: A technical study of FAST-LIO2: motion compensation, manifold state estimation, point-to-plane residuals, Kalman updates, and incremental mapping, with worked examples and limitations.
tags: [DCLab, Research & Study Notes, Robotics, Localization, FAST-LIO2]
publish: true
---
# FAST-LIO2 — Understanding LiDAR–Inertial Odometry

By Chheng Lydiya

This study expands the theory in my DCLab research notes: how the measurements enter the estimator, what the equations mean, and where their assumptions can fail. The algorithm is the work of the authors cited below. My contribution here is the explanation, dimensional checks, and worked examples; the examples are illustrative calculations rather than hardware measurements.

## Question

How does Fast-LIO2 achieve real-time, highly accurate 3D LiDAR-Inertial state estimation and mapping without requiring hand-engineered feature extraction?

## Core idea

Fast-LIO2 is a direct, tightly-coupled LiDAR–Inertial Odometry framework that registers raw LiDAR points directly to a global or local map without extracting edge or planar features. It maintains large, dense point cloud maps using a dynamic Incremental KD-Tree (`ikd-Tree`) that supports point insertion, on-tree downsampling, lazy box-wise deletions, and parallel subtree re-balancing. State estimation is formulated on manifold spaces using a tightly-coupled iterated Extended Kalman Filter (iEKF) with a state-dimension Kalman gain computation that supports the authors’ reported odometry and mapping rates up to 100 Hz in their experiments. Those rates describe the authors’ experiments; a different sensor, computer, or point-cloud workload needs its own timing measurements.

## Method and assumptions

### Method

1. **IMU Propagation and Motion Compensation (De-skewing):** propagates the state forward using high-rate IMU measurements, then compensates scan points backward relative to the scan end-time using their individual sampling timestamps. This reduces motion distortion; it does not guarantee exact correction when measurements, calibration, or timing are imperfect.
2. **Direct raw Point Scan-to-Map Matching:** registers raw 3D points directly to the map via point-to-plane residual distances, removing hand-engineered feature extraction and adapting naturally to diverse spinning and solid-state scan patterns
3. **On-Manifold IEKF State Update:** propagates and updates system states directly on the manifold space $\mathcal{M} = SO(3) \times \mathbb{R}^{15} \times SO(3) \times \mathbb{R}^3$
4. **Dynamic Map Management (`ikd-Tree`):** organizes map points in a local cuboid with side length $L$ (the paper’s default evaluation uses $L=1000\,\mathrm{m}$). Deletes historical points falling outside the active map region via box-wise delete operations and inserts new points with on-tree spatial downsampling. Sub-tree re-balancing is offloaded to a parallel second thread to reduce blocking of the main thread

### Assumptions

- **Rigid Sensor Extrinsics and Timing:** the LiDAR and IMU are rigidly mounted. Their relative transform must be known or estimated, and point/IMU timestamps must have a consistent time base. The paper includes extrinsic estimation in the state. A known, fixed calibration and an estimated calibration represent different assumptions and should be reported explicitly.
- **Local Environmental Planarity:** neighboring map points locally approximate planar patches to support point-to-plane residuals. The scene also needs sufficient geometric constraints to observe motion; a dominant flat surface can leave some directions poorly constrained.

## Following one scan through the estimator

The IMU supplies a prediction between LiDAR updates. Because a scan is collected over an interval, its points were measured from different poses. De-skewing brings those points into a common reference time before map matching. Nearby map points provide local surface constraints; the iterated update combines those constraints with the predicted state and uncertainty. Accepted points then update the map used by the next scan.

This sequence matters when diagnosing an estimate. A poor map match may originate in timing or calibration before the matching step. Conversely, accurate timestamps cannot compensate for a scene that provides too little geometric information. The outline follows the method in the original notes; the following examples unpack the equations rather than presenting new experiments.

## Equations and notation

### Defined Symbols and Units

- $G$: global reference frame (coinciding with the initial IMU frame)
- $I$: IMU body frame
- $L$: local LiDAR sensor frame
- $T_{I}^{G} = (R_{I}^{G}, p_{I}^{G}) \in SE(3)$: IMU rotation matrix ($SO(3)$) and position vector ($\mathbb{R}^{3}$, meters) in the global frame
- $T_{L}^{I} = (R_{L}^{I}, p_{L}^{I}) \in SE(3)$: LiDAR-to-IMU extrinsic rotation matrix and translation vector
- $\mathbf{x} \in \mathcal{M}$: state on the paper’s 24-dimensional manifold $$\mathcal{M} = SO(3) \times \mathbb{R}^{15} \times SO(3) \times \mathbb{R}^{3}: \mathbf{x} = \left[R_{I}^{G}, p_{I}^{G}, v_{I}^{G}, b_{\omega}, b_{a}, g^{G}, R_{L}^{I}, p_{L}^{I}\right]^{T}$$
- $\mathbf{u} = \left[\omega_{m}^{T}, a_{m}^{T}\right]^{T}$: measured angular velocity ($rad/s$) and linear acceleration ($m/s^{2}$)
- $\mathbf{w} = [n_\omega^T, n_a^T, n_{b\omega}^T, n_{ba}^T]^T$: sensor measurement noise and bias random walk noise processes
- $^{L} p_j \in \mathbb{R}^3$: $j$-th measured 3D point in the local LiDAR frame $L$ (meters)
- $^{G} u_j \in \mathbb{R}^3$: unit normal vector of the corresponding local planar patch in global frame
- $^{G} q_j \in \mathbb{R}^3$: centroid point lying on the local planar patch in global frame

The two rotations each contribute three local degrees of freedom. The position, velocity, two bias vectors, and gravity contribute fifteen; extrinsic translation contributes three more. This is why the paper describes a 24-dimensional manifold even though rotation matrices contain nine entries each.

In the equations below, $a_m$ is the accelerometer's measured **specific force**, expressed in $\mathrm{m/s^2}$. Its frame and units matter: gravity enters separately after the measurement is rotated into the global frame.

### Formulations

#### Continuous Kinematic State Transition model

$$\dot{R}_I^G = R_I^G \lfloor \omega_m - b_\omega - n_\omega \rfloor_\wedge, \quad \dot{p}_I^G = v_I^G, \quad \dot{v}_I^G = R_I^G (a_m - b_a - n_a) + g^G \quad$$

Here $\lfloor\cdot\rfloor_\wedge$ turns an angular-velocity vector into its skew-symmetric matrix. The rotation derivative stays consistent with $SO(3)$; simply adding independent values to a rotation matrix would not preserve orthogonality.

As a sign check, consider an ideal stationary, level IMU with $R_I^G=I$ and $g^G=[0,0,-9.81]^T\,\mathrm{m/s^2}$. With zero bias and noise, its specific-force measurement is $[0,0,9.81]^T\,\mathrm{m/s^2}$. Substitution gives $\dot v=0$, as expected. Treating that measurement as already gravity-free and still adding $g^G$ would produce spurious acceleration.

#### Implicit Point-to-Plane Measurement Residual ($z_{j}$)

$$z_j = h_j(\hat{x}_k, 0) = {}^G u_j^T \left( \hat{R}_I^G \hat{R}_L^I {}^L p_j + \hat{R}_I^G \hat{p}_L^I + \hat{p}_I^G - {}^G q_j \right)$$

The subtraction of the plane point $q_j$ is **inside** the inner product, so $z_j$ is a scalar signed distance in meters. The residual at an estimated state is generally nonzero. The ideal noise-free constraint is zero; the iterated filter reduces the residual while accounting for the prior and measurement uncertainty. [Paper, §IV-B2, Eq. (9)](https://arxiv.org/html/2107.06829v1#S4.SS2.SSS2)

#### Worked example: a plane residual and what it cannot observe

Take a horizontal plane through $q=[0,0,0]^T$ with unit normal $u=[0,0,1]^T$. Suppose the transformed scan point is $p=[2,1,0.04]^T\,\mathrm{m}$. Then

$$
r=u^T(p-q)=0.04\,\mathrm{m}.
$$

Moving the point by $-0.04\,\mathrm{m}$ in the vertical direction makes this residual zero. Moving it horizontally changes neither the residual nor its derivative with respect to horizontal translation. This single measurement therefore constrains height but supplies no horizontal position information. Other surface orientations or other measurements are needed to constrain those directions.

The unit normal is essential: multiplying it by ten would multiply the residual by ten without changing the physical distance. A small residual is evidence of agreement with a surface, not proof that the complete pose is correct. This is a constructed geometry example, not a measured localization result.

#### State-Dimension Computationally Efficient Kalman Gain ($K$)

$$K = (H^T R^{-1} H + P^{-1})^{-1} H^T R^{-1} \quad$$

> Here $H$ is the stacked measurement Jacobian, $R$ the measurement-noise covariance, and $P$ the prior covariance expressed in the current error coordinates. The formula inverts a state-sized matrix instead of a measurement-sized matrix. For the manifold iteration, the prior covariance is transported into the current tangent coordinates; see the paper’s Eqs. (11)–(14).

To keep the symbols separate, $R$ in the gain formula denotes measurement covariance, whereas $R_I^G$ denotes orientation. If there are $m$ scalar residuals and $n$ error-state coordinates, then $H$ is $m\times n$, $P$ is $n\times n$, and $K$ is $n\times m$.

For example, a 24-coordinate state and 1,000 scalar residuals produce a $24\times24$ information matrix in the displayed inverse, rather than a $1,000\times1,000$ innovation matrix. This is a dimension comparison, not a measured speedup: constructing the residuals and Jacobians, searching the map, and solving the system still cost time. The expression also assumes usable inverse covariances; a numerical implementation normally solves linear systems rather than explicitly forming every inverse.

Iteration re-evaluates the nonlinear measurement around an updated estimate. It must retain the correct prior and covariance treatment rather than repeatedly count the same scan as independent new evidence.

#### `ikd-Tree` Balancing Criteria

Let $S(T)$ be the total node count of a subtree rooted at $T$, and $I(T)$ its invalid/deleted node count. The parameters below control structural balance and the tolerated proportion of deleted nodes.

- **$\alpha$-Balanced Criterion:** $S(T.\text{leftchild}) < \alpha_{\text{bal}} S(T) - 1$ and $S(T.\text{rightchild}) < \alpha_{\text{bal}} S(T) - 1$ (where $\alpha_{\text{bal}} \in (0.5, 1)$)
- **$\alpha$-Deleted Criterion:** $I(T) < \alpha_{\text{del}} S(T)$ (where $I(T)$ is the invalid/deleted node count and $\alpha_{\text{del}} \in (0, 1)$). Violating either criterion triggers rebalancing; these inequalities describe a balanced tree.

The balancing conditions concern the search structure's shape and deleted-node population. They are not tests of localization accuracy. Map downsampling also introduces an engineering trade-off: retaining every return increases work, while excessive reduction may discard useful geometry. The appropriate choice depends on scene structure and the accuracy being evaluated.

## Evidence and limitations

### Author Claims and Benchmark Evidence

These are the paper’s experimental results. This study does not report an independent reproduction or claim those measurements as my own.

- **Real-time performance:** reported operation up to 100 Hz on Intel i7-based hardware and 10 Hz on the Khadas VIM3 ARM platform under the evaluated workloads. [§VI-D and §VII](https://arxiv.org/html/2107.06829v1#S6.SS4)
- **Data structure efficiency:** the reported ikd-Tree experiments show lower overall update/search cost than the compared octree, $R^*$-tree and nanoflann structures. Peak processing time was 214.4 ms in `nclt_2` and below 150 ms in the other 17 evaluated data-structure sequences; nanoflann exceeded seconds in the long sequences. These are data-structure evaluation timings, not a blanket end-to-end latency bound. [§VI-B2](https://arxiv.org/html/2107.06829v1#S6.SS2.SSS2)
- **Benchmark comparison:** 19 sequences from `lili`, `utbm`, `ulhk`, `nclt` and `liosam`. The authors report approximately $8\times$, $10\times$ and $6\times$ faster combined odometry/mapping processing than LILI-OM, LIO-SAM and LINS, respectively, with favorable accuracy in their evaluation. This does not mean it wins every individual table entry. [§VI-C and §VI-D](https://arxiv.org/html/2107.06829v1#S6.SS3)
- **Aggressive motion:** experiments include handheld motion reaching $7\,\mathrm{m/s}$ and a UAV flip reaching $1198^\circ/\mathrm{s}$. [§VII-B2 and §VII-B3](https://arxiv.org/html/2107.06829v1#S7.SS2.SSS2)

### Limitations and interpretation

- **Drift:** local LiDAR–inertial odometry can accumulate error. Loop closure, relocalization, or suitable absolute measurements are separate sources of correction; a filter alone does not create a global reference.
- **Timing and initialization:** a geometrically plausible scan can still be wrong if its timestamps, initial gravity estimate, or bias estimate are inconsistent. Motion compensation depends on those inputs.
- **Scene geometry:** many points on one plane do not necessarily constrain every direction of motion. A low residual can coexist with uncertainty along the plane.
- **Dynamic objects:** scan-to-map matching assumes useful correspondences to persistent scene structure. Moving surfaces can violate that assumption.
- **Scope:** pose estimation and mapping provide inputs to other systems. They do not themselves drive motors, plan routes, follow waypoints, or avoid obstacles.

## What I would measure next

A useful evaluation needs a reference trajectory or surveyed poses, a documented alignment convention, and the exact sensor/software setup. I would separate these checks:

| Check | Measurement | What it can reveal |
| --- | --- | --- |
| Stationary interval | Position/orientation variation after initialization | Bias, initialization, or timing problems |
| Known motion | Translation and rotation error against a reference | Tracking quality under the tested motion |
| Longer route | Error growth and return-to-start discrepancy | Accumulated drift; endpoint agreement alone does not describe the whole trajectory |
| Scene change | Failures or uncertainty in sparse and repetitive geometry | Dependence on available constraints |
| Runtime | Per-scan latency distribution and backlog | Whether processing keeps up, including slow scans |

These are proposed checks, not completed experiments. My main takeaway from the derivations is that the estimator's apparent confidence must be judged alongside timing, geometry, calibration, and independent evidence.

For the broader comparison that motivated this study, read [Localization with Livox MID-360 — A Study of the Options](Livox%20MID-360%20Localization%20Study.md). Related work appears on my [robotics portfolio](https://chheng-lydiya-portfolio.vercel.app/#/projects).

## Sources

- Wei Xu, Yixi Cai, Dongjiao He, Jiarong Lin, and Fu Zhang, [FAST-LIO2: Fast Direct LiDAR-inertial Odometry](https://arxiv.org/abs/2107.06829), 2021 preprint. Sections IV–V contain the estimation and mapping formulation; sections VI–VII contain the evaluation.
- [Official FAST_LIO implementation](https://github.com/hku-mars/FAST_LIO), including sensor timing and calibration guidance. Software branches and versions can differ from the paper's mathematical presentation.
