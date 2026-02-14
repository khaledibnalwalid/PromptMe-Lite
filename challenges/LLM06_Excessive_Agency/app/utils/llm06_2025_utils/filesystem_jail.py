from pathlib import Path
import os

class SecurityError(Exception):
    """Raised when security violation is detected"""
    pass

class FileSystemJail:
    """
    Sandboxed filesystem that prevents directory traversal attacks.
    Even if LLM generates malicious paths, code enforces boundaries.
    """

    def __init__(self, jail_root: Path):
        """
        Initialize jail with root directory.
        All file operations are confined to this directory.
        """
        self.jail_root = jail_root.resolve()

        # Ensure jail directory exists
        if not self.jail_root.exists():
            raise ValueError(f"Jail directory does not exist: {self.jail_root}")

        if not self.jail_root.is_dir():
            raise ValueError(f"Jail path must be a directory: {self.jail_root}")

    def safe_path(self, user_path: str) -> Path:
        """
        Convert user input to safe path inside jail.
        Prevents directory traversal attacks like ../../../etc/passwd

        Args:
            user_path: User-provided path (potentially malicious)

        Returns:
            Safe Path object inside jail

        Raises:
            SecurityError: If path escapes jail
        """
        # Normalize path (remove .., //, etc.)
        clean_path = Path(user_path).as_posix()

        # Block absolute paths
        if clean_path.startswith("/"):
            raise SecurityError("Absolute paths not allowed")

        # Block parent directory traversal
        if ".." in clean_path:
            raise SecurityError("Directory traversal blocked")

        # Join with jail root and resolve
        full_path = (self.jail_root / clean_path).resolve()

        # Security check: ensure we're still inside jail
        try:
            full_path.relative_to(self.jail_root)
        except ValueError:
            raise SecurityError(f"Path escape attempt blocked: {user_path}")

        return full_path

    def read_file(self, filename: str) -> tuple[bool, str, str]:
        """
        Read file content if it exists inside jail.

        Args:
            filename: Name of file to read

        Returns:
            Tuple of (found, file_id, content)
        """
        try:
            safe_file_path = self.safe_path(filename)

            if not safe_file_path.exists():
                return False, "", "File not found in accessible directory"

            if not safe_file_path.is_file():
                return False, "", "Path is not a file"

            content = safe_file_path.read_text(encoding='utf-8')
            return True, str(safe_file_path), content

        except SecurityError as e:
            return False, "", f"⛔ Security violation: {e}"
        except Exception as e:
            return False, "", f"❌ Error reading file: {e}"

    def list_files(self) -> dict:
        """
        List all files in jail directory recursively.

        Returns:
            Dictionary with folder structure
        """
        result = {}

        try:
            # Get jail folder name
            jail_name = self.jail_root.name
            result[jail_name] = []

            # Walk through all files in jail
            for item in self.jail_root.rglob("*"):
                if item.is_file():
                    # Get relative path from jail root
                    rel_path = item.relative_to(self.jail_root)
                    result[jail_name].append(str(rel_path))

            return result

        except Exception as e:
            return {"error": f"Failed to list files: {e}"}

    def search_file_recursive(self, filename: str) -> tuple[bool, str, str]:
        """
        Search for a file recursively in jail.

        Args:
            filename: Name of file to search for

        Returns:
            Tuple of (found, file_path, content)
        """
        try:
            # Search recursively
            for item in self.jail_root.rglob("*"):
                if item.is_file() and item.name.lower() == filename.lower():
                    content = item.read_text(encoding='utf-8')
                    return True, str(item), content

            return False, "", "File not found in accessible directory"

        except SecurityError as e:
            return False, "", f"⛔ Security violation: {e}"
        except Exception as e:
            return False, "", f"❌ Error searching file: {e}"


def get_accessible_jail() -> FileSystemJail:
    """Get jail for regular users (accessible directory)"""
    base_dir = Path(__file__).parent.parent.parent.parent / "file_storage"
    accessible_dir = base_dir / "accessible"
    return FileSystemJail(accessible_dir)


def get_restricted_jail() -> FileSystemJail:
    """Get jail for admin users (restricted directory)"""
    base_dir = Path(__file__).parent.parent.parent.parent / "file_storage"
    restricted_dir = base_dir / "restricted"
    return FileSystemJail(restricted_dir)


def get_whole_jail() -> FileSystemJail:
    """Get jail with access to all directories (admin only)"""
    base_dir = Path(__file__).parent.parent.parent.parent / "file_storage"
    return FileSystemJail(base_dir)
