"""
Core functionality for executing MashDB queries.
"""

import json
import subprocess
from pathlib import Path
from typing import Union, Dict, Any


def _get_mashdb_bin_path() -> Path:
    """Get the path to the MashDB binary."""
    path = Path(__file__).parent / "bin" / "MashDB"
    if not path.exists():
        raise FileNotFoundError(
            f"MashDB binary not found at {path}. "
            "Please ensure it's properly installed."
        )
    # Ensure the binary is executable
    path.chmod(0o755)
    return path


def query(sql: str, as_json: bool = False) -> Union[str, Dict[str, Any]]:
    """
    Execute a SQL query against MashDB.
    
    Args:
        sql: SQL query string to execute
        as_json: If True, parse the output as JSON
        
    Returns:
        Query result as string or parsed JSON dictionary
    """
    cmd = [str(_get_mashdb_bin_path())]
    if as_json:
        cmd.append("--json")
    cmd.append(sql)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if as_json:
            return json.loads(result.stdout)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error occurred"
        raise RuntimeError(f"Query failed: {error_msg}")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON response from database")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")
