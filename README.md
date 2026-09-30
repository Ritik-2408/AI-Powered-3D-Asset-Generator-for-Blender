# AI-Powered-3D-Asset-Generator-for-Blender
It is a hybrid, cross-network pipeline that generates a usable 3D mesh from a short text prompt, entirely from within Blender's own interface. It was built under a strict constraint: the target machine has no dedicated GPU and a system RAM budget under 4 GB, so the design had to split the workload intelligently rather than run everything locally.

<img width="1268" height="706" alt="preview" src="https://github.com/user-attachments/assets/342ffa90-ec85-45cb-861c-9f50e9365c3b" />

The core idea is simple: the expensive step (turning text into a 2D image) is offloaded to a free cloud API, while the comparatively lightweight step (turning that 2D image into a 3D mesh) runs locally on the CPU. A custom Blender add-on ties it all together, so the end user never has to leave Blender, handle intermediate files, or understand what's happening underneath.


<img width="899" height="317" alt="image" src="https://github.com/user-attachments/assets/12d3f86d-92d8-4f98-9f1a-6a0f7b00b139" />

<img width="937" height="490" alt="image" src="https://github.com/user-attachments/assets/a3c0e77c-b164-4f1f-aa06-848d4fd2ca95" />
