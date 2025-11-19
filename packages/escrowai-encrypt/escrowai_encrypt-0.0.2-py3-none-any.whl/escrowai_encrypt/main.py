#!/usr/bin/env python3
# Copyright (c) 2024 BeeKeeperAI, Inc.
#
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE.txt file
# or at https://opensource.org/license/mit.

"""
File encryption/decryption using escrowai-encrypt library
Integrates with Azure Blob Storage for secure file handling
Supports algorithm encryption with exclusions and secrets.yaml generation
"""

import os
import warnings
import argparse

# Suppress urllib3 NotOpenSSLWarning on macOS
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

from pathlib import Path
import tempfile
import zipfile
import shutil
import multiprocessing
from multiprocessing import Pool
from escrowai_encrypt.encryption import (
    generate_content_encryption_key,
    encrypt_upload_dataset,
    encrypt_upload_dataset_from_blob,
    AESGCM,
    PBKDF2HMAC,
    hashes,
    default_backend,
)
from azure.storage.blob import ContainerClient

# Set to True to enable debug mode or use debug argument
DEBUG_MODE = False


def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)


def download_from_blob(sas_url, output_path):
    """Download files from Azure Blob Storage to local directory."""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    client = ContainerClient.from_container_url(sas_url)
    blob_list = client.list_blobs()

    file_count = 0
    for blob in blob_list:
        file_count += 1
        blob_path = output_path / blob.name
        blob_path.parent.mkdir(parents=True, exist_ok=True)

        debug_print(f"Downloading {blob.name}...")
        blob_client = client.get_blob_client(blob.name)
        with open(blob_path, "wb") as f:
            f.write(blob_client.download_blob().readall())

    print(f"Downloaded {file_count} file(s) from Azure Blob Storage to {output_path}")
    return file_count


def decrypt_blob_dataset(source_sas_url, key_path, output_path):
    """Download and decrypt files from Azure Blob Storage using escrowai_encrypt library."""
    # Import from escrowai_encrypt's internal modules to match library's encryption
    from escrowai_encrypt.encryption import AESGCM, PBKDF2HMAC, hashes, default_backend

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load CEK
    with open(key_path, "rb") as f:
        cek = f.read()

    client = ContainerClient.from_container_url(source_sas_url)
    blob_list = list(client.list_blobs())

    count = len(blob_list)
    n = 1

    print(f"{count} blob(s) to be downloaded and decrypted.")

    for blob in blob_list:
        debug_print(f"Downloading blob {blob.name} ({n}/{count})...")
        blob_client = client.get_blob_client(blob.name)
        encrypted_data = blob_client.download_blob().readall()

        # Check for "Salted__" prefix
        if not encrypted_data.startswith(b"Salted__"):
            print(f"Warning: {blob.name} doesn't have 'Salted__' prefix, skipping...")
            n += 1
            continue

        # Extract salt and ciphertext
        salt = encrypted_data[8:16]
        ciphertext = encrypted_data[16:]

        # Derive key using PBKDF2 (same as library)
        pbkdf2_hash = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            salt=salt,
            length=32 + 12,
            iterations=10000,
            backend=default_backend(),
        )
        derived_password = pbkdf2_hash.derive(cek)
        key = derived_password[0:32]
        iv = derived_password[32 : (32 + 12)]

        # Decrypt
        debug_print(f"Decrypting blob {blob.name}...")
        plaintext = AESGCM(key).decrypt(iv, ciphertext, None)

        # Remove .bkenc extension if present
        output_filename = blob.name
        if output_filename.endswith(".bkenc"):
            output_filename = output_filename[:-6]

        output_file = output_path / output_filename
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(plaintext)

        print(f"Decrypted {blob.name} -> {output_filename} ({n}/{count})")
        n += 1

    print(f"All files decrypted to {output_path}")


def encrypt_file_local(input_file_path, key_path, output_file_path):
    """Encrypt a single file locally using AES-256-GCM with PBKDF2 key derivation."""
    with open(key_path, "rb") as key_file:
        password = key_file.read()

    # Generate a random salt
    salt = os.urandom(8)

    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32 + 12,  # 32 bytes for AES key and 12 for nonce
        salt=salt,
        iterations=10000,
        backend=default_backend(),
    )
    derived_key = kdf.derive(password)
    key = derived_key[:32]
    nonce = derived_key[32:44]

    # Encrypt the file
    aesgcm = AESGCM(key)
    with open(input_file_path, "rb") as file:
        plaintext = file.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # Save the encrypted file with "Salted__" prefix, salt, and ciphertext
    with open(output_file_path, "wb") as encrypted_file:
        debug_print(f"Encrypting file: {input_file_path} to {output_file_path}")
        encrypted_file.write(b"Salted__" + salt + ciphertext)


