from imports import *

def list_datasets(keyword=None, usability_min=None, min_mb=None, columns=None):
    
    from kaggle import api

    print(f"Lister les datasets correspondant à '{keyword if keyword else 'tous les datasets'}' :")
    
    """
    dataset metadata:
    'id', 'ref', 'subtitle', 'creatorName', 'creatorUrl', 'totalBytes',
        'url', 'lastUpdated', 'downloadCount', 'licenseName', 'description',
        'ownerName', 'ownerRef', 'kernelCount', 'title', 'viewCount',
        'voteCount', 'currentVersionNumber', 'usabilityRating', 'tags'
    """
    
    # Traitement des mots-clés
    if keyword:
        if isinstance(keyword, str):
            keyword = [keyword]
        keyword = [re.escape(kw) for kw in keyword]

    # Recherche des datasets via l'API Kaggle
    datasets = []
    for kw in keyword:
        datasets.extend(api.dataset_list(search=kw))

    result = []
    for dataset in datasets:
        dataset_dict = dataset.to_dict()  # Convertir le dataset en dictionnaire
        
        title = dataset_dict.get("title", "")
        ref = dataset_dict.get("ref", "")
        description = dataset_dict.get("description", "")
        lastUpdated = dataset_dict.get("lastUpdated", "")
        voteCount = dataset_dict.get("voteCount", 0)
        tags = dataset_dict.get("tags", [])
        usabilityRating = dataset_dict.get("usabilityRating", 0)
        size = dataset_dict.get("totalBytes", 0)

        # Convertir la taille en Mo
        dataset_size = dataset_dict.get("totalBytes", 0)
        dataset_size_mb = dataset_size / (1024 * 1024)

        # Filtrage selon la taille du dataset
        if min_mb is not None and dataset_size_mb < min_mb:
            continue

        # Filtrage selon la note d'utilisabilité
        if usability_min is not None and usabilityRating < usability_min:
            continue

        # Si des colonnes spécifiques sont demandées
        if columns is not None:
            dataset_dict = {key: dataset_dict[key] for key in columns if key in dataset_dict}

        # Ajouter les informations dans le résultat
        result_dict = {
            "title": title,
            "ref": ref,
            "description": description,
            "lastUpdated": lastUpdated,
            "voteCount": voteCount,
            "tags": tags,
            "usabilityRating": usabilityRating,
            "dataset_size_mb": round(dataset_size_mb,2),
            "Size (Mb)" : round(dataset_dict.get("totalBytes", 0) / (1024 * 1024),2)  # Conversion en Mo
        }

        result.append(result_dict)

    # Création du DataFrame
    df = pd.DataFrame(result)
    
    
    print(f"\n{df.shape[0]} datasets trouvés.")
    return df

def download_dataset(dataset_ref: str, path: str = ".", dataset_size=None):
    dataset_title = dataset_ref.split("/")[1]  # Extraire le titre du dataset de la référence
    dataset_folder = os.path.join(path, dataset_title)  # Chemin complet pour le dataset

    if not os.path.exists(dataset_folder):
        try:
            os.makedirs(dataset_folder, exist_ok=True)  # Crée le dossier de destination
            print(f"📁 Création du dossier : '{dataset_folder}'")
        except Exception as e:
            print(f"❌ Impossible de créer le dossier '{dataset_folder}'. Erreur : {str(e)}")
            return  # Arrêter l'exécution si on ne peut pas créer le dossier

    if dataset_size:
        if dataset_size >= 1000:
            dataset_size_str = f"{dataset_size / 1024:.2f} GB"
        else:
            dataset_size_str = f"{dataset_size:.2f} MB"
        dataset_title_with_size = f"{dataset_title}_{dataset_size_str.replace(' ', '_').replace('GB', 'gb').replace('MB', 'mb')}"
    else:
        dataset_title_with_size = dataset_title

    command = ["kaggle", "datasets", "download", "-d", dataset_ref, "-p", dataset_folder, "--unzip"]

    if dataset_size:
        print(f"📥 Téléchargement de '{dataset_title_with_size}'...")
    else:
        print(f"📥 Téléchargement de '{dataset_title}'...")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        with tqdm(total=dataset_size, unit="MB", unit_scale=True, desc="📥 Progression") as pbar:
            while process.poll() is None:
                time.sleep(1)
                pbar.update(1)

        if process.returncode == 0:
            print(f"✅ Dataset '{dataset_title_with_size}' téléchargé avec succès dans '{dataset_folder}'.")
        else:
            print(f"❌ Erreur lors du téléchargement de '{dataset_title_with_size}'. Code de retour : {process.returncode}")
            print(f"💡 Détails de l'erreur : {process.stderr.read().decode('utf-8')}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du téléchargement. Code de retour : {e.returncode}")
        print(f"💡 Détails : {e.stderr.decode('utf-8')}")
    except FileNotFoundError:
        print("❌ Erreur : La commande 'kaggle' n'a pas été trouvée. Assurez-vous que l'API Kaggle est installée.")
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {str(e)}")

def sort_dataset_by_keyword(datasets_folders_path, keyword, folder_title, destination_folder):
    print("📁 Début du tri des datasets...")
    print(f"🔍 Mot-clé recherché : '{keyword}'")
    print(f"📂 Titre du dossier de regroupement : '{folder_title}'")
    print(f"📍 Dossier de destination : '{destination_folder}'")

    # Chemin complet du dossier de regroupement dans le dossier de destination
    final_destination = os.path.join(destination_folder, folder_title)

    # Récupérer tous les sous-dossiers dans le dossier principal
    datasets = [
        name for name in os.listdir(datasets_folders_path)
        if os.path.isdir(os.path.join(datasets_folders_path, name))
           and name != folder_title  # 🔐 Évite de traiter un éventuel dossier portant ce nom
    ]

    print(f"📄 Dossiers trouvés : {len(datasets)}")
    moved_datasets = []

    for dataset in datasets:
        print(f"\n🔎 Analyse du dataset : '{dataset}'")
        if keyword.lower() in dataset.lower():
            print("✅ Mot-clé trouvé.")

            os.makedirs(final_destination, exist_ok=True)

            source_path = os.path.join(datasets_folders_path, dataset)
            destination_path = os.path.join(final_destination, dataset)

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




