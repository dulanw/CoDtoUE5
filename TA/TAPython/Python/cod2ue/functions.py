import json
import math
import unreal
from necessary import *

class Props:

    #Import all props
    @staticmethod
    def import_props(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items):

        with open(os.path.join(map_folder, f"{map_name}_xmodels.json"), "r") as file:
            entities = json.load(file)

        props = []
        for prop in entities:
            if 'Name' in prop:
                if prop['Name'] not in props:
                    props.append(prop['Name'])

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        for model in props:
            #Import models
            model_found = False
            model_clean = clean(model)

            if not unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}xmodels/{model_clean}.{model_clean}"):
                unreal.log_warning(f"{import_folder}xmodels/{model_clean}.{model_clean} does not exist, trying to import")

                for file in files_list(greyhound_folder):
                    if file['Name'] == model and file['Type'] == "obj":

                        model_found = True
                        model_full_directory = file['Full Directory']
                        prop_original_name = file['Original Name']

                        options = unreal.FbxImportUI()
                        options.create_physics_asset = False
                        options.import_materials = False
                        options.import_textures = False
                        options.import_animations = False
                        options.static_mesh_import_data.build_nanite = False
                        options.static_mesh_import_data.combine_meshes = True
                        options.skeletal_mesh_import_data.import_uniform_scale = 1

                        task = unreal.AssetImportTask()
                        task.automated = True
                        task.destination_path = f"{import_folder}xmodels"
                        task.destination_name = model_clean
                        task.filename = model_full_directory
                        task.options = options
                        task.save = True
                        asset_tools.import_asset_tasks([task])

                        # rename prop_original_name.prop_original_name to model_clean.model_clean if destination_name doesn't work
                        if len(task.get_objects()) > 0:
                            unreal.log_warning(f"imported {model_full_directory} to {import_folder}xmodels/{model_clean}")
                        else:
                            unreal.log_error(f"failed to import {model_full_directory} to {import_folder}xmodels/{model_clean}")

                        break

                if not model_found:
                    unreal.log_error(f"did not find {model_clean}, duplicate {assets_folder}error.error to {import_folder}xmodels/{model_clean}")
                    unreal.EditorAssetLibrary.duplicate_asset(f"{assets_folder}error.error", f"{import_folder}xmodels/{model_clean}")

        for model in props:
            model_clean = clean(model)
            all_material_info = []

            #Look for file, get slot name from mtl file and open _images file in order to get all the material info needed
            for file in files_list(greyhound_folder):
                if file['Name'] == model:
                    for textures_file in files_list(file['Directory']):

                        if textures_file['Raw Name'].endswith(".mtl"):

                            #Set default values
                            material_info = {'Slot': textures_file['Original Name'], 'Albedo': "Default",
                                             'Normal': "Default", 'Specular': "Default"}

                            #Add real values if texture is found
                            img_loc = os.path.join(textures_file['Directory'], f"{textures_file['Original Name']}_images.txt")
                            if os.path.isfile(img_loc):
                                with open(img_loc, 'r') as images_info:
                                    for _line in images_info:
                                        line = _line.strip()
                                        if line.startswith("colorMap,"):
                                            texture_name = line[line.rfind(',') + 1:]
                                            material_info['Albedo'] = texture_name
                                            import_texture(texture_name, import_folder, greyhound_folder, assets_folder)

                                        if line.startswith("normalMap,"):
                                            texture_name = line[line.rfind(',') + 1:]
                                            material_info['Normal'] = texture_name
                                            import_texture(texture_name, import_folder, greyhound_folder, assets_folder)

                                        if line.startswith("unk_semantic_0x34ECCCB3,"):
                                            texture_name = line[line.rfind(',') + 1:]
                                            material_info['Specular'] = texture_name
                                            import_texture(texture_name, import_folder, greyhound_folder, assets_folder)

                                all_material_info.append(material_info)

            if all_material_info:
                #Create and assign materials
                for material_value in all_material_info:

                    #Replace all "illegal characters" with a "_"
                    name = clean(material_value['Slot'])
                    albedo = clean(material_value['Albedo'])
                    normal = clean(material_value['Normal'])
                    specular = clean(material_value['Specular'])

                    material_instance = check_material_existence(name, import_folder, assets_folder, global_opacity, opacity_items, model_clean)
                    if material_instance is None:
                        unreal.log_warning(f"creating material instance {import_folder}materials/{name}")
                        #Select master and create instance
                        master_material: unreal.Material = unreal.load_asset(f"{assets_folder}MasterMat.MasterMat")
                        # noinspection PyTypeChecker
                        material_instance: unreal.MaterialInstanceConstant = asset_tools.create_asset(name, f"{import_folder}materials/", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                        unreal. MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)  # set parent material

                        if not albedo == 'Default':
                            texture_name = albedo
                            current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'AlbedoTexture', current_texture)

                        if not normal == 'Default':
                            texture_name = normal
                            current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'NormalTexture', current_texture)

                        if not specular == 'Default':
                            texture_name = specular
                            current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'SpecularTexture', current_texture)
                            unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Specular', True)

                        if any(item in name for item in opacity_items) and "decal" not in name:
                            unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Alpha', True)

                        if "decal" in name:
                            unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Decal', True)

                    #Actually start assigning the material to the model
                    asset: unreal.StaticMesh = unreal.load_asset(f"{import_folder}xmodels/{model_clean}.{model_clean}")
                    # selected_material: unreal.MaterialInstanceConstant = unreal.load_asset(f"{import_folder}materials/{slot}.{slot}")

                    for index, material in enumerate(asset.static_materials):
                        if name in unreal.StringLibrary.conv_name_to_string(material.material_slot_name):
                            if material.material_interface != material_instance:
                                asset.set_material(index, material_instance)

                all_material_info.clear()

    #Re-assign parent of instances, useful if someone goes from global_opacity to not having global_opacity (and the opossite)
    @staticmethod
    def re_parent_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items):

        #Get all necessary info
        with open(f"{map_folder}\\{map_name}_xmodels.json", "r") as file:
            entities = json.load(file)

        props = []
        for prop in entities:
            if 'Name' in prop:
                if prop['Name'] not in props:
                    props.append(prop['Name'])

        #Get all prop material names and change the parent material if needed
        for model in props:
            for file in files_list(greyhound_folder):
                if file['Name'] == model:
                    for textures_file in files_list(file['Directory']):
                        if textures_file['Raw Name'].endswith(".mtl"):

                            material_name = clean(textures_file['Original Name'])
                            check_material_existence(material_name, import_folder, assets_folder, global_opacity, opacity_items, model)

    #Place props
    @staticmethod
    def place(map_name, map_folder, import_folder):

        #Get (raw) necessary info
        with open(os.path.join(map_folder, f"{map_name}_xmodels.json"), "r") as file:
            entities = json.load(file)

        cube_placeholder: unreal.StaticMesh = unreal.load_asset('/Engine/BasicShapes/Cube.Cube')

        #Create cube to hold all props
        props_cube : unreal.StaticMeshActor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        props_cube.static_mesh_component.set_static_mesh(cube_placeholder)
        props_cube.set_actor_label('Props')

        #Start the placing process
        actors_info = []
        for actor in entities:

            #If the actor meets all this requirements then it proceeds to place it.
            actor_requirements = ['Name', 'RotX', 'RotY', 'RotZ', 'PosX', 'PosY', 'PosZ', 'Scale']

            if all(item in actor for item in actor_requirements):

                #Get all the info required
                name = clean(actor['Name'])

                RotX = (float(actor['RotX'])) * math.pi/180
                RotY = (float(actor['RotY'])) * math.pi/180
                RotZ = (float(actor['RotZ'])) * math.pi/180

                RotX = RotX * 180/math.pi
                RotY = RotY * 180/math.pi
                RotZ = RotZ * 180/math.pi

                PosX = float(actor['PosX'])
                PosY = float(actor['PosY'])
                PosZ = float(actor['PosZ'])

                Scale = float(actor['Scale']) * 0.3937

                #Classify the actor, and it's number (this is 2 stop an actor placed twice from having the same)

                current_number = None
                actor_info = {}

                actor_info['Number'] = 1
                actor_info['Model'] = name

                for model in actors_info:
                    if name == model['Model']:
                        actor_info['Number'] = model['Number']
                        current_number = model['Number'] + 1

                if actor_info not in actors_info:
                    actors_info.append(actor_info)

                elif actor_info in actors_info:

                    actors_info.remove(actor_info)
                    actor_info['Number'] = current_number
                    actors_info.append(actor_info)

                #Place the actor
                asset = unreal.load_asset(f"{import_folder}xmodels/{name}.{name}")
                if asset is None:
                    unreal.log_error(f"did not find required asset {import_folder}xmodels/{name}.{name}")
                else:
                    unreal.log(f"found required asset {import_folder}xmodels/{name}.{name}")

                    asset_actor: unreal.StaticMeshActor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
                    asset_actor.attach_to_actor(props_cube, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
                    asset_actor.set_actor_scale3d(unreal.Vector(Scale, -Scale, Scale))
                    asset_actor.set_actor_location(unreal.Vector(PosX, PosY, PosZ), False, True)
                    asset_actor.set_actor_rotation(unreal.Rotator(-RotX, -RotY, RotZ), True)
                    asset_actor.static_mesh_component.set_static_mesh(asset)
                    asset_actor.set_actor_label(f"{name}{current_number}")

        props_cube.set_actor_scale3d(unreal.Vector(1,-1,1))


class Geometry:
    #Import textures and materials for geometry. The reason for its own separate function is that I will have to do this part for both states of "individual_geometry_objects"
    #Both states require the same method to import geometry, so, i decided to not have to write this part twice.
    @staticmethod
    def import_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items):

        with open(os.path.join(map_folder, f"{map_name}_matdata.json"), "r") as file:
            mat_data = json.load(file)

        for textures in mat_data['Materials'].values():
            for texture_name in textures.values():
                texture_name = texture_name.split('\\')[-1]
                import_texture(texture_name, import_folder, greyhound_folder, assets_folder)

        #Create materials
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        for slot, texture in mat_data['Materials'].items():
            name = clean(slot)

            material_instance = check_material_existence(name, import_folder, assets_folder, global_opacity, opacity_items)
            if material_instance is None:
                unreal.log_warning(f"creating material instance {import_folder}materials/{name}")
                # Select master and create instance
                master_material: unreal.Material = unreal.load_asset(f"{assets_folder}MasterMat.MasterMat")
                # noinspection PyTypeChecker
                material_instance: unreal.MaterialInstanceConstant = asset_tools.create_asset(name, f"{import_folder}materials/", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)  # set parent material

                if 'Color Map' in texture:
                    texture_name = clean(texture['Color Map'].split('\\')[-1])
                    current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'AlbedoTexture', current_texture)

                if 'Normal Map' in texture:
                    texture_name = clean(texture['Normal Map'].split('\\')[-1])
                    current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'NormalTexture', current_texture)

                if 'Specular Map' in texture:
                    texture_name = clean(texture['Specular Map'].split('\\')[-1])
                    current_texture: unreal.Texture2D = unreal.load_asset(f"{import_folder}textures/{texture_name}.{texture_name}")
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'SpecularTexture', current_texture)
                    unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Specular', True)

                if any(item in name for item in opacity_items) and "decal" not in name:
                    unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Alpha', True)

                if "decal" in name:
                    unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material_instance, 'Decal', True)

    #Re-assign parent of instances, useful if someone goes from global_opacity to not having global_opacity (and the opossite)
    @staticmethod
    def re_parent_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items):

        #Get all basic necesasry info
        with open(f"{map_folder}\\{map_name}_matdata.json", "r") as file:
            mat_data = json.load(file)

        #Use the info
        for slot in mat_data['Materials']:
            slot = clean(slot)

            check_material_existence(slot, import_folder, assets_folder, global_opacity, opacity_items)

    #import geometry
    @staticmethod
    def import_geometry(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items, map_extension):

        with open(os.path.join(map_folder, f"{map_name}_matdata.json"), "r") as file:
            mat_data = json.load(file)

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        imported = False
        for model in mat_data['Materials']:
            model_name = clean(model)

            if not unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}MapGeo/{map_name}/{model_name}.{model_name}"):
                #we only have to import once, do not try to import multiple times, all assets are in os.path.join(map_folder, f"{map_name}{map_extension}")
                obj = os.path.join(map_folder, f"{map_name}{map_extension}")
                unreal.log_error(f"{import_folder}MapGeo/{map_name}/{model_name}.{model_name} does not exist, {'already imported' if imported else 'try to import'} {obj}")

                if imported:
                    continue

                imported = True

                options = unreal.FbxImportUI()
                options.create_physics_asset = False
                options.import_materials = False
                options.import_textures = False
                options.import_animations = False
                options.static_mesh_import_data.build_nanite = False
                options.static_mesh_import_data.combine_meshes = False
                options.skeletal_mesh_import_data.import_uniform_scale = 1

                task = unreal.AssetImportTask()
                task.automated = True
                task.destination_path = f"{import_folder}MapGeo/{map_name}"
                task.filename = obj
                task.options = options
                task.save = True
                asset_tools.import_asset_tasks([task])

                if len(task.get_objects()) > 0:
                    unreal.log_warning(f"imported {len(task.get_objects())} objects---")
                    for obj in task.get_objects():
                        unreal.log_warning(f"imported: {obj.get_path_name()}")
                else:
                    unreal.log_error(f"failed to import {obj} to {import_folder}MapGeo/{map_name}")

            else:
                unreal.log_warning(f"found {import_folder}MapGeo/{map_name}/{model_name}.{model_name}")

        # Import materials and assign them
        Geometry.import_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items)

        model_names = []
        with open(os.path.join(map_folder, f"{map_name}.obj")) as obj_info:

            for _line in obj_info.readlines():
                line = _line.strip()
                if line .startswith("g "):
                    model_name = line[line.rfind(" ") + 1:]
                    if model_name not in model_names:
                        model_names.append(model_name)

        for material_info in model_names:
            name = clean(material_info)

            # Actually start assigning the material to the model
            asset: unreal.StaticMesh = unreal.load_asset(f"{import_folder}MapGeo/{map_name}/{name}.{name}")
            selected_material: unreal.MaterialInstanceConstant = unreal.load_asset(f"{import_folder}materials/{name}.{name}")

            for index, material in enumerate(asset.static_materials):
                if name in unreal.StringLibrary.conv_name_to_string(
                        material.material_slot_name):
                    if material.material_interface != selected_material:
                        asset.set_material(index, selected_material)

    #Only returns list if create_obj is set to false. Name of the function is pretty self-explanatory.
    @staticmethod
    def import_individual_geometry(create_obj, map_name, map_folder, import_folder, greyhound_folder, assets_folder, individual_geometry_objects, global_opacity, opacity_items, map_extension):

        individual_obj_name = map_name if map_extension == '.fbx' else f"io_{map_name}"
        ret_create_obj = not create_obj
        create_obj = False if map_extension == '.fbx' else create_obj

        models = []
        with open(os.path.join(map_folder, f"{map_name}.obj")) as og_obj_info:

            if create_obj:
                new_temporal_obj = open(os.path.join(map_folder, f"{individual_obj_name}.obj"), "a")

            for _line in og_obj_info.readlines():
                line = _line.strip()
                if line.startswith("g "):
                    model_name = line[line.rfind(" ") + 1:]
                    model_info = {'Number': 1, 'Model': model_name}

                    for model in models:
                        if model_name == model['Model']:
                            model_info['Number'] = model['Number']
                            number_temp = model['Number'] + 1

                    if model_info not in models:
                        models.append(model_info)
                    elif model_info in models:
                        models.remove(model_info)
                        model_info['Number'] = number_temp
                        models.append(model_info)

                    if create_obj:
                        new_temporal_obj.write(f"g {model_info['Model']}{model_info['Number']}\n")

                elif create_obj:
                    new_temporal_obj.write(line + "\n")

            if create_obj:
                new_temporal_obj.close()

            if ret_create_obj:
                return models

        #Import geometry
        #First do a check to see if it is already imported, if not then import.
        imported = False

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        for model in models:
            for number in range(1, model['Number'] + 1):
                model_name = clean(f"{model['Model']}{number}")

                if not unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}MapGeo/{individual_obj_name}/{model_name}.{model_name}"):
                    #we only have to import once, do not try to import multiple times, all assets are in os.path.join(map_folder, f"{individual_obj_name}{map_extension}")
                    obj = os.path.join(map_folder, f"{individual_obj_name}{map_extension}")
                    unreal.log_error(f"{import_folder}MapGeo/{individual_obj_name}/{model_name}.{model_name} does not exist, {'already imported' if imported else 'try to import'} {obj}")

                    if imported:
                        continue

                    imported = True

                    options = unreal.FbxImportUI()
                    options.create_physics_asset = False
                    options.import_materials = False
                    options.import_textures = False
                    options.import_animations = False
                    options.static_mesh_import_data.build_nanite = False
                    options.static_mesh_import_data.combine_meshes = False
                    options.skeletal_mesh_import_data.import_uniform_scale = 1

                    task = unreal.AssetImportTask()
                    task.automated = True
                    task.destination_path = f"{import_folder}MapGeo/{individual_obj_name}"
                    task.filename = obj
                    task.options = options
                    task.save = True
                    asset_tools.import_asset_tasks([task])

                    if len(task.get_objects()) > 0:
                        unreal.log_warning(f"imported {len(task.get_objects())} objects---")
                        for obj in task.get_objects():
                            unreal.log_warning(f"imported: {obj.get_path_name()}")
                    else:
                        unreal.log_error(f"failed to import {obj} to {import_folder}MapGeo/{individual_obj_name}")

                else:
                    unreal.log_warning(f"found {import_folder}MapGeo/{individual_obj_name}/{model_name}.{model_name}")

        if map_extension != '.fbx':
            os.remove( os.path.join(map_folder, f"{individual_obj_name}.obj"))

        # Import materials and assign them
        Geometry.import_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items)

        for material_info in models:
            for model_number in range(1, material_info['Number'] + 1):

                model_name_only = clean(material_info['Model'])
                material_name = model_name_only
                model_name = f"{model_name_only}{model_number}"

                # Actually start assigning the material to the model
                asset: unreal.StaticMesh = unreal.load_asset(f"{import_folder}MapGeo/{individual_obj_name}/{model_name}.{model_name}")
                selected_material: unreal.MaterialInstanceConstant = unreal.load_asset(f"{import_folder}materials/{material_name}.{material_name}")

                for index, material in enumerate(asset.static_materials):
                    if model_name_only in unreal.StringLibrary.conv_name_to_string(material.material_slot_name):
                        if material.material_interface != selected_material:
                            asset.set_material(index, selected_material)

    #Place geometry (applies for both individual and not individual objects geometry)
    @staticmethod
    def place(map_name, map_folder, import_folder, greyhound_folder, assets_folder, individual_geometry_objects, global_opacity, opacity_items, map_extension):

        cube_placeholder: unreal.StaticMesh = unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
        geometry_cube: unreal.StaticMeshActor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        geometry_cube.static_mesh_component.set_static_mesh(cube_placeholder)
        geometry_cube.set_actor_label('Map_Geometry')

        if individual_geometry_objects:

            io_map_name = map_name if map_extension == '.fbx' else f"io_{map_name}"

            #Check if everything is imported
            models = Geometry.import_individual_geometry(False, map_name, map_folder, import_folder, greyhound_folder, assets_folder, individual_geometry_objects, global_opacity, opacity_items, map_extension)
            for model in models:
                for number in range(1, model['Number'] + 1):
                    model_name = clean(f"{model['Model']}{number}")
                    if unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}MapGeo/{io_map_name}/{model_name}.{model_name}"):
                        unreal.log(
                            f"found required geometry {import_folder}MapGeo/{io_map_name}/{model_name}.{model_name}")
                    else:
                        unreal.log_error(f"did not find required geometry {import_folder}MapGeo/{io_map_name}/{model_name}.{model_name}")
                        return

            #If it is imported then place it
            for model in models:
                for number in range(1, model['Number'] + 1):
                    asset_name = clean(f"{model['Model']}{number}")
                    asset = unreal.load_asset(f"{import_folder}MapGeo/{io_map_name}/{asset_name}.{asset_name}")

                    geometry_actor: unreal.StaticMeshActor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
                    geometry_actor.attach_to_actor(geometry_cube, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
                    geometry_actor.set_actor_scale3d(unreal.Vector(0.3937, 0.3937, 0.3937))
                    geometry_actor.static_mesh_component.set_static_mesh(asset)
                    geometry_actor.set_actor_label(asset_name)

            if map_extension == '.fbx':
                geometry_cube.set_actor_scale3d(unreal.Vector(0.01, 0.01, 0.01))
        else:
            with open(os.path.join(map_folder, f"{map_name}_matdata.json"), "r") as file:
                mat_data = json.load(file)

            for model in mat_data['Materials']:
                model_name = clean(model)
                if unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}MapGeo/{map_name}/{model_name}.{model_name}"):
                    unreal.log(f"found required geometry {import_folder}MapGeo/{map_name}/{model_name}.{model_name}")
                else:
                    unreal.log_error(f"did not find required geometry {import_folder}MapGeo/{map_name}/{model_name}.{model_name}")
                    return

            #If it is imported then place it
            for model_name in mat_data['Materials']:
                asset_name = clean(f"{model_name}")
                asset = unreal.load_asset(f"{import_folder}MapGeo/{map_name}/{asset_name}.{asset_name}")

                geometry_actor: unreal.StaticMeshActor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
                geometry_actor.attach_to_actor(geometry_cube, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
                geometry_actor.set_actor_scale3d(unreal.Vector(0.3937, 0.3937, 0.3937))
                geometry_actor.static_mesh_component.set_static_mesh(asset)
                geometry_actor.set_actor_label(asset_name)

            if map_extension == '.fbx':
                geometry_cube.set_actor_scale3d(unreal.Vector(0.01, 0.01, 0.01))