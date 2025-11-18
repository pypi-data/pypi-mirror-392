import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Iterable, Set

from .config import get_vm_locations


class VMRunError(RuntimeError):
    """Raised when vmrun returns an error."""


@dataclass
class VMInfo:
    path: Path
    running: bool


class VMManager:

    def __init__(
        self,
        vmrun_path: Optional[str] = None,
        search_paths: Optional[Iterable[str]] = None,
    ) -> None:
        self.vmrun_path = self._find_vmrun(vmrun_path)
        if search_paths is None:
            search_paths = get_vm_locations()
        self.search_paths: List[Path] = [
            Path(p).expanduser() for p in search_paths
        ]

    def _find_vmrun(self, vmrun_path: Optional[str]) -> str:
        if vmrun_path:
            return vmrun_path

        vmrun = shutil.which("vmrun")
        if vmrun:
            return vmrun

        default = Path("/Applications/VMware Fusion.app/Contents/Library/vmrun")
        if default.exists():
            return str(default)

        raise FileNotFoundError("vmrun executable not found. "
                                "Install VMware Fusion or add vmrun to PATH.")

    def _run_vmrun(self, *args: str) -> str:
        """
        Run vmrun with '-T fusion' and return stdout as text.
        Raise VMRunError on vmrun error output.
        """
        cmd = [self.vmrun_path, "-T", "fusion", *args]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if stdout.startswith("Error:") or stderr:
            msg_parts = []
            if stdout:
                msg_parts.append(stdout)
            if stderr:
                msg_parts.append(stderr)
            raise VMRunError("\n".join(msg_parts))

        return stdout

    def list_running_vmx_paths(self) -> Set[Path]:
        output = self._run_vmrun("list")
        lines = output.splitlines()
        if not lines:
            return set()

        vm_lines = lines[1:]
        return {Path(line.strip()) for line in vm_lines if line.strip()}

    def discover_all_vms(self) -> List[Path]:
        vmx_files: List[Path] = []
        for base in self.search_paths:
            if not base.exists():
                continue
            for vmx in base.rglob("*.vmx"):
                vmx_files.append(vmx)
        seen: Set[Path] = set()
        unique: List[Path] = []
        for p in vmx_files:
            rp = p.resolve()
            if rp not in seen:
                seen.add(rp)
                unique.append(rp)
        return sorted(unique)

    def list_vms(self) -> List[VMInfo]:
        running = self.list_running_vmx_paths()
        all_vms = self.discover_all_vms()
        return [VMInfo(path=vmx, running=(vmx in running)) for vmx in all_vms]

    def start(self, vmx: Path | str, gui: bool = True) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        mode = "gui" if gui else "nogui"
        self._run_vmrun("start", str(vmx), mode)

    def stop(self, vmx: Path | str, soft: bool = True) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        mode = "soft" if soft else "hard"
        self._run_vmrun("stop", str(vmx), mode)

    def reset(self, vmx: Path | str, soft: bool = True) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        mode = "soft" if soft else "hard"
        self._run_vmrun("reset", str(vmx), mode)

    def suspend(self, vmx: Path | str, soft: bool = True) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        mode = "soft" if soft else "hard"
        self._run_vmrun("suspend", str(vmx), mode)

    def list_snapshots(self, vmx: Path | str) -> list[str]:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")

        output = self._run_vmrun("listSnapshots", str(vmx))
        lines = output.splitlines()
        return [line.strip() for line in lines[1:] if line.strip()]

    def snapshot(self, vmx: Path | str, name: str) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        self._run_vmrun("snapshot", str(vmx), name)

    def revert_to_snapshot(self, vmx: Path | str, name: str) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        self._run_vmrun("revertToSnapshot", str(vmx), name)

    def delete_snapshot(self, vmx: Path | str, name: str) -> None:
        vmx = Path(vmx).expanduser().resolve()
        if not vmx.is_file():
            raise FileNotFoundError(f"VMX not found at {vmx}")
        self._run_vmrun("deleteSnapshot", str(vmx), name)