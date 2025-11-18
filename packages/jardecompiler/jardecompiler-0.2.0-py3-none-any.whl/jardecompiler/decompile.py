import os
import zipfile
import urllib.request
import subprocess
import tempfile
import argparse

# CFR download URL (latest release at time of writing)
CFR_URL = "https://www.benf.org/other/cfr/cfr-0.152.jar"

def unzip_jar(jar_path, output_dir="extracted_jar"):
    """Unzip a JAR file into a folder."""
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(jar_path, "r") as jar:
        print("Contents of JAR:")
        jar.printdir()
        jar.extractall(output_dir)
    print(f"\nJAR extracted to: {os.path.abspath(output_dir)}")
    return output_dir

def decompile_jar(jar_path, output_dir="decompiled_src"):
    """Decompile a JAR file using CFR (downloaded temporarily)."""
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: download CFR into a temp folder
    tmp_dir = tempfile.mkdtemp()
    cfr_path = os.path.join(tmp_dir, "cfr.jar")
    print(f"Downloading CFR from {CFR_URL}...")
    urllib.request.urlretrieve(CFR_URL, cfr_path)

    # Step 2: run CFR on the JAR
    print("Running CFR decompiler...")
    subprocess.run([
        "java", "-jar", cfr_path, jar_path,
        "--outputdir", output_dir
    ])

    # Step 3: cleanup CFR jar
    os.remove(cfr_path)
    os.rmdir(tmp_dir)
    print(f"Decompiled source written to: {os.path.abspath(output_dir)}")
    return output_dir

def main():
    parser = argparse.ArgumentParser(description="Unzip and optionally decompile JAR files")
    parser.add_argument("jarfile", help="Path to the JAR file")
    parser.add_argument("-u", "--unzip", action="store_true", help="Unzip the JAR contents")
    parser.add_argument("-d", "--decompile", action="store_true", help="Decompile the JAR into .java files")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    args = parser.parse_args()

    if args.unzip:
        unzip_jar(args.jarfile, args.output)

    if args.decompile:
        decompile_jar(args.jarfile, args.output)

    if not args.unzip and not args.decompile:
        print("No action specified. Use --unzip or --decompile.")

if __name__ == "__main__":
    main()