def create_secrets_yaml(output_folder_path, encrypted_files):
    """Generate a secrets.yaml file in the output directory based on the encrypted files."""
    secrets_path = output_folder_path / "secrets.yaml"
    with open(secrets_path, "w") as yaml_file:
        yaml_file.write("secretFiles:\n")
        for encrypted_file in encrypted_files:
            yaml_file.write(f" - [{encrypted_file[0]}, {encrypted_file[1]}]\n")

    debug_print(f"secrets.yaml created at: {secrets_path}")
    print(f"Created secrets.yaml with {len(encrypted_files)} encrypted file(s)")


def _encrypt_file_worker(args):
    """Worker function for parallel file encryption."""
    file_path, input_folder_path, output_folder_path, key_path, exclusions = args

    rel_path = file_path.relative_to(input_folder_path)
    dest_file_path = output_folder_path / rel_path

    # Check if file should be excluded
    if file_path.name in exclusions:
        dest_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, dest_file_path)
        return ("excluded", rel_path, None)

    # Encrypt file with .bkenc extension
    encrypted_dest = dest_file_path.parent / (dest_file_path.name + ".bkenc")
    encrypted_dest.parent.mkdir(parents=True, exist_ok=True)

    encrypt_file_local(str(file_path), key_path, str(encrypted_dest))
    encrypted_rel = str(encrypted_dest.relative_to(output_folder_path))

    return ("encrypted", rel_path, [encrypted_rel, str(rel_path)])


