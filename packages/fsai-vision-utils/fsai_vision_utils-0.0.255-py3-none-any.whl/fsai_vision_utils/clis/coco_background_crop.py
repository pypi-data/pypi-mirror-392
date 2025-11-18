import argparse
import json
import os
import random
from PIL import Image


def random_crops_for_image(
    img_path,
    base_name_no_ext,
    ext,
    crops_per_image,
    crop_width,
    crop_height,
    output_dir,
    starting_image_id,
):
    """
    Generate random crops for a single image and return:
      - list of new COCO image dicts
      - next available image id
    """
    image = Image.open(img_path)
    width, height = image.size

    if width < crop_width or height < crop_height:
        print(f"Skipping {img_path}: smaller than crop size ({width}x{height})")
        return [], starting_image_id

    new_images = []
    image_id = starting_image_id

    for i in range(crops_per_image):
        max_x = width - crop_width
        max_y = height - crop_height

        left = 0 if max_x == 0 else random.randint(0, max_x)
        top = 0 if max_y == 0 else random.randint(0, max_y)

        right = left + crop_width
        bottom = top + crop_height

        crop = image.crop((left, top, right, bottom))

        new_filename = (
            f"{base_name_no_ext}_background_{i + 1:03d}_{crop_width}x{crop_height}{ext}"
        )
        out_path = os.path.join(output_dir, new_filename)

        crop.save(out_path)

        new_images.append(
            {
                "id": image_id,
                "file_name": new_filename,
                "width": crop_width,
                "height": crop_height,
            }
        )
        image_id += 1

    return new_images, image_id


def build_background_coco(
    coco_input_path,
    input_dir,
    output_dir,
    coco_output_path,
    crops_per_image,
    crop_size,
    seed=None,
):
    if seed is not None:
        random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)

    with open(coco_input_path, "r") as f:
        coco = json.load(f)

    input_images = coco.get("images", [])

    new_images = []
    next_image_id = 1

    # Optional: carry over some metadata if present
    new_coco = {
        "info": coco.get("info", {}),
        "licenses": coco.get("licenses", []),
        "images": new_images,
        "annotations": [],
        "categories": [],
    }

    crop_width, crop_height = crop_size

    for img in input_images:
        file_name = img["file_name"]
        # Try full relative path first
        candidate_path = os.path.join(input_dir, file_name)
        if not os.path.isfile(candidate_path):
            # Fallback: just use basename
            base_name = os.path.basename(file_name)
            candidate_path = os.path.join(input_dir, base_name)

        if not os.path.isfile(candidate_path):
            print(f"WARNING: could not find image file for {file_name}, skipping.")
            continue

        base_name = os.path.basename(candidate_path)
        base_no_ext, ext = os.path.splitext(base_name)

        crops, next_image_id = random_crops_for_image(
            candidate_path,
            base_no_ext,
            ext,
            crops_per_image,
            crop_width,
            crop_height,
            output_dir,
            next_image_id,
        )

        new_images.extend(crops)

    print(f"Generated {len(new_images)} cropped images in: {output_dir}")

    with open(coco_output_path, "w") as f:
        json.dump(new_coco, f, indent=2)

    print(f"New COCO file written to: {coco_output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate random background crops from COCO images "
        "and create a new COCO JSON with only image entries."
    )
    parser.add_argument(
        "--input-coco-json",
        type=str,
        required=True,
        help="Path to input COCO JSON file.",
    )
    parser.add_argument(
        "--input-image-dir",
        type=str,
        required=True,
        help="Directory containing the original images.",
    )
    parser.add_argument(
        "--output-images-dir",
        type=str,
        required=True,
        help="Directory to save cropped images.",
    )
    parser.add_argument(
        "--output-coco-json",
        type=str,
        required=True,
        help="Path to save the new COCO JSON file.",
    )
    parser.add_argument(
        "--crops-per-image",
        type=int,
        default=1,
        help="Number of random crops to generate per input image.",
    )
    parser.add_argument(
        "--crop-size",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=[2048, 2048],
        help="Crop size as WIDTH HEIGHT (default: 2048 2048).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    build_background_coco(
        coco_input_path=args.input_coco_json,
        input_dir=args.input_image_dir,
        output_dir=args.output_images_dir,
        coco_output_path=args.output_coco_json,
        crops_per_image=args.crops_per_image,
        crop_size=tuple(args.crop_size),
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
