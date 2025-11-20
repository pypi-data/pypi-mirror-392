import argparse
from nml.binary_reader import BinaryReader

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Filename to read from.')
    args = parser.parse_args()
    # # Read sample-by-sample
    # reader = BinaryReader(args.file)
    # while True:
    #     sample = reader.read_next()
    #     if sample is None:
    #         break
    #     print("Sample:", sample)
    # reader.close()
    reader = BinaryReader(args.file)
    reader.convert()
    reader.close()