from __future__ import print_function
import os
import sys
import glob
from struct import *
import argparse

def jp(*paths):
    return os.path.normcase(os.path.join(paths[0], *paths[1:]))

def opencreate(path, mode):
    path = os.path.normcase(path)
    dir = os.path.dirname(path)
    if dir != '' and not os.path.exists(dir):
        os.makedirs(dir)
    return open(path, mode)

def banner():
    print("\033[1;32m==========================================\033[0m")
    print("\033[1;32m       Sheikh Nightshader's IMGCraft\033[0m")
    print("\033[1;32m==========================================\033[0m")
    print("\033[1;34mBuild and Extract Files from Custom Images\033[0m")
    print("\033[1;34mUse the options below to choose your action.\033[0m")

def pad_to_sector_alignment(data):
    padding_size = (2048 - (len(data) % 2048)) % 2048
    return data + b'\x00' * padding_size

def build(directory, name):
    img = opencreate(name+'.img', 'wb')
    dirf = opencreate(name+'.dir', 'wb')

    tablepos = img.tell()
    curpos = 0
    dir = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            fname = os.path.join(root, file)
            print(f"Adding file: {fname}")

            with open(fname, 'rb') as f:
                data = f.read()

            padded_data = pad_to_sector_alignment(data)

            img.write(padded_data)

            size = (len(padded_data) + 2047) // 2048

            dir.append((curpos, size, file))

            curpos += size

    for entry in dir:
        dirf.write(pack('IHH24s', entry[0], entry[1], 0, entry[2].encode('latin1')))

    img.close()
    dirf.close()
    print(f"Finished building {name}.img and {name}.dir")

def extract(path, filename=None):
    img = open(path+".img", "rb")
    dirf = open(path+".dir", "rb")

    while True:
        entry = dirf.read(32)
        if entry == '':
            break

        pos, size, name = unpack('2I24s', entry)
        name = name.decode('latin1')

        x = name.index('\x00')
        if x > 0:
            name = name[:x]

        if filename and filename != name:
            continue

        print(f"Extracting {name} at position {hex(pos)} with size {hex(size)}")

        img.seek(pos * 2048, 0)
        data = img.read(size * 2048)

        file_path = jp(path+'_img', name)

        with opencreate(file_path, "wb") as file:
            file.write(data)

    img.close()
    dirf.close()
    print("Extraction complete.")

def main():
    banner()

    parser = argparse.ArgumentParser(description="Build or Extract files from custom .img/.dir archives.")
    parser.add_argument('path', help="Path to the directory or .img/.dir file")
    parser.add_argument('--extract', '-e', help="Extract files from the archive")
    parser.add_argument('--build', '-b', action='store_true', help="Build a new archive from the directory")

    args = parser.parse_args()

    if args.build:
        build(args.path, args.path)
    elif args.extract:
        extract(args.path, args.extract)
    elif args.path[-4:].lower() == '.img' or args.path[-4:].lower() == '.dir':
        extract(args.path[:-4])
    else:
        print("Invalid input. Please use --build to create or --extract to extract files.")

if __name__ == "__main__":
    main()
