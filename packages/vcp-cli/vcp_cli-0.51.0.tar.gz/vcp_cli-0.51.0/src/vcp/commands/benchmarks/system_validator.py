"""System hardware validation for VCP benchmarks."""

import logging
import os
import platform
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from rich.console import Console

DOCKER_GPU_TEST_IMAGE = os.environ.get(
    "VCP_DOCKER_GPU_TEST_IMAGE", "nvidia/cuda:12.0.1-base-ubuntu22.04"
)
DOCKER_GPU_TEST_TIMEOUT_SECONDS = int(
    os.environ.get("VCP_DOCKER_GPU_TEST_TIMEOUT", "1500")
)

logger = logging.getLogger(__name__)
console = Console()


def get_system_specs() -> Dict[str, Any]:
    """
    Collect system hardware specifications.

    Detects RAM, NVIDIA GPUs, CUDA version, and driver information.
    For non-Linux systems, only collects basic RAM information since
    model inference requires Linux.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - ram_total_gb: Total system RAM in GB
            - gpus: List of GPU specifications (Linux only)
            - nvidia_driver_version: NVIDIA driver version (Linux only)
            - cuda_version: CUDA version (Linux only)
    """
    specs: Dict[str, Any] = {
        "ram_total_gb": 0.0,
        "gpus": [],
        "nvidia_driver_version": None,
        "cuda_version": None,
    }

    system = platform.system()

    try:
        if system == "Darwin":
            specs["ram_total_gb"] = _detect_macos_ram()
        elif system == "Linux":
            specs["ram_total_gb"] = _detect_linux_ram()
        else:
            logger.warning(f"Unsupported OS for RAM detection: {system}")
    except Exception as e:
        logger.warning(f"Failed to detect RAM: {e}")

    if system == "Linux":
        try:
            specs.update(_detect_nvidia_gpus())
        except Exception as e:
            logger.warning(f"Failed to detect GPUs: {e}")

    return specs


