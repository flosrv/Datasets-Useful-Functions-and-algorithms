import os, shutil, filecmp

def sort_dataset_by_keyword(datasets_folders_path, keyword, folder_title):
    print("📁 Début du tri des datasets...")
    print(f"🔍 Mot-clé recherché : '{keyword}'")
    print(f"📂 Dossier de destination : '{folder_title}'")

    destination_folder = os.path.join(datasets_folders_path, folder_title)

    # Récupérer tous les sous-dossiers dans le dossier principal
    datasets = [
        name for name in os.listdir(datasets_folders_path)
        if os.path.isdir(os.path.join(datasets_folders_path, name))
           and name != folder_title  # 🔐 Évite de traiter le dossier de destination
    ]

    print(f"📄 Dossiers trouvés : {len(datasets)}")
    moved_datasets = []

    for dataset in datasets:
        print(f"\n🔎 Analyse du dataset : '{dataset}'")
        if keyword.lower() in dataset.lower():
            print("✅ Mot-clé trouvé.")

            os.makedirs(destination_folder, exist_ok=True)

            source_path = os.path.join(datasets_folders_path, dataset)
            destination_path = os.path.join(destination_folder, dataset)

            try:
                shutil.move(source_path, destination_path)
                print(f"📦 Dossier déplacé : {source_path} -> {destination_path}")
                moved_datasets.append(dataset)
            except Exception as e:
                print(f"❌ Erreur lors du déplacement de '{dataset}': {e}")
        else:
            print("⏩ Mot-clé non trouvé, ignoré.")

    print("\n✅ Tri terminé.")
    print(f"📦 Total des dossiers déplacés : {len(moved_datasets)}")
    return moved_datasets

def move_files_from_subfolders(datasets_folders_path):
    print(f"\n📂 Traitement du dossier : {datasets_folders_path}")

    has_subfolders = False
    total_files_moved = 0
    total_subfolders = 0

    # Parcourir tous les sous-dossiers
    for dirpath, dirnames, filenames in os.walk(datasets_folders_path, topdown=False):
        if dirpath == datasets_folders_path:
            continue  # On saute le dossier de base lui-même

        has_subfolders = True
        total_subfolders += 1
        print(f"  🔍 Sous-dossier trouvé : {dirpath} ({len(filenames)} fichier(s))")

        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(datasets_folders_path, filename)

            if os.path.exists(dest_file):
                if filecmp.cmp(source_file, dest_file, shallow=False):
                    print(f"    ✅ Identique (ignoré) : {filename}")
                    continue
                else:
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    new_filename = f"{base}_{counter}{ext}"
                    new_dest_file = os.path.join(datasets_folders_path, new_filename)

                    while os.path.exists(new_dest_file):
                        counter += 1
                        new_filename = f"{base}_{counter}{ext}"
                        new_dest_file = os.path.join(datasets_folders_path, new_filename)

                    shutil.move(source_file, new_dest_file)
                    print(f"    🔄 Déplacé & renommé : {filename} → {new_filename}")
                    total_files_moved += 1
            else:
                shutil.move(source_file, dest_file)
                print(f"    🔄 Déplacé : {filename}")
                total_files_moved += 1

        # Suppression du dossier s’il est vide
        try:
            if len(os.listdir(dirpath)) == 0:
                os.rmdir(dirpath)
                print(f"    🗑️ Supprimé le dossier vide : {dirpath}")
            else:
                print(f"    ⚠️ Le dossier n'est pas vide : {dirpath}")
                for file in os.listdir(dirpath):
                    print(f"      - {file}")
        except OSError as e:
            print(f"    ❌ Erreur suppression : {dirpath} - {e}")

    if not has_subfolders:
        print(f"  ✅ Aucun sous-dossier trouvé, rien à faire.")
    else:
        print(f"  ✅ Terminé : {total_subfolders} sous-dossier(s), {total_files_moved} fichier(s) déplacé(s).")




