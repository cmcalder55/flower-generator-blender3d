@echo off
@REM "C:\Program Files\Blender Foundation\Blender 3.0\blender.exe" --background %1 --python ".\FlowerGenerator\make_flower.py"
@REM "C:\Program Files\Blender Foundation\Blender 3.0\blender.exe" --background "C:\Users\camer\GitHub\automation\flower-generator-blender3d\flower.blend" --python ".\FlowerGenerator\make_flower.py"

"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe" "C:\Users\camer\GitHub\automation\flower-generator-blender3d\flower.blend" --python ".\FlowerGenerator\make_flower.py"