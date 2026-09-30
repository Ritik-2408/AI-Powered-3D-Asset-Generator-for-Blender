# AI-Powered-3D-Asset-Generator-for-Blender
It is a hybrid, cross-network pipeline that generates a usable 3D mesh from a short text prompt, entirely from within Blender's own interface. It was built under a strict constraint: the target machine has no dedicated GPU and a system RAM budget under 4 GB, so the design had to split the workload intelligently rather than run everything locally.


The core idea is simple: the expensive step (turning text into a 2D image) is offloaded to a free cloud API, while the comparatively lightweight step (turning that 2D image into a 3D mesh) runs locally on the CPU. A custom Blender add-on ties it all together, so the end user never has to leave Blender, handle intermediate files, or understand what's happening underneath.


This document explains every underlying concept in plain terms, then walks through every file created during development and exactly what role it plays in the finished system.
