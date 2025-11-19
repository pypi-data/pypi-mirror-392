import subprocess
import sys
import os
from pathlib import Path
from typing import Optional


class PySpyProfiler:
    """Integration with py-spy for CPU profiling."""

    def __init__(self, output_dir: str = "./perf_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def profile_script(
        self,
        script_path: str,
        duration: Optional[int] = None,
        rate: int = 100,
        format: str = "speedscope",
        output_name: Optional[str] = None
    ) -> str:
        """
        Profile a Python script using py-spy.

        Args:
            script_path: Path to Python script to profile
            duration: Duration in seconds (None = until script completes)
            rate: Sampling rate in Hz
            format: Output format (speedscope, flamegraph, raw)
            output_name: Custom output filename

        Returns:
            Path to generated profile file
        """
        if output_name is None:
            output_name = f"pyspy_profile.{format}"

        output_file = self.output_dir / output_name

        cmd = [
            "py-spy",
            "record",
            "-o", str(output_file),
            "-f", format,
            "-r", str(rate),
            "--",
            sys.executable,
            script_path
        ]

        if duration:
            cmd.insert(2, "-d")
            cmd.insert(3, str(duration))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return str(output_file)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"py-spy profiling failed: {e.stderr}")

    def profile_pid(
        self,
        pid: int,
        duration: int,
        rate: int = 100,
        format: str = "speedscope",
        output_name: Optional[str] = None
    ) -> str:
        """
        Profile a running Python process by PID.

        Args:
            pid: Process ID to profile
            duration: Duration in seconds
            rate: Sampling rate in Hz
            format: Output format
            output_name: Custom output filename

        Returns:
            Path to generated profile file
        """
        if output_name is None:
            output_name = f"pyspy_pid_{pid}.{format}"

        output_file = self.output_dir / output_name

        cmd = [
            "py-spy",
            "record",
            "-p", str(pid),
            "-d", str(duration),
            "-o", str(output_file),
            "-f", format,
            "-r", str(rate)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return str(output_file)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"py-spy profiling failed: {e.stderr}")
