import os
import bpy

bl_info = {
    "name":         "PSX",
    "author":       "petenub",
    "blender":      (2,80,0),
    "version":      (1,0),
    "location":     "File > Import-Export",
    "description":  "Export psx data into a c file, updated from script posted on psxdev.net",
    "category":     "Import-Export"
}
        
from bpy.props import (CollectionProperty,
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       )
                       
from bpy_extras.io_utils import (
        ExportHelper,
        orientation_helper,
        axis_conversion,
        )

from mathutils import Matrix

@orientation_helper(axis_forward='Z', axis_up='-Y')
class ExportPSX(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_psx.c";
    bl_label        = "PSX compatible format exporter";
    bl_options      = {'PRESET'};
        
    filename_ext = ".c"
    filter_glob: StringProperty(
            default="*.c",
            options={'HIDDEN'},
            )
            
    exp_Scale: FloatProperty(
        name="Scale",
        description="Scale",
        default=20,
        )
        
    exp_perVertexNormals: BoolProperty(
        name="Per-Vertex Normals",
        description="Gouraud shading needs per-vertex normals",
        default=False,
        )
        
    def execute(self, context):        
        print("Executing PSX EXPORT")        
        f = open(self.filepath, "w", encoding='ansi')
        
        f.write("// PSX MESH exported from blender using psxexport.py\n")
        
        for m in bpy.data.meshes:
            
            global_matrix = (axis_conversion(to_forward=self.axis_forward,
                            to_up=self.axis_up,
                            ).to_4x4())
            #m.transform(global_matrix)
            
            f.write("SVECTOR "+"model"+m.name+"_mesh[] = {\n")
            for i in range(len(m.vertices)):
                v = global_matrix @ m.vertices[i].co
                f.write("\t{"+str(int(round(v.x*self.properties.exp_Scale)))+","+str(int(round(v.y*self.properties.exp_Scale)))+","+str(int(round(v.z*self.properties.exp_Scale)))+"}")
                if i != len(m.vertices) - 1:
                    f.write(",")
                f.write("\n")
            f.write("};\n\n")

            if (self.properties.exp_perVertexNormals):
                f.write("SVECTOR "+"model"+m.name+"_vertNormal[] = {\n")
                for i in range(len(m.vertices)):
                    normal = global_matrix @ m.vertices[i].normal
                    # Playstation uses 4096, and we're flipping the triangle winding below so negate it as well
                    f.write("\t"+str(int(round(normal.x * -4096)))+","+str(int(round(normal.y * -4096)))+","+str(int(round(normal.z * -4096)))+",0")
                    if i != len(m.vertices) - 1:
                        f.write(",")
                    f.write("\n")
                f.write("};\n\n")
            else:
                f.write("SVECTOR "+"model"+m.name+"_normal[] = {\n")
                for i in range(len(m.polygons)):
                    poly = m.polygons[i]
                    normal = global_matrix @ poly.normal
                    # Playstation uses 4096, and we're flipping the triangle winding below so negate it as well
                    f.write("\t"+str(int(round(normal.x * -4096)))+","+str(int(round(normal.y * -4096)))+","+str(int(round(normal.z * -4096)))+",0")
                    if i != len(m.polygons) - 1:
                        f.write(",")
                    f.write("\n")
                f.write("};\n\n")
                

            if not m.vertex_colors:
                m.vertex_colors.new()

            f.write("CVECTOR "+"model"+m.name+"_color[] = {\n")
            for i in range(len(m.polygons)):
                colors = m.vertex_colors["Col"].data
                color1 = colors[i*3 + 0].color
                color2 = colors[i*3 + 2].color
                color3 = colors[i*3 + 1].color
                f.write("\t"+str(int(color1[0]*255))+","+str(int(color1[1]*255))+","+str(int(color1[2]*255))+", 0")
                if i != len(m.polygons) - 1:
                    f.write(",")
                f.write("\n")
            f.write("};\n\n")

            f.write("u_short "+"model"+m.name+"_index[] = {\n")
            for i in range(len(m.polygons)):
                poly = m.polygons[i]
				# 0,1,2 isn't the correct winding for PSX, use 0,2,1
                f.write("\t"+str(poly.vertices[0])+","+str(poly.vertices[2])+","+str(poly.vertices[1]))
                if i != len(m.polygons) - 1:
                    f.write(",")
                f.write("\n")
            f.write("};\n\n")
        
        f.flush()
        f.close()
        return {'FINISHED'};
        
module_classes = (
    ExportPSX,
)

def menu_func_export_button(self, context):
    self.layout.operator(ExportPSX.bl_idname, text="PSX (.c)")
    
def register():
    print("Registering PSX export")
    for cls in module_classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_button)

def unregister():        
    print("Unregistering PSX export")
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_button)
    
    for cls in reversed(module_classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
        