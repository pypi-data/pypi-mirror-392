#!/usr/bin/env python3
"""
Convert summary CSV files from base64 images to file-based images.

This script takes a CSV file containing base64-encoded images in an 'img' column
and converts it to use file-based images stored in an images directory.
"""

import argparse
import base64
import io
import os
import sys
import pandas as pd
from PIL import Image
from pint.logging import log


def decode_and_save_image(base64_str, output_path, image_config=None):
    """
    Decode base64 string and save as image file.

    Parameters
    ----------
    base64_str : str
        Base64 encoded image string
    output_path : str
        Path where to save the decoded image
    image_config : dict, optional
        Image configuration for resizing/quality

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    if not base64_str or pd.isna(base64_str):
        return False

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Decode base64
        img_bytes = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_bytes))

        # Apply image processing if config provided
        if image_config:
            width, height = img.size
            max_width = image_config.get("max_width", 512)

            if width > max_width:
                h_w_ratio = height / width
                new_size = (max_width, int(max_width * h_w_ratio))
                img.thumbnail(new_size, Image.LANCZOS)

        # Save image
        save_kwargs = {}
        if image_config:
            img_format = image_config.get("format", "JPEG")
            if img_format.upper() == "JPEG":
                save_kwargs["quality"] = image_config.get("quality", 85)
                save_kwargs["optimize"] = True
        else:
            img_format = "JPEG"
            save_kwargs["quality"] = 85
            save_kwargs["optimize"] = True

        img.save(output_path, format=img_format, **save_kwargs)
        return True

    except Exception as e:
        log.warning(f"Failed to decode/save image to {output_path}: {e}")
        return False


def generate_image_filename(row_idx, obsid=None, mission=None, instrument=None):
    """
    Generate a filename for the image based on available information.

    Parameters
    ----------
    row_idx : int
        Row index as fallback
    obsid : str, optional
        Observation ID
    mission : str, optional
        Mission name
    instrument : str, optional
        Instrument name

    Returns
    -------
    str
        Generated filename
    """
    if obsid:
        base_name = f"obsid_{obsid}_diagnostics"
    elif mission and instrument:
        base_name = f"{mission}_{instrument}_{row_idx:04d}_diagnostics"
    else:
        base_name = f"observation_{row_idx:04d}_diagnostics"

    return f"{base_name}.jpg"


def convert_csv_images(input_csv, output_csv=None, images_dir="images", image_config=None):
    """
    Convert CSV file from base64 images to file-based images.

    Parameters
    ----------
    input_csv : str
        Path to input CSV file with base64 images
    output_csv : str, optional
        Path to output CSV file. If None, will overwrite input
    images_dir : str
        Name of images directory (relative to CSV)
    image_config : dict, optional
        Image processing configuration

    Returns
    -------
    tuple
        (success_count, total_count)
    """
    # Read the CSV
    df = pd.read_csv(input_csv)

    if "img" not in df.columns:
        log.error("No 'img' column found in CSV file. Nothing to convert.")
        return 0, 0

    # Determine output paths
    if output_csv is None:
        output_csv = input_csv

    csv_dir = os.path.dirname(os.path.abspath(output_csv))
    images_path = os.path.join(csv_dir, images_dir)

    log.info(f"Converting {len(df)} rows from {input_csv}")
    log.info(f"Images will be saved to: {images_path}")

    # Process each row
    success_count = 0
    img_paths = []

    for idx, row in df.iterrows():
        base64_img = row.get("img", "")

        if pd.isna(base64_img) or base64_img == "":
            img_paths.append("")
            continue

        # Generate filename
        obsid = row.get("obsid", None)
        mission = row.get("mission", None)
        instrument = row.get("instrument", None)

        filename = generate_image_filename(idx, obsid, mission, instrument)
        relative_path = os.path.join(images_dir, filename)
        full_path = os.path.join(csv_dir, relative_path)

        # Decode and save image
        if decode_and_save_image(base64_img, full_path, image_config):
            img_paths.append(relative_path)
            success_count += 1
            if (idx + 1) % 50 == 0:
                log.info(f"Processed {idx + 1}/{len(df)} images...")
        else:
            img_paths.append("")

    # Update dataframe
    df["img_path"] = img_paths
    df.drop(columns=["img"], inplace=True)

    # Save updated CSV
    df.to_csv(output_csv, index=False)

    log.info(f"Conversion complete: {success_count}/{len(df)} images successfully converted")
    log.info(f"Updated CSV saved to: {output_csv}")

    return success_count, len(df)


def main():
    parser = argparse.ArgumentParser(
        description="Convert summary CSV files from base64 images to file-based images"
    )
    parser.add_argument("input_csv", help="Input CSV file with base64 images in 'img' column")
    parser.add_argument(
        "-o", "--output", help="Output CSV file (default: overwrite input)", default=None
    )
    parser.add_argument(
        "-d", "--images-dir", help="Images directory name (default: images)", default="images"
    )
    parser.add_argument(
        "--max-width", type=int, help="Maximum image width in pixels (default: 512)", default=512
    )
    parser.add_argument("--quality", type=int, help="JPEG quality 1-100 (default: 85)", default=85)
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without actually converting"
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_csv):
        log.error(f"Input file does not exist: {args.input_csv}")
        return 1

    # Set up image config
    image_config = {"max_width": args.max_width, "quality": args.quality, "format": "JPEG"}

    if args.dry_run:
        # Just analyze the file
        df = pd.read_csv(args.input_csv)
        if "img" not in df.columns:
            log.error("No 'img' column found in CSV file.")
            return 1

        img_count = sum(1 for img in df["img"] if pd.notna(img) and img != "")
        log.info(f"Found {img_count} images in {len(df)} rows")
        log.info(f"Would create images in: {args.images_dir}/")
        log.info(f"Image settings: max_width={args.max_width}, quality={args.quality}")
        return 0

    # Perform conversion
    try:
        success_count, total_count = convert_csv_images(
            args.input_csv, args.output, args.images_dir, image_config
        )

        if success_count == total_count:
            log.info("All images converted successfully!")
            return 0
        else:
            log.warning(f"Some images failed to convert: {success_count}/{total_count} successful")
            return 1

    except Exception as e:
        log.error(f"Conversion failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