def _detect_macos_ram() -> float:
    """
    Detect RAM on macOS using sysctl.

    Returns:
        float: RAM in GB
    """
    result = subprocess.run(
        ["sysctl", "-n", "hw.memsize"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        timeout=10,
    )
    mem_bytes = int(result.stdout.strip())
    ram_gb = round(mem_bytes / (1024**3), 2)
    logger.debug(f"macOS RAM detected: {ram_gb} GB")
    return ram_gb


def _detect_linux_ram() -> float:
    """
    Detect RAM on Linux using /proc/meminfo.

    Returns:
        float: RAM in GB
    """
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                mem_kb = int(line.split()[1])
                ram_gb = round(mem_kb / (1024**2), 2)
                logger.debug(f"Linux RAM detected: {ram_gb} GB")
                return ram_gb

    logger.warning("Could not find MemTotal in /proc/meminfo")
    return 0.0


def _detect_nvidia_gpus() -> Dict[str, Any]:
    """
    Detect NVIDIA GPUs and CUDA information using nvidia-smi.

    Returns:
        Dict[str, Any]: Dictionary with gpus, nvidia_driver_version, and cuda_version.
    """
    gpu_info: Dict[str, Any] = {
        "gpus": [],
        "nvidia_driver_version": None,
        "cuda_version": None,
    }

    try:
        gpus = _query_nvidia_gpus()
        gpu_info["gpus"] = gpus

        gpu_info["nvidia_driver_version"] = _query_nvidia_driver_version()

        gpu_info["cuda_version"] = _query_cuda_version()

        logger.debug(f"Detected {len(gpu_info['gpus'])} NVIDIA GPU(s)")

    except FileNotFoundError:
        logger.warning("nvidia-smi not found - no NVIDIA GPUs detected")
    except subprocess.CalledProcessError as e:
        logger.warning(f"nvidia-smi failed: {e}")
    except Exception as e:
        logger.warning(f"GPU detection error: {e}")

    return gpu_info


def _query_nvidia_gpus() -> List[Dict[str, Any]]:
    """
    Query NVIDIA GPU specifications using nvidia-smi.

    Returns:
        List of GPU specification dictionaries
    """
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    gpus = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue

        try:
            name, vram_mb, compute_cap = parts[0], parts[1], parts[2]
            vram_gb = round(float(vram_mb) / 1024, 2)
            cc_float = float(compute_cap)

            gpus.append({
                "name": name,
                "vram_total_gb": vram_gb,
                "cuda_compute_capability": compute_cap,
                "is_flash_attention_compatible": cc_float >= 8.0,
            })
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse GPU info '{line}': {e}")

    return gpus


def _query_nvidia_driver_version() -> Optional[str]:
    """
    Query NVIDIA driver version using nvidia-smi.

    Returns:
        Driver version string or None
    """
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    driver_version = result.stdout.strip().split("\n")[0].strip()
    return driver_version if driver_version else None


def _query_cuda_version() -> Optional[str]:
    """
    Query CUDA version using nvidia-smi.

    Returns:
        CUDA version string or None
    """
    result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        return None

    # Parse CUDA version from the header line
    # Format: "| NVIDIA-SMI 535.230.02             Driver Version: 535.230.02   CUDA Version: 12.2     |"
    for line in result.stdout.split("\n")[:5]:  # Check first 5 lines
        if "CUDA Version:" in line:
            try:
                # Extract version after "CUDA Version:"
                parts = line.split("CUDA Version:")
                if len(parts) > 1:
                    cuda_version = parts[1].strip().split()[0].strip()
                    return cuda_version if cuda_version else None
            except (IndexError, AttributeError):
                continue

    return None


class BaselineRequirements(BaseModel):
    """
    Default baseline requirements for system-check display.

    These represent minimum recommended specifications for running
    basic benchmarks, not model-specific requirements.
    """

    min_ram_gb: float = 8.0
    min_gpu_count: int = 1
    min_gpu_vram_gb: float = 8.0

    model_config = {"frozen": True}


BASELINE_REQUIREMENTS = BaselineRequirements()


class GpuSpec(BaseModel):
    """Specification for a single NVIDIA GPU."""

    name: str = Field(description="GPU model name")
    vram_total_gb: float = Field(description="Total VRAM in gigabytes")
    cuda_compute_capability: str = Field(description="CUDA compute capability version")
    is_flash_attention_compatible: bool = Field(
        description="Whether GPU supports Flash Attention (requires CC >= 8.0)"
    )


class SystemHardwareSpecs(BaseModel):
    """Complete hardware specification for the host system."""

    ram_total_gb: float = Field(description="Total system RAM in gigabytes")
    is_nvidia_driver_installed: bool = Field(description="NVIDIA drivers installed")
    nvidia_driver_version: Optional[str] = Field(
        default=None, description="NVIDIA driver version"
    )
    cuda_version: Optional[str] = Field(default=None, description="CUDA version")
    gpus: List[GpuSpec] = Field(
        default_factory=list, description="Available NVIDIA GPUs"
    )
    is_docker_installed: bool = Field(description="Docker installed")
    is_docker_gpu_operational: bool = Field(description="Docker GPU access")
    docker_error_message: Optional[str] = Field(
        default=None, description="Docker error"
    )


class SystemValidator:
    """Collects and displays system hardware information."""

    def __init__(self):
        """Initialize the SystemValidator."""
        self._specs: Optional[SystemHardwareSpecs] = None

    @property
    def specs(self) -> SystemHardwareSpecs:
        """Get system specs, collecting them if not already cached."""
        if self._specs is None:
            logger.debug("Collecting system hardware specifications...")
            self._specs = self._collect_system_info()
            logger.debug(
                f"System specs collected: RAM={self._specs.ram_total_gb}GB, "
                f"GPUs={len(self._specs.gpus)}"
            )
        return self._specs

    def get_system_info(self) -> List[dict]:
        """
        Get system hardware information for display purposes.

        Returns information about the system's hardware capabilities
        compared against baseline requirements.

        Returns:
            List of dictionaries with keys: component, actual, expected, status
        """
        specs = self.specs
        results = []

        ram_pass = specs.ram_total_gb >= BASELINE_REQUIREMENTS.min_ram_gb
        results.append({
            "component": "System RAM",
            "expected": f"≥ {BASELINE_REQUIREMENTS.min_ram_gb} GB",
            "actual": f"{specs.ram_total_gb:.1f} GB",
            "status": "✅ Pass" if ram_pass else "❌ Fail",
        })

        if specs.gpus:
            for i, gpu in enumerate(specs.gpus, 1):
                prefix = f"GPU {i}" if len(specs.gpus) > 1 else "GPU"

                gpu_count_pass = len(specs.gpus) >= BASELINE_REQUIREMENTS.min_gpu_count
                results.append({
                    "component": f"{prefix} Model",
                    "expected": f"NVIDIA GPU x{BASELINE_REQUIREMENTS.min_gpu_count}",
                    "actual": gpu.name,
                    "status": "✅ Pass" if gpu_count_pass else "❌ Fail",
                })

                vram_pass = gpu.vram_total_gb >= BASELINE_REQUIREMENTS.min_gpu_vram_gb
                results.append({
                    "component": f"{prefix} VRAM",
                    "expected": f"≥ {BASELINE_REQUIREMENTS.min_gpu_vram_gb} GB",
                    "actual": f"{gpu.vram_total_gb:.1f} GB",
                    "status": "✅ Pass" if vram_pass else "❌ Fail",
                })

                results.append({
                    "component": f"{prefix} Compute Capability",
                    "expected": "Model Dependent",
                    "actual": gpu.cuda_compute_capability,
                    "status": "N/A",
                })

                fa_actual = (
                    "Yes (CC ≥ 8.0)"
                    if gpu.is_flash_attention_compatible
                    else f"No (CC {gpu.cuda_compute_capability})"
                )
                results.append({
                    "component": f"{prefix} Flash Attention",
                    "expected": "Model Dependent",
                    "actual": fa_actual,
                    "status": "✅ Pass"
                    if gpu.is_flash_attention_compatible
                    else "❌ Fail",
                })

            results.append({
                "component": "NVIDIA Driver",
                "expected": "Installed",
                "actual": specs.nvidia_driver_version or "Not Found",
                "status": "✅ Pass" if specs.nvidia_driver_version else "❌ Fail",
            })

            results.append({
                "component": "CUDA Version",
                "expected": "Available",
                "actual": specs.cuda_version or "Not Found",
                "status": "✅ Pass" if specs.cuda_version else "❌ Fail",
            })
        else:
            results.append({
                "component": "NVIDIA GPU",
                "expected": f"NVIDIA GPU x{BASELINE_REQUIREMENTS.min_gpu_count}",
                "actual": "Not Found",
                "status": "❌ Fail",
            })

        results.append({
            "component": "Docker",
            "expected": "Installed",
            "actual": "Installed" if specs.is_docker_installed else "Not Found",
            "status": "✅ Pass" if specs.is_docker_installed else "❌ Fail",
        })

        if specs.gpus and platform.system() == "Linux":
            docker_actual = (
                "Operational" if specs.is_docker_gpu_operational else "Failed"
            )
            results.append({
                "component": "Docker GPU Access",
                "expected": "Operational",
                "actual": docker_actual,
                "status": "✅ Pass" if specs.is_docker_gpu_operational else "❌ Fail",
            })

        return results

    def _collect_system_info(self) -> SystemHardwareSpecs:
        """
        Collect comprehensive system hardware information.

        Gathers information about RAM, GPUs, Docker, and CUDA capabilities.

        Returns:
            SystemHardwareSpecs: Complete hardware specification
        """
        hardware_info = get_system_specs()
        logger.debug(f"Detected {len(hardware_info.get('gpus', []))} GPU(s)")

        is_docker_installed = self._check_docker_installed()

        if (
            is_docker_installed
            and hardware_info.get("gpus")
            and platform.system() == "Linux"
        ):
            docker_gpu_operational, docker_error = self._check_docker_gpu()
        elif not is_docker_installed:
            docker_gpu_operational, docker_error = False, "Docker not installed"
        else:
            docker_gpu_operational, docker_error = (
                False,
                "Not applicable (non-Linux or no GPUs)",
            )

        return SystemHardwareSpecs(
            ram_total_gb=hardware_info.get("ram_total_gb", 0.0),
            is_nvidia_driver_installed=bool(hardware_info.get("gpus")),
            nvidia_driver_version=hardware_info.get("nvidia_driver_version"),
            cuda_version=hardware_info.get("cuda_version"),
            gpus=[GpuSpec(**gpu) for gpu in hardware_info.get("gpus", [])],
            is_docker_installed=is_docker_installed,
            is_docker_gpu_operational=docker_gpu_operational,
            docker_error_message=docker_error,
        )

    def _check_docker_installed(self) -> bool:
        """Check if Docker is installed and accessible."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            logger.debug(f"Docker version: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            logger.debug("Docker command not found in PATH")
            return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Docker version check failed: {e}")
            return False

    def _check_docker_gpu(self) -> Tuple[bool, Optional[str]]:
        """
        Test Docker GPU access by running nvidia-smi in a container.

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """

        try:
            check_image = subprocess.run(
                ["docker", "image", "inspect", DOCKER_GPU_TEST_IMAGE],
                capture_output=True,
                timeout=5,
            )
            if check_image.returncode != 0:
                logger.info(f"Pulling Docker GPU test image: {DOCKER_GPU_TEST_IMAGE}")
                console.print(
                    f"⬇️  Pulling Docker GPU test image (first time only): {DOCKER_GPU_TEST_IMAGE}"
                )
                console.print("   This may take a moment...")
        except Exception as e:
            logger.debug(f"Could not check for existing Docker image: {e}")

        docker_command = [
            "docker",
            "run",
            "--rm",
            "--gpus",
            "all",
            DOCKER_GPU_TEST_IMAGE,
            "nvidia-smi",
            "--query-gpu=name",
            "--format=csv,noheader",
        ]

        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=DOCKER_GPU_TEST_TIMEOUT_SECONDS,
            )
            logger.debug(f"Docker GPU test successful: {result.stdout.strip()}")
            return True, None
        except FileNotFoundError:
            logger.error("Docker command not found")
            return False, "Docker not found"
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker GPU test failed: {e.stderr.strip()}")
            return False, e.stderr.strip()
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ({DOCKER_GPU_TEST_TIMEOUT_SECONDS}s)"
            logger.error(
                f"Docker GPU test timed out after {DOCKER_GPU_TEST_TIMEOUT_SECONDS}s"
            )
            return False, error_msg
        except Exception as e:
            logger.error(f"Docker GPU test error: {e}")
            return False, str(e)

    def print_verbose_info(self) -> None:
        """Print verbose NVIDIA diagnostic information."""
        console.print("\n[bold]NVIDIA Diagnostic Information[/bold]\n")

        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                console.print("[bold]nvidia-smi:[/bold]")
                console.print(result.stdout)
            else:
                console.print("[yellow]nvidia-smi:[/yellow] Command failed")
        except FileNotFoundError:
            console.print("[yellow]nvidia-smi:[/yellow] Not found")
        except Exception as e:
            console.print(f"[yellow]nvidia-smi:[/yellow] Error - {e}")

        try:
            result = subprocess.run(
                ["nvidia-container-cli", "info"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                console.print("\n[bold]nvidia-container-cli info:[/bold]")
                console.print(result.stdout)
            else:
                console.print(
                    "\n[yellow]nvidia-container-cli info:[/yellow] Command failed"
                )
        except FileNotFoundError:
            console.print("\n[yellow]nvidia-container-cli info:[/yellow] Not found")
        except Exception as e:
            console.print(f"\n[yellow]nvidia-container-cli info:[/yellow] Error - {e}")

        try:
            result = subprocess.run(
                ["ldconfig", "-p"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                libs = [
                    line
                    for line in result.stdout.splitlines()
                    if "libnvidia-ml" in line
                ]
                console.print(
                    "\n[bold]libnvidia-ml libraries (ldconfig -p | grep libnvidia-ml):[/bold]"
                )
                if libs:
                    console.print("\n".join(libs))
                else:
                    console.print("[yellow]No libnvidia-ml libraries found[/yellow]")
            else:
                console.print("\n[yellow]ldconfig:[/yellow] Command failed")
        except FileNotFoundError:
            console.print("\n[yellow]ldconfig:[/yellow] Not found")
        except Exception as e:
            console.print(f"\n[yellow]ldconfig:[/yellow] Error - {e}")