def encrypt_algorithm(
    input_folder_path, key_path, output_path, exclusions=None, zip_output=None
):
    """
    Encrypt an algorithm folder, excluding specified files (like Dockerfile, run.sh, requirements.txt).
    Generates a secrets.yaml manifest and optionally zips the result.
    Returns True if temp folder was cleaned up, False otherwise.
    """
    input_folder_path = Path(input_folder_path)
    output_folder_path = Path(output_path)
    output_folder_path.mkdir(parents=True, exist_ok=True)

    exclusions = set(exclusions or [])
    encrypted_files = []
    excluded_files = []

    # Automatically detect and exclude Dockerfile if present
    dockerfile_path = input_folder_path / "Dockerfile"
    if dockerfile_path.exists():
        if "Dockerfile" not in exclusions:
            print("Detected Dockerfile - automatically adding to exclusions")
        exclusions.add("Dockerfile")

    print(f"Encrypting algorithm from {input_folder_path}")
    print(f"Excluding files: {', '.join(sorted(exclusions))}")

    # First pass: count total files to process
    all_files = [
        f for f in input_folder_path.rglob("*") if f.is_file() and ".git" not in f.parts
    ]
    total_files = len(all_files)
    print(f"Processing {total_files} file(s)...")

    # Prepare arguments for parallel processing
    worker_args = [
        (file_path, input_folder_path, output_folder_path, key_path, exclusions)
        for file_path in all_files
    ]

    # Use all available CPU cores for parallel processing
    num_workers = multiprocessing.cpu_count()
    processed = 0

    # Calculate optimal chunk size for better performance
    chunksize = max(1, total_files // (num_workers * 4))

    # Process files in parallel
    with Pool(processes=num_workers) as pool:
        for result in pool.imap_unordered(
            _encrypt_file_worker, worker_args, chunksize=chunksize
        ):
            result_type, rel_path, encrypted_data = result

            if result_type == "excluded":
                excluded_files.append(rel_path)
            else:
                encrypted_files.append(encrypted_data)

            # Show progress bar for large operations (updates in place)
            processed += 1
            if total_files > 100:
                progress = int((processed / total_files) * 100)
                bar_length = 30
                filled = int(bar_length * processed / total_files)
                bar = "=" * filled + "-" * (bar_length - filled)
                print(
                    f"\rProgress: [{bar}] {progress}% ({processed}/{total_files} files)",
                    end="",
                    flush=True,
                )

    # Print newline after progress bar completes
    if total_files > 100:
        print()

    # Generate secrets.yaml
    create_secrets_yaml(output_folder_path, encrypted_files)

    print(f"Encrypted {len(encrypted_files)} file(s) to {output_folder_path}")
    if excluded_files:
        print(f"Copied {len(excluded_files)} excluded file(s)")

    # Optionally zip the output
    cleaned_up = False
    if zip_output:
        zip_file_path = f"{zip_output}"
        print(f"Creating zip file: {zip_file_path}")

        # Count files to zip
        zip_files = []
        for root, dirs, files in os.walk(output_folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(output_folder_path)
                zip_files.append((file_path, arcname))

        total_zip_files = len(zip_files)
        print(f"Archiving {total_zip_files} file(s)...")

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for idx, (file_path, arcname) in enumerate(zip_files, 1):
                zipf.write(file_path, arcname)

                # Show progress for large zips
                if total_zip_files > 100 and idx % 500 == 0:
                    progress = int((idx / total_zip_files) * 100)
                    bar_length = 30
                    filled = int(bar_length * idx / total_zip_files)
                    bar = "=" * filled + "-" * (bar_length - filled)
                    print(
                        f"\rArchiving: [{bar}] {progress}% ({idx}/{total_zip_files} files)",
                        end="",
                        flush=True,
                    )

        if total_zip_files > 100:
            print()  # Newline after progress bar

        print(f"Algorithm package created: {zip_file_path}")

        # Remove the temporary folder after zipping
        debug_print(f"Removing temporary folder: {output_folder_path}")
        shutil.rmtree(output_folder_path)
        cleaned_up = True

    return cleaned_up


def main():
    # Required for multiprocessing on Windows
    multiprocessing.freeze_support()

    global DEBUG_MODE
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt files using escrowai-encrypt library with Azure Blob Storage"
    )
    parser.add_argument(
        "action",
        choices=["encrypt", "decrypt", "generate-key", "encrypt-algorithm"],
        help="Action to perform",
    )
    parser.add_argument(
        "--input",
        help="Input file or folder path (for encrypt) or SAS URL (for decrypt)",
    )
    parser.add_argument("--key", help="Content Encryption Key file path")
    parser.add_argument(
        "--output",
        help="Output path (local folder for decrypt or algorithm encryption)",
    )
    parser.add_argument(
        "--sas-url", help="Azure Blob Storage SAS URL for encrypted data"
    )
    parser.add_argument(
        "--source-sas-url",
        help="Source Azure Blob Storage SAS URL (for encrypt from blob)",
    )
    parser.add_argument("--key-output", help="Output filename for generated key")
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="List of exact file names to exclude from encryption (for algorithms)",
    )
    parser.add_argument(
        "--zip", help="Optional. Provide a zip file name to zip the algorithm output"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    DEBUG_MODE = args.debug

    if args.action == "generate-key":
        key_file = args.key_output if args.key_output else ""
        generate_content_encryption_key(key_file)
        return

    if args.action == "encrypt":
        if not args.key:
            parser.error("--key is required for encryption")
        if not args.sas_url:
            parser.error("--sas-url is required for encryption")

        if args.source_sas_url:
            # Encrypt from blob to blob
            print(f"Encrypting dataset from {args.source_sas_url} to {args.sas_url}")
            encrypt_upload_dataset_from_blob(
                args.source_sas_url, args.key, args.sas_url
            )
        elif args.input:
            # Encrypt from local to blob
            input_path = Path(args.input)
            if not input_path.exists():
                parser.error(f"Input path {args.input} does not exist")

            print(f"Encrypting dataset from {args.input} to {args.sas_url}")
            encrypt_upload_dataset(args.input, args.key, args.sas_url)
        else:
            parser.error(
                "Either --input or --source-sas-url is required for encryption"
            )

    elif args.action == "encrypt-algorithm":
        if not args.input:
            parser.error("--input is required for algorithm encryption")
        if not args.key:
            parser.error("--key is required for algorithm encryption")
        if not args.output and not args.zip:
            parser.error("--output or --zip is required for algorithm encryption")

        # Use temporary directory if only zip is specified
        output_path = args.output
        if not output_path:
            temp_dir = tempfile.mkdtemp()
            output_path = temp_dir

        cleaned_up = encrypt_algorithm(
            args.input,
            args.key,
            output_path,
            exclusions=args.exclude,
            zip_output=args.zip,
        )

        # Clean up temp directory if used and not already cleaned up by encrypt_algorithm
        if not args.output and args.zip and not cleaned_up:
            if os.path.exists(output_path):
                shutil.rmtree(output_path)

    elif args.action == "decrypt":
        if not args.key:
            parser.error("--key is required for decryption")
        if not args.sas_url:
            parser.error("--sas-url is required for decryption (source)")
        if not args.output:
            parser.error("--output is required for decryption")

        decrypt_blob_dataset(args.sas_url, args.key, args.output)


if __name__ == "__main__":
    main()
