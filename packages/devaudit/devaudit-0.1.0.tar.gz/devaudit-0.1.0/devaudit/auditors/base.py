"""
Base auditor class that all specific auditors inherit from.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


class BaseAuditor(ABC):
    """
    Abstract base class for all auditors.

    Each auditor must implement:
        - name: The display name of the tool being audited
        - is_installed(): Check if the tool is installed
        - get_version(): Get the tool's version
        - audit(): Perform detailed audit
    """

    def __init__(self, target_dir: Optional[str] = None):
        self.name = "Unknown"
        self.installed = False
        self.version = None
        self.data = {}
        self.target_dir = Path(target_dir) if target_dir else None

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the tool is installed on the system."""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get the version of the installed tool."""
        pass

    @abstractmethod
    def audit(self) -> Dict:
        """
        Perform a detailed audit of the tool.

        Returns:
            Dict containing audit results with keys:
                - installed: bool
                - version: str or None
                - packages: List[Dict] (optional)
                - cleanup_candidates: List[Dict] (optional)
                - warnings: List[str] (optional)
        """
        pass

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run a shell command and return output.

        Args:
            cmd: Command to run as list of strings
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", -1
        except FileNotFoundError:
            return "", f"Command not found: {cmd[0]}", -1
        except Exception as e:
            return "", f"Error running command: {str(e)}", -1

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None

    def run_command_in_target(self, cmd: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run a command in the target directory if specified.

        Args:
            cmd: Command to run as list of strings
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.target_dir) if self.target_dir else None
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", -1
        except FileNotFoundError:
            return "", f"Command not found: {cmd[0]}", -1
        except Exception as e:
            return "", f"Error running command: {str(e)}", -1

    def check_file_exists(self, filename: str) -> bool:
        """Check if a file exists in the target directory."""
        if not self.target_dir:
            return False
        file_path = self.target_dir / filename
        return file_path.exists() and file_path.is_file()

    def read_file(self, filename: str) -> Optional[str]:
        """Read a file from the target directory."""
        if not self.target_dir:
            return None
        file_path = self.target_dir / filename
        try:
            return file_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            return None
