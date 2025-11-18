import argparse
from .decompile import unzip_jar

def main():
    parser = argparse.ArgumentParser(description="Unzip and inspect JAR files")
    parser.add_argument("jarfile", help="Path to the JAR file")
    parser.add_argument("-o", "--output", default="extracted_jar", help="Output directory")
    args = parser.parse_args()

    unzip_jar(args.jarfile, args.output)

if __name__ == "__main__":
    main()