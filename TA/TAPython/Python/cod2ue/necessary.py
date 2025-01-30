#All initial necessary stuff
import glob, os, shutil
import unreal

#Make a list with all the greyhound files info (all textures, obj files, etc).
def files_list(path):

    all_files = []

    for root, directories, files in os.walk(path):
        for file_name in files:
            file = {}

            if file_name.endswith(".obj"):
                file['Type'] = "obj"

            elif file_name.endswith(".mtl"):
                file['Type'] = "mtl"

            elif file_name.endswith(".tga") or file_name.endswith(".png"):
                file['Type'] = "texture"

            else:
                file['Type'] = "other"

            file['Full Directory'] = os.path.join(root, file_name)
            file['Raw Name'] = file_name

            file_name = file_name[:file_name.rfind(".")]

            file['Original Name'] = file_name

            if "_LOD0" in file_name:
                file_name = file_name[:file_name.rfind("_LOD0")]

            file['Name'] = file_name
            file['Directory'] = root

            all_files.append(file)

    return all_files


#Fix text so that it is usable on ue4
def clean(text):
    new_text = text.replace('~', '_').replace('#', '_').replace('$', '_').replace('&', '_').replace('.', '').replace('\\', '')

    if new_text.startswith("ml"):
        new_text = new_text.replace("ml", '')

    return new_text

#Import textures
def import_texture(texture_name, import_folder, greyhound_folder, assets_folder):

    texture_clean = clean(texture_name)

    texture_found = False
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{import_folder}textures/{texture_clean}.{texture_clean}"):
        unreal.log_warning(f"{import_folder}textures/{texture_clean}.{texture_clean} does not exist, trying to import")
        #If it does not exist, import it. if the texture is also not available for import then import the missing texture

        for file in files_list(greyhound_folder):
            if file['Name'] == texture_name and file['Type'] == "texture":
                texture_found = True
                texture_directory = file['Full Directory']

                asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

                task = unreal.AssetImportTask()
                task.automated = True
                task.destination_path = f"{import_folder}textures"
                task.filename = texture_directory
                task.save = True
                asset_tools.import_asset_tasks([task])

                if len(task.get_objects()) > 0:
                    unreal.log_warning(f"imported {texture_directory} to {import_folder}textures/{texture_clean}.{texture_clean}")
                else:
                    unreal.log_error(f"failed to import {texture_directory} to {import_folder}textures/{texture_clean}.{texture_clean}")

                break

        # this assumes we have successfully imported the assets folder
        if not texture_found:
            unreal.log_error(f"did not find {texture_clean}, duplicate {assets_folder}error.error to {import_folder}textures/{texture_clean}")
            unreal.EditorAssetLibrary.duplicate_asset(f"{assets_folder}missing.missing", f"{import_folder}textures/{texture_clean}")


