import zipfile
import os

def unzip_jar(jar_path, output_dir="extracted_jar"):
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the JAR as a zip archive
    with zipfile.ZipFile(jar_path, "r") as jar:
        # List contents
        print("Contents of JAR:")
        jar.printdir()

        # Extract everything
        jar.extractall(output_dir)

    print(f"\nJAR extracted to: {os.path.abspath(output_dir)}")

