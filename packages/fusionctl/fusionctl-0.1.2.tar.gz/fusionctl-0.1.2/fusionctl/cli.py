import sys
from pathlib import Path

from . import (
    VMManager,
    VMRunError,
    get_vm_locations,
    add_vm_location,
    remove_vm_location,
)


def print_vm_list(manager: VMManager) -> list[Path]:
    vms = manager.list_vms()
    if not vms:
        print("No VMs found in configured locations.")
        return []

    print("\nDiscovered VMs:")
    for idx, vm in enumerate(vms, start=1):
        status = "Running" if vm.running else "Stopped"
        name = vm.path.name
        print(f"{idx}. [{status}] {name} \u2192 {vm.path}")
    print()
    return [vm.path for vm in vms]


# ---------- interactive menu ----------

def run_menu() -> None:
    manager = VMManager()

    while True:
        print("\n=== fusionctl - pmrsec ===")
        print("1) List VMs")
        print("2) Start VM")
        print("3) Stop VM")
        print("4) Reset VM")
        print("5) Suspend VM")
        print("6) Show VM search paths")
        print("7) Add VM search path")
        print("8) Remove VM search path")
        print("9) Quit")

        choice = input("Select option: ").strip()

        if choice == "1":
            print_vm_list(manager)

        elif choice in {"2", "3", "4", "5"}:
            vm_paths = print_vm_list(manager)
            if not vm_paths:
                continue
            selection = input("Select VM number: ").strip()
            if not selection.isdigit():
                print("Invalid selection.")
                continue
            idx = int(selection)
            if idx < 1 or idx > len(vm_paths):
                print("Invalid VM number.")
                continue
            vmx = vm_paths[idx - 1]

            try:
                if choice == "2":
                    gui_answer = input("Start with GUI? [Y/n]: ").strip().lower()
                    gui = not (gui_answer == "n")
                    manager.start(vmx, gui=gui)
                    print(f"Started {vmx}")
                elif choice == "3":
                    manager.stop(vmx, soft=True)
                    print(f"Stopped {vmx}")
                elif choice == "4":
                    manager.reset(vmx, soft=True)
                    print(f"Reset {vmx}")
                elif choice == "5":
                    manager.suspend(vmx, soft=True)
                    print(f"Suspended {vmx}")
            except (VMRunError, FileNotFoundError) as e:
                print(f"Error: {e}")

        elif choice == "6":
            paths = get_vm_locations()
            if not paths:
                print("No VM search paths configured.")
            else:
                print("\nConfigured VM search paths:")
                for p in paths:
                    print(f" - {p}")

        elif choice == "7":
            new_path = input("Enter directory to add: ").strip()
            if new_path:
                add_vm_location(new_path)
                print(f"Added VM search path: {new_path}")
                manager = VMManager()

        elif choice == "8":
            paths = get_vm_locations()
            if not paths:
                print("No VM search paths configured.")
                continue
            print("\nConfigured paths:")
            for idx, p in enumerate(paths, start=1):
                print(f"{idx}. {p}")
            sel = input("Select path to remove: ").strip()
            if not sel.isdigit():
                print("Invalid selection.")
                continue
            idx = int(sel)
            if idx < 1 or idx > len(paths):
                print("Invalid index.")
                continue
            to_remove = paths[idx - 1]
            remove_vm_location(to_remove)
            print(f"Removed VM search path: {to_remove}")
            manager = VMManager()

        elif choice == "9":
            print("Bye.")
            break

        else:
            print("Unknown option.")


# ---------- command mode ----------

def print_usage() -> None:
    print("Usage:")
    print("  fusionctl                # interactive menu")
    print("  fusionctl list")
    print("  fusionctl start <index>")
    print("  fusionctl stop <index>")
    print("  fusionctl reset <index>")
    print("  fusionctl suspend <index>")
    print("  fusionctl paths")
    print("  fusionctl add-path <dir>")
    print("  fusionctl remove-path <dir>")


def run_command(argv: list[str]) -> None:
    manager = VMManager()

    if len(argv) == 0:
        run_menu()
        return

    cmd = argv[0]

    if cmd == "list":
        print_vm_list(manager)
        return

    if cmd in {"start", "stop", "reset", "suspend"}:
        if len(argv) < 2:
            print("Missing VM index.")
            print_usage()
            return
        index_str = argv[1]
        if not index_str.isdigit():
            print("VM index must be a number.")
            return
        idx = int(index_str)
        vm_paths = print_vm_list(manager)
        if not vm_paths:
            return
        if idx < 1 or idx > len(vm_paths):
            print("Invalid VM index.")
            return
        vmx = vm_paths[idx - 1]
        try:
            if cmd == "start":
                manager.start(vmx, gui=True)
                print(f"Started {vmx}")
            elif cmd == "stop":
                manager.stop(vmx, soft=True)
                print(f"Stopped {vmx}")
            elif cmd == "reset":
                manager.reset(vmx, soft=True)
                print(f"Reset {vmx}")
            elif cmd == "suspend":
                manager.suspend(vmx, soft=True)
                print(f"Suspended {vmx}")
        except (VMRunError, FileNotFoundError) as e:
            print(f"Error: {e}")
        return

    if cmd == "paths":
        paths = get_vm_locations()
        if not paths:
            print("No VM search paths configured.")
        else:
            print("Configured VM search paths:")
            for p in paths:
                print(f" - {p}")
        return

    if cmd == "add-path":
        if len(argv) < 2:
            print("Missing directory path.")
            print_usage()
            return
        path = argv[1]
        add_vm_location(path)
        print(f"Added VM search path: {path}")
        return

    if cmd == "remove-path":
        if len(argv) < 2:
            print("Missing directory path.")
            print_usage()
            return
        path = argv[1]
        remove_vm_location(path)
        print(f"Removed VM search path: {path}")
        return

    print(f"Unknown command: {cmd}")
    print_usage()


def main() -> None:
    """Entry point for console_scripts."""
    run_command(sys.argv[1:])


if __name__ == "__main__":
    main()