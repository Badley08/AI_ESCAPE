import os
import sys
from PIL import Image

def convert_image_to_bmp(input_path, output_path=None):
    """
    Convertit une image (PNG, JPG, WEBP, etc.) en format BMP 24/32 bits standard.
    """
    if not os.path.exists(input_path):
        print(f"❌ Erreur : Le fichier '{input_path}' n'existe pas.")
        return False

    # Générer le nom de sortie si non spécifié
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.bmp"

    try:
        with Image.open(input_path) as img:
            # Si l'image a une transparence (RGBA), on conserve le canal Alpha (32 bits)
            # Sinon, on la convertit en RGB standard (24 bits)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            # Sauvegarde en format BMP
            img.save(output_path, format="BMP")
            print(f"✅ Converti avec succès : '{input_path}' -> '{output_path}'")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la conversion de '{input_path}' : {e}")
        return False


def convert_folder_to_bmp(folder_path):
    """
    Parcourt un dossier et convertit toutes les images (PNG, JPG, etc.) en BMP.
    """
    supported_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    
    if not os.path.exists(folder_path):
        print(f"❌ Le dossier '{folder_path}' n'existe pas.")
        return

    count = 0
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(supported_extensions):
            full_path = os.path.join(folder_path, file_name)
            if convert_image_to_bmp(full_path):
                count += 1
                
    print(f"\n🎉 Conversion terminée ! {count} image(s) convertie(s) en BMP.")


if __name__ == "__main__":
    # Utilisation en ligne de commande :
    # 1. python3 convert_to_bmp.py assets/logo.png
    # 2. python3 convert_to_bmp.py assets/
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isdir(target):
            convert_folder_to_bmp(target)
        else:
            convert_image_to_bmp(target)
    else:
        # Par défaut, si aucun argument n'est fourni, on convertit tout le dossier assets
        print("Aucun argument fourni. Conversion du dossier 'assets' par défaut...\n")
        convert_folder_to_bmp("assets")
