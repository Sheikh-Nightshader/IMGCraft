from __future__ import print_function
import os
from struct import *

SECTOR_SIZE = 2048


def jp(*paths):
    return os.path.normcase(os.path.join(paths[0], *paths[1:]))


def opencreate(path, mode):
    path = os.path.normcase(path)

    folder = os.path.dirname(path)

    if folder != '' and not os.path.exists(folder):
        os.makedirs(folder)

    return open(path, mode)


def pause():
    input("\nPress Enter to continue...")


def banner():
    os.system("cls" if os.name == "nt" else "clear")

    print("\033[1;32m==========================================\033[0m")
    print("\033[1;32m     Sheikh Nightshader's IMGCraft v2\033[0m")
    print("\033[1;32m==========================================\033[0m")
    print("\033[1;34mBuild and Extract GTA IMG Archives\033[0m")
    print("")


def pad_to_sector_alignment(data):
    padding_size = (
        SECTOR_SIZE - (len(data) % SECTOR_SIZE)
    ) % SECTOR_SIZE

    return data + (b'\x00' * padding_size)


def build(directory):

    directory = os.path.normpath(directory)

    if not os.path.exists(directory):
        print("\n[!] Folder not found.")
        return

    name = os.path.basename(directory)

    img = opencreate(name + '.img', 'wb')
    dirf = opencreate(name + '.dir', 'wb')

    curpos = 0
    entries = []

    print(f"\n[+] Building {name}.img")
    print(f"[+] Building {name}.dir\n")

    try:

        for root, dirs, files in os.walk(directory):

            files.sort()

            for file in files:

                fname = os.path.join(root, file)

                try:

                    print(f"[+] Adding: {file}")

                    with open(fname, 'rb') as f:
                        data = f.read()

                    padded_data = pad_to_sector_alignment(data)

                    img.write(padded_data)

                    size = len(padded_data) // SECTOR_SIZE

                    entries.append(
                        (
                            curpos,
                            size,
                            file
                        )
                    )

                    curpos += size

                except Exception as e:
                    print(f"[!] Failed: {file}")
                    print(e)

        for entry in entries:

            filename = entry[2].encode(
                'latin1',
                errors='ignore'
            )[:23]

            filename += b'\x00'

            dirf.write(
                pack(
                    '<IHH24s',
                    entry[0],
                    entry[1],
                    0,
                    filename
                )
            )

        print(f"\n[+] Finished building {name}.img and {name}.dir")

    except Exception as e:
        print("\n[!] Build failed.")
        print(e)

    finally:
        img.close()
        dirf.close()


def extract(path, filename=None):

    path = os.path.splitext(path)[0]

    img_path = path + ".img"
    dir_path = path + ".dir"

    if not os.path.exists(img_path):
        print("\n[!] IMG not found.")
        return

    if not os.path.exists(dir_path):
        print("\n[!] DIR not found.")
        return

    output_folder = os.path.basename(path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"\n[+] Extracting to folder: {output_folder}\n")

    try:

        img = open(img_path, "rb")
        dirf = open(dir_path, "rb")

        while True:

            entry = dirf.read(32)

            if len(entry) < 32:
                break

            try:

                pos, size, _, raw_name = unpack(
                    '<IHH24s',
                    entry
                )

                name = raw_name.split(
                    b'\x00'
                )[0].decode(
                    'latin1',
                    errors='ignore'
                )

                if not name:
                    continue

                if filename and filename.lower() != name.lower():
                    continue

                print(f"[+] Extracting: {name}")

                img.seek(pos * SECTOR_SIZE)

                data = img.read(size * SECTOR_SIZE)

                file_path = jp(output_folder, name)

                with opencreate(file_path, "wb") as file:
                    file.write(data.rstrip(b'\x00'))

            except Exception as e:
                print("[!] Failed entry")
                print(e)

        img.close()
        dirf.close()

        print("\n[+] Extraction complete.")

    except Exception as e:
        print("\n[!] Extraction failed.")
        print(e)


def menu():

    while True:

        banner()

        print("[1] Extract IMG")
        print("[2] Build IMG")
        print("[3] Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":

            path = input(
                "\nEnter IMG or DIR filename: "
            ).strip().strip('"')

            extract(path)

            pause()

        elif choice == "2":

            folder = input(
                "\nEnter folder name: "
            ).strip().strip('"')

            build(folder)

            pause()

        elif choice == "3":

            print("\nGoodbye.")
            pause()
            break

        else:

            print("\n[!] Invalid option.")
            pause()


if __name__ == "__main__":
    menu()