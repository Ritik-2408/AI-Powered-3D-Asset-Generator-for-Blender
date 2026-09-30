bl_info = {
    "name": "AI 3D Generator",
    "author": "Ritik",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > 3D Gen",
    "description": "Generate 3D meshes from text prompts via local FastAPI + TripoSR backend",
    "category": "Import-Export",
}

import bpy
import os
import tempfile
import urllib.request
import json


BACKEND_URL = "http://127.0.0.1:8000/generate-3d"


class AIGEN_Properties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Text description of the 3D object to generate",
        default="a small red toy car",
    )
    status: bpy.props.StringProperty(
        name="Status",
        default="Ready",
    )


class AIGEN_OT_Generate(bpy.types.Operator):
    bl_idname = "aigen.generate_3d"
    bl_label = "Generate 3D Model"
    bl_description = "Send prompt to local backend and import the generated mesh"

    def execute(self, context):
        props = context.scene.aigen_props
        prompt = props.prompt.strip()

        if not prompt:
            self.report({'WARNING'}, "Prompt is empty.")
            return {'CANCELLED'}

        props.status = "Generating... please wait"

        payload = json.dumps({"prompt": prompt}).encode("utf-8")
        req = urllib.request.Request(
            BACKEND_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                if response.status != 200:
                    error_body = response.read().decode("utf-8", errors="ignore")
                    self.report({'ERROR'}, f"Backend error ({response.status}): {error_body[:200]}")
                    props.status = "Failed"
                    return {'CANCELLED'}
                mesh_bytes = response.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            self.report({'ERROR'}, f"Backend returned an error: {error_body[:200]}")
            props.status = "Failed"
            return {'CANCELLED'}
        except urllib.error.URLError as e:
            self.report({'ERROR'}, f"Could not reach backend at {BACKEND_URL}: {e.reason}")
            props.status = "Failed - server unreachable"
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            props.status = "Failed"
            return {'CANCELLED'}

        # Save the returned .obj bytes to a temp file, then import it
        temp_dir = tempfile.gettempdir()
        temp_obj_path = os.path.join(temp_dir, "aigen_temp_mesh.obj")
        try:
            with open(temp_obj_path, "wb") as f:
                f.write(mesh_bytes)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save mesh file: {e}")
            props.status = "Failed"
            return {'CANCELLED'}

        try:
            bpy.ops.wm.obj_import(filepath=temp_obj_path)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import mesh into Blender: {e}")
            props.status = "Failed - import error"
            return {'CANCELLED'}

        props.status = "Done"
        self.report({'INFO'}, "3D model generated and imported successfully.")
        return {'FINISHED'}


class AIGEN_PT_Panel(bpy.types.Panel):
    bl_label = "AI 3D Generator"
    bl_idname = "AIGEN_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "3D Gen"

    def draw(self, context):
        layout = self.layout
        props = context.scene.aigen_props

        layout.label(text="Prompt:")
        layout.prop(props, "prompt", text="")
        layout.operator("aigen.generate_3d", text="Generate 3D Model")
        layout.label(text=f"Status: {props.status}")


classes = (
    AIGEN_Properties,
    AIGEN_OT_Generate,
    AIGEN_PT_Panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aigen_props = bpy.props.PointerProperty(type=AIGEN_Properties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.aigen_props


if __name__ == "__main__":
    register()