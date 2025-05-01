# 3D-Engine-for-pygame


## Report by Arman Kiani.

- This projects contains a 3D render engine for python, made in 4 days.
Two files are created for viewing flexibility and capability of engine, showing it can be used for any project / game with the right adjustment.

***
- showcase/pygame viewer.py
	general visualization of engine capabilities like collision detection and direct obj file importing.

- Minecraft/pygame viewer.py 
	shows flexibility of the engine being used in a simple real life game.
***

Controls:
Mouse: Look
wasd: move
R click, L click: Place, break block / Shoot
L shift: Run
Space: Jump


##Down sides:
Doesnt support gpu acceleration, resulting in performance issues for big projects.
Projection bug for objects behind the camera. (needs cutting and generating new vertices which gets advanced)
doesn't support textures and advanced lighting.

##Summery:
There is room for a lot of improvements due to code clarity and use of OOP programing.

Best wishes, Arman Kiani :)



## Additional info about engine functionality:
- Render method / algorithm: Projection
- Moving: Shifting the world,
- Rotating the camera: rotating the world around camera (matrix multiplication).
- Rendering faces and edges: Vertex look up + pygame polygon and draw.line()
- Efficiency: blocking objects behind the camera (not rendered).
- Render priority: averaging face vertices z dimension.
- Shading: standard deviation of vertices z dimension and mixing color by shadow color (smart simple approach simulationg light).
- collision detection: checking 2D polygon renders.
- Shadows: clipping y to ground level for all vertices.
- Ability to importi obj files directly with one command!