#This basically takes the necessary things and places them, that way the process is not manual.
#I know it looks like a lot of unnecessary code, but, this will make everything not crash. Its necessary since these files are the most important ones.
def place_assets_folder(assets_folder, assets_folder_dir, current_path):

    #Import stuff
    #You might notice I have "assets_folder[:-1]", this is because assets_folder ends with / and UE4 does not like that for imports, so, I remove it.
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    #import missing texture
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{assets_folder}missing.missing"):
        unreal.log_warning(f"{assets_folder}missing.missing does not exist, trying to import {current_path}\\AssetsFolder\\missing.tga")

        task = unreal.AssetImportTask()
        task.automated = True
        task.destination_path = f"{assets_folder[:-1]}"
        task.filename = f"{current_path}\\AssetsFolder\\missing.tga"
        task.save = True
        asset_tools.import_asset_tasks([task])

        if len(task.get_objects()) > 0:
            unreal.log_warning(f"imported {current_path}\\AssetsFolder\\missing.tga to {assets_folder[:-1]}")
        else:
            unreal.log_error(f"failed to import {current_path}\\AssetsFolder\\missing.tga to {assets_folder[:-1]}")

        # freeze, no idea why
        # asset_import_data = unreal.AutomatedAssetImportData()
        # asset_import_data.replace_existing = True
        # asset_import_data.destination_path = f"{assets_folder[:-1]}"
        # asset_import_data.filenames = f"{current_path}\\AssetsFolder\\missing.tga"
        # imported_assets = asset_tools.import_assets_automated(asset_import_data)
        #
        # if len(imported_assets) > 0:
        #     unreal.log(f"imported {current_path}\\AssetsFolder\\missing.tga to {assets_folder[:-1]}")
        #     # unreal.EditorAssetLibrary.save_asset(imported_assets[0].get_path_name())
        # else:
        #     unreal.log(f"failed to import {current_path}\\AssetsFolder\\missing.tga to {assets_folder[:-1]}")

    #import flat normal
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{assets_folder}flat_normal.flat_normal"):
        unreal.log_warning(f"{assets_folder}flat_normal.flat_normal does not exist, trying to import to {current_path}\\AssetsFolder\\flat_normal.tga")

        task = unreal.AssetImportTask()
        task.automated = True
        task.destination_path = f"{assets_folder[:-1]}"
        task.filename = f"{current_path}\\AssetsFolder\\flat_normal.tga"
        task.save = True
        asset_tools.import_asset_tasks([task])

        if len(task.get_objects()) > 0:
            unreal.log_warning(f"imported {current_path}\\AssetsFolder\\flat_normal.tga to {assets_folder[:-1]}")
        else:
            unreal.log_error(f"failed to import {current_path}\\AssetsFolder\\flat_normal.tga to {assets_folder[:-1]}")

        # asset_import_data = unreal.AutomatedAssetImportData()
        # asset_import_data.replace_existing = True
        # asset_import_data.destination_path = f"{assets_folder[:-1]}"
        # asset_import_data.filenames = f"{current_path}\\AssetsFolder\\flat_normal.tga"
        # imported_assets = asset_tools.import_assets_automated(asset_import_data)
        #
        # if len(imported_assets) > 0:
        #     unreal.log(f"imported {current_path}\\AssetsFolder\\flat_normal.tga to {assets_folder[:-1]}")
        #     unreal.EditorAssetLibrary.save_asset(imported_assets[0].get_path_name())
        # else:
        #     unreal.log(f"failed to import {current_path}\\AssetsFolder\\flat_normal.tga to {assets_folder[:-1]}")

    #import white texture
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{assets_folder}White.White"):
        unreal.log_warning(f"{assets_folder}White.White does not exist, trying to import to {current_path}\\AssetsFolder\\White.tga")

        task = unreal.AssetImportTask()
        task.automated = True
        task.destination_path = f"{assets_folder[:-1]}"
        task.filename = f"{current_path}\\AssetsFolder\\White.tga"
        task.save = True
        asset_tools.import_asset_tasks([task])

        if len(task.get_objects()) > 0:
            unreal.log_warning(f"imported {current_path}\\AssetsFolder\\White.tga to {assets_folder[:-1]}")
        else:
            unreal.log_error(f"failed to import {current_path}\\AssetsFolder\\White.tga to {assets_folder[:-1]}")

        # asset_import_data = unreal.AutomatedAssetImportData()
        # asset_import_data.replace_existing = True
        # asset_import_data.destination_path = f"{assets_folder[:-1]}"
        # asset_import_data.filenames = f"{current_path}\\AssetsFolder\\White.tga"
        # imported_assets = asset_tools.import_assets_automated(asset_import_data)
        #
        # if len(imported_assets) > 0:
        #     unreal.log(f"imported {current_path}\\AssetsFolder\\White.tga to {assets_folder[:-1]}")
        #     unreal.EditorAssetLibrary.save_asset(imported_assets[0].get_path_name())
        # else:
        #     unreal.log(f"failed to import {current_path}\\AssetsFolder\\White.tga to {assets_folder[:-1]}")


    #import uassets (materials)
    #Copy uassets and put them in UE's folder. I know it's a bit too much for such a simple task but it's better to prevent crashes.
    try:
        os.makedirs(assets_folder_dir)
    except:
        pass

    SRC_DIR = f"{current_path}\\AssetsFolder\\uasset"
    TARG_DIR = assets_folder_dir

    GLOB_PARMS = "*"

    for file in glob.glob(os.path.join(SRC_DIR, GLOB_PARMS)):
        if file not in glob.glob(os.path.join(TARG_DIR, GLOB_PARMS)):

            try:
                shutil.copy(file,TARG_DIR)
            except:
                pass


    #Import error fbx file
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{assets_folder}error.error"):
        unreal.log_warning(f"{assets_folder}error.error does not exist, trying to import to {current_path}\\AssetsFolder\\error.fbx")

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
        task.destination_path = f"{assets_folder[:-1]}"
        task.filename = f"{current_path}\\AssetsFolder\\error.fbx"
        task.options = options
        task.save = True
        asset_tools.import_asset_tasks([task])

        if len(task.get_objects()) > 0:
            unreal.log_warning(f"imported {current_path}\\AssetsFolder\\error.fbx to {assets_folder[:-1]}")
        else:
            unreal.log_error(f"failed to import {current_path}\\AssetsFolder\\error.fbx to {assets_folder[:-1]}")


#Check if material exists and if it does check if the parent mat is correct.
def check_material_existence(name, import_folder, assets_folder, global_opacity, opacity_items, model = []):

    material: unreal.MaterialInstanceConstant = unreal.load_asset(f"{import_folder}materials/{name}.{name}")
    if material is None:
        return None

    if not global_opacity and any(item in name for item in opacity_items) or any(item in model for item in opacity_items):
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material, 'Alpha', True)
    elif not global_opacity:
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material, 'Alpha', False)
    elif global_opacity:
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(material, 'Alpha', True)

    return material