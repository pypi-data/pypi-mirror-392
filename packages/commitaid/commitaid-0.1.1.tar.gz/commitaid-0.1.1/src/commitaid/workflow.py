"""Main workflow logic for CommitAid."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# Placeholder URL for the commitaid slash command
COMMITAID_COMMAND_URL = "https://raw.githubusercontent.com/Ruclo/commitaid/main/commitaid-command.md"

# Default commit specification (Inspired by Conventional Commits)
DEFAULT_COMMIT_SPEC = """
Commit consists of header, body and footer.
Header contains type(feat, fix, docs, style, refactor, test, chore), optional scope and subject (50 characters max).
Body is optional and provides additional information.
Footer is optional and can include breaking changes.
Maximum line length is 72 characters.
""".strip()


class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run(
            ["which", command],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_staged_changes() -> bool:
    """
    Check if there are any staged changes ready to commit.

    Returns:
        True if there are staged changes, False otherwise
    """
    try:
        # git diff --cached --quiet returns 0 if no changes, 1 if there are changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
            text=True
        )
        return result.returncode == 1
    except subprocess.CalledProcessError:
        return False


def get_git_root() -> Optional[Path]:
    """Get the root directory of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None


def check_claude_command_exists() -> bool:
    """Check if /commitaid command exists in Claude CLI."""
    claude_commands_dir = Path.home() / ".claude" / "commands"
    command_file = claude_commands_dir / "commitaid.md"
    return command_file.exists()


def install_claude_command() -> bool:
    """Install the /commitaid command for Claude CLI."""
    claude_commands_dir = Path.home() / ".claude" / "commands"
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    command_file = claude_commands_dir / "commitaid.md"

    print("Installing /commitaid command for Claude CLI...")
    try:
        # Fetch the command file from GitHub
        result = subprocess.run(
            ["curl", "-fsSL", COMMITAID_COMMAND_URL],
            check=True,
            capture_output=True,
            text=True
        )

        with open(command_file, 'w') as f:
            f.write(result.stdout)

        print("✓ /commitaid command installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to download command file: {e}")
        return False
    except IOError as e:
        print(f"Error: Failed to write command file: {e}")
        return False


def run_claude_commitaid(commit_spec: Optional[str] = None) -> Optional[str]:
    """
    Run Claude CLI with /commitaid command.

    Args:
        commit_spec: Optional commit specification to pass to Claude.
                    If None, uses DEFAULT_COMMIT_SPEC.

    Returns:
        Generated commit message or None if failed
    """
    # Always set COMMITAID_SPEC, using default if not provided
    commit_spec_arg = commit_spec if commit_spec else DEFAULT_COMMIT_SPEC

    try:
        result = subprocess.run(
            ["claude", "-p", "/commitaid", commit_spec_arg],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: Claude command failed: {e}")
        if e.stderr:
            print(e.stderr)
        return None


def open_in_editor(content: str) -> Optional[str]:
    """
    Open content in user's preferred editor.

    Args:
        content: Initial content to edit

    Returns:
        Edited content or None if cancelled
    """
    # Get git root for tempfile location
    git_root = get_git_root()
    if not git_root:
        raise WorkflowError("Could not determine git root directory")

    git_dir = git_root / ".git"
    if not git_dir.exists():
        raise WorkflowError(".git directory not found")

    # Create tempfile in .git directory
    temp_fd, temp_path = tempfile.mkstemp(
        suffix=".txt",
        prefix="COMMIT_EDITMSG_",
        dir=str(git_dir),
        text=True
    )

    try:
        # Write initial content
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)

        # Get editor from environment or use default
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vim"))

        # Open editor
        subprocess.run([editor, temp_path], check=True)

        # Ask for confirmation before proceeding
        print("\nProceed with this commit message? (y/n): ", end='', flush=True)
        confirmation = input().strip().lower()

        if confirmation not in ('y', 'yes'):
            return None

        # Read edited content
        with open(temp_path, 'r') as f:
            edited_content = f.read().strip()

        return edited_content if edited_content else None

    except subprocess.CalledProcessError as e:
        print(f"Error: Editor failed: {e}")
        return None
    except IOError as e:
        print(f"Error: Failed to read/write tempfile: {e}")
        return None
    finally:
        # Clean up tempfile
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def run_git_commit(message: str, signoff: bool = False) -> bool:
    """
    Run git commit with the provided message.

    Args:
        message: Commit message
        signoff: Whether to add Signed-off-by line

    Returns:
        True if successful, False otherwise
    """
    cmd = ["git", "commit", "-m", message]
    if signoff:
        cmd.append("-s")

    try:
        subprocess.run(cmd, check=True)
        print("✓ Commit created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Git commit failed: {e}")
        return False


def run_workflow(commit_spec: Optional[str] = None, auto_signoff: bool = False):
    """
    Run the main CommitAid workflow.

    Args:
        commit_spec: Optional commit specification
        auto_signoff: Whether to add Signed-off-by line
    """
    # Check if git is installed
    if not check_command_exists("git"):
        raise WorkflowError("git is not installed or not in PATH")

    # Check if in git repo
    if not check_git_repo():
        raise WorkflowError("Not in a git repository")

    # Check for staged changes
    if not check_staged_changes():
        raise WorkflowError(
            "No staged changes found\n"
            "Use 'git add' to stage changes before running commitaid"
        )

    # Display configuration
    print(f"Auto sign-off: {'enabled' if auto_signoff else 'disabled'}")
    if commit_spec:
        print(f"Commit spec: custom")
    else:
        print(f"Commit spec: Conventional Commits-like format")

    # Check if claude CLI is installed
    if not check_command_exists("claude"):
        raise WorkflowError(
            "Claude CLI is not installed or not in PATH\n"
            "Install it from: https://docs.claude.com/en/docs/claude-code"
        )

    # Check if /commitaid command exists, install if not
    if not check_claude_command_exists():
        if not install_claude_command():
            raise WorkflowError("Failed to install /commitaid command")

    # Run Claude to generate commit message
    print("Generating commit message with Claude...")
    commit_message = run_claude_commitaid(commit_spec)

    if not commit_message:
        raise WorkflowError("Failed to generate commit message")

    # Open in editor for user to review/edit
    print("Opening editor for review...")
    edited_message = open_in_editor(commit_message)

    if not edited_message:
        print("Commit cancelled")
        return

    # Run git commit
    run_git_commit(edited_message, signoff=auto_signoff)
