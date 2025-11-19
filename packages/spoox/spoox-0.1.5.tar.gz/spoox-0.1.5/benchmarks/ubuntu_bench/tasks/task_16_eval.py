import sys
from pathlib import Path


if __name__ == "__main__":

    home = Path("/home/linus")
    pictures_dir = home / "Pictures"
    large_images_dir = home / "LargeImages"

    # check if solution dir exists
    if not large_images_dir.is_dir():
        sys.exit("LargeImages dir is missing.")

    # check if the images were only copied (base images still exist)
    if not (pictures_dir / "cardboard" / "cardboard_00001.jpg").is_file():
        sys.exit("The images should be copied not moved.")
    if not (pictures_dir / "cardboard" / "cardboard_00002.jpg").is_file():
        sys.exit("The images should be copied not moved.")
    if not (pictures_dir / "metal" / "metal_00004.jpg").is_file():
        sys.exit("The images should be copied not moved.")
    if not (pictures_dir / "metal" / "metal_00020.png").is_file():
        sys.exit("The images should be copied not moved.")
    if not (pictures_dir / "trash" / "trash_00044.jpg").is_file():
        sys.exit("The images should be copied not moved.")

    # check if all expected images are copied
    if not (large_images_dir / "cardboard_00001.jpg").is_file():
        sys.exit("There should be more images fulfilling the constraints.")
    if not (large_images_dir / "cardboard_00002.jpg").is_file():
        sys.exit("There should be more images fulfilling the constraints.")
    if not (large_images_dir / "glass_00002.jpg").is_file():
        sys.exit("There should be more images fulfilling the constraints.")
    if not (large_images_dir / "metal_00004.jpg").is_file():
        sys.exit("There should be more images fulfilling the constraints.")
    if not (large_images_dir / "trash_00044.jpg").is_file():
        sys.exit("There should be more images fulfilling the constraints.")

    # check if exactly 6 images are found
    if len(list(large_images_dir.glob("*.jpg"))) != 5:
        sys.exit("There should be less images fulfilling the constraints.")

    sys.exit(0)
