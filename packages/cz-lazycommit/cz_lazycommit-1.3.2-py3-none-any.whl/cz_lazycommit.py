import re
import subprocess
from typing import Any, Dict, List, Optional

import questionary
from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import MAJOR, MINOR, PATCH
from questionary import Choice


class CommitEditor:
    """Handles different editing modes for commit messages with clean separation of concerns."""

    def __init__(self):
        self.commit_types = [
            Choice("feat: New feature", "feat"),
            Choice("fix: Bug fix", "fix"),
            Choice("docs: Documentation", "docs"),
            Choice("style: Formatting", "style"),
            Choice("refactor: Refactoring", "refactor"),
            Choice("test: Tests", "test"),
            Choice("chore: Maintenance", "chore"),
            Choice("perf: Performance", "perf"),
            Choice("ci: CI/CD", "ci"),
            Choice("build: Build system", "build"),
        ]

    def should_edit_commit(self) -> bool:
        """Ask if user wants to edit the commit."""
        return questionary.confirm("Do you want to edit this commit?").ask()

    def ask_edit_choice(self) -> str:
        """Ask what aspect of the commit to edit."""
        choice = questionary.select(
            "What would you like to edit?",
            choices=[
                Choice("Edit subject only (description text)", "subject"),
                Choice("Edit full commit (type, scope, subject)", "full"),
            ],
            default="subject",
            use_arrow_keys=True,
            use_jk_keys=True,
        ).ask()
        return choice if choice else "subject"

    def edit_subject_only(self, original_message: str, parsed: dict) -> str:
        """Edit only the subject/description part of the commit message."""
        print(f"\n📝 Current commit: {original_message}")
        print(f"   Type: {parsed.get('commit_type', 'feat')}")
        if parsed.get("scope"):
            print(f"   Scope: ({parsed.get('scope')})")
            print(f"   Subject: {parsed.get('subject', '')}")

            current_subject = parsed.get("subject", "")
            new_subject = questionary.text(
                "Edit subject (description):", default=current_subject
            ).ask()

            if new_subject and new_subject != current_subject:
                commit_type = parsed.get("commit_type", "feat")
                scope = parsed.get("scope", "")
                scope_part = f"({scope})" if scope else ""
                return f"{commit_type}{scope_part}: {new_subject}"

            return original_message

    def edit_full_commit(self, original_message: str, parsed: dict) -> str:
        """Edit commit type, scope, and subject separately with pre-filled defaults."""
        print(f"\n📝 Current commit: {original_message}")

        current_type = parsed.get("commit_type", "feat")
        current_scope = parsed.get("scope", "")
        current_subject = parsed.get("subject", "")

        new_type = questionary.select(
            "Select commit type:",
            choices=self.commit_types,
            default=current_type,
            use_arrow_keys=True,
            use_jk_keys=True,
        ).ask()

        new_scope = questionary.text(
            "Edit scope (leave empty to remove):", default=current_scope
        ).ask()

        new_subject = questionary.text("Edit subject:", default=current_subject).ask()

        scope_part = f"({new_scope})" if new_scope else ""
        return f"{new_type}{scope_part}: {new_subject}"

    def apply_edit_changes(
        self, original_message: str, edited_message: str, answers: dict
    ) -> bool:
        """Apply edited message changes to answers dict."""
        if edited_message and edited_message != original_message:
            new_parsed = self._parse_commit_message(edited_message)
            if new_parsed:
                answers.update(new_parsed)
                new_bump_level = self._detect_version_level(edited_message)
                if new_bump_level:
                    answers["bump_level"] = new_bump_level
                return True
        return False

    def _parse_commit_message(self, commit_msg: str) -> Optional[Dict[str, Any]]:
        """Parse a commit message into its components."""
        try:
            match = re.match(r"^(\w+)(?:\(([^)]+)\))?:\s*(.+)$", commit_msg.strip())
            if match:
                commit_type, scope, subject = match.groups()
                return {
                    "commit_type": commit_type,
                    "scope": scope or "",
                    "subject": subject,
                    "body": "",
                    "is_breaking_change": "BREAKING CHANGE" in commit_msg,
                    "breaking_changes": "",
                    "footer": "",
                }
            else:
                return {
                    "commit_type": "feat",
                    "scope": "",
                    "subject": commit_msg.strip(),
                    "body": "",
                    "is_breaking_change": False,
                    "breaking_changes": "",
                    "footer": "",
                }
        except:
            return None

    def _detect_version_level(self, commit_msg: str) -> Optional[str]:
        """Detect version bump level based on conventional commit mapping."""
        msg_lower = commit_msg.lower()

        if "breaking change" in msg_lower or "!" in commit_msg:
            return MAJOR

        if msg_lower.startswith("feat"):
            return MINOR

        if msg_lower.startswith("fix"):
            return PATCH

        return None


class CzLazycommitCz(BaseCommitizen):
    def __init__(self, config=None):
        super().__init__(config)
        self.editor = CommitEditor()

    def questions(self) -> list:
        """Enhanced questions with auto-detection from AI suggestions."""
        return [
            {
                "type": "confirm",
                "name": "is_breaking_change",
                "message": "Are there any breaking changes?",
                "default": False,
            },
            {
                "type": "input",
                "name": "breaking_changes",
                "message": "Describe the breaking changes:\n",
                "when": lambda x: x.get("is_breaking_change")
                and not x.get("breaking_changes"),
            },
            # TODO: integrate with gh for auto issue list
            {
                "type": "input",
                "name": "footer",
                "message": "Add any additional context or issue references (optional):",
                "when": lambda x: not x.get("footer"),  # Only show if not already set
            },
        ]

    def message(self, answers: dict) -> str:
        commit_messages = self._get_lazycommit_suggestions()
        if commit_messages:
            selected_message = self._select_commit_with_arrows(commit_messages)
            if selected_message:
                parsed = self._parse_commit_message(selected_message)
                if parsed:
                    answers.update(parsed)
                    bump_level = self._detect_version_level(selected_message)
                    if bump_level:
                        answers["bump_level"] = bump_level
                    self._handle_edit_workflow(selected_message, parsed, answers)

        return self._build_commit_message(answers)

    def _parse_commit_message(self, commit_msg: str) -> Optional[Dict[str, Any]]:
        """Parse a commit message into its components using the editor."""
        return self.editor._parse_commit_message(commit_msg)

    def _detect_version_level(self, commit_msg: str) -> Optional[str]:
        """Detect version bump level using the editor."""
        return self.editor._detect_version_level(commit_msg)

    def _handle_edit_workflow(
        self, selected_message: str, parsed: dict, answers: dict
    ) -> None:
        """Handle the complete edit workflow using the CommitEditor."""
        if self.editor.should_edit_commit():
            edit_choice = self.editor.ask_edit_choice()

            if edit_choice == "full":
                edited_message = self.editor.edit_full_commit(selected_message, parsed)
                self.editor.apply_edit_changes(
                    selected_message, edited_message, answers
                )

            elif edit_choice == "subject":
                edited_message = self.editor.edit_subject_only(selected_message, parsed)
                self.editor.apply_edit_changes(
                    selected_message, edited_message, answers
                )

    def _get_lazycommit_suggestions(self) -> List[str]:
        """Get commit suggestions from lazycommit."""
        try:
            subprocess.run(
                ["lazycommit", "config", "get"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print("Error: lazycommit not found. Please install lazycommit first.")
            print("Installation: go install github.com/m7medvision/lazycommit@latest")
            return []

        try:
            print("🤖 Generating commit messages using lazycommit...")
            result = subprocess.run(
                ["lazycommit", "commit"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                print(f"lazycommit error: {result.stderr}")
                if "No staged changes to commit." in result.stderr:
                    print("Please stage some changes first: git add <files>")
                return []

            return self._parse_lazycommit_output(result.stdout)

        except subprocess.TimeoutExpired:
            print("lazycommit timed out.")
            return []
        except Exception as e:
            print(f"Error running lazycommit: {e}")
            return []

    def _select_commit_with_arrows(self, commit_messages: List[str]) -> str:
        """Select a commit message using enhanced arrow navigation with preview."""
        try:
            return self._enhanced_commit_selector(commit_messages)
        except ImportError:
            return self._fallback_selector(commit_messages)

    def _enhanced_commit_selector(self, commit_messages: List[str]) -> str:
        """Enhanced commit selector using questionary for better compatibility."""

        def get_commit_bump_suggestion(msg: str) -> str:
            """Suggest version bump based on commit content."""
            msg_lower = msg.lower()
            if "breaking" in msg_lower or "!" in msg:
                return "MAJOR"
            elif msg_lower.startswith("feat"):
                return "MINOR"
            elif msg_lower.startswith("fix"):
                return "PATCH"
            else:
                return ""

        # Create enhanced choices with icons and bump suggestions
        choices = []
        for i, msg in enumerate(commit_messages):
            bump = get_commit_bump_suggestion(msg)
            display_text = f"[{i + 1:2d}] {bump:7s} │ {msg}"
            choices.append(Choice(title=display_text, value=msg))

        # Use questionary select with enhanced features
        selected = questionary.select(
            "🤖 Select a commit message:",
            choices=choices,
            use_arrow_keys=True,
            use_jk_keys=True,
            show_selected=False,
            instruction="↑/k:up ↓/j:down Enter:select",
            qmark="?",
        ).ask()

        if selected is None:
            return None

        return selected

    def _fallback_selector(self, commit_messages: List[str]) -> str:
        """Simple fallback selector when questionary is not available."""
        print(f"\nGenerated {len(commit_messages)} commit message suggestions:")
        print("=" * 60)
        for i, msg in enumerate(commit_messages, 1):
            print(f"{i:2d}. {msg}")
        print("=" * 60)

        while True:
            try:
                choice = input(
                    "Select a message (number) or press Enter for first: "
                ).strip()
                if not choice or choice == "1":
                    return commit_messages[0]
                elif choice.isdigit() and 1 <= int(choice) <= len(commit_messages):
                    return commit_messages[int(choice) - 1]
                else:
                    print(
                        f"Please enter a number between 1 and {len(commit_messages)} or press Enter"
                    )
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")

    def _build_commit_message(self, answers: dict) -> str:
        """Build the final commit message from answers."""
        commit_type = answers.get("commit_type", "feat")
        scope = answers.get("scope", "")
        subject = answers.get("subject", "")
        body = answers.get("body", "")
        is_breaking = answers.get("is_breaking_change", False)
        breaking_changes = answers.get("breaking_changes", "")
        footer = answers.get("footer", "")

        scope_part = f"({scope})" if scope else ""

        header = f"{commit_type}{scope_part}: {subject}"
        if is_breaking:
            header += "!"

        message_parts = [header]

        if body:
            message_parts.append("")
            message_parts.append(body)

        if is_breaking and breaking_changes:
            message_parts.append("")
            message_parts.append(f"BREAKING CHANGE: {breaking_changes}")

        if footer:
            message_parts.append("")
            message_parts.append(footer)

        return "\n".join(message_parts)

    def _parse_lazycommit_output(self, output: str) -> list:
        """
        Parse lazycommit output to extract commit messages.
        Your lazycommit outputs plain lines, one message per line.
        """
        lines = output.strip().split("\n")
        commit_messages = []

        for line in lines:
            line = line.strip()
            if line and self._looks_like_commit_message(line):
                commit_messages.append(line)

        return commit_messages

    def _looks_like_commit_message(self, line: str) -> bool:
        """
        Check if a line looks like a conventional commit message.
        """

        commit_types = [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "test",
            "chore",
            "build",
            "ci",
            "perf",
            "revert",
            "improve",
            "add",
            "update",
            "remove",
            "delete",
            "create",
            "implement",
        ]

        pattern = r"^(?:" + "|".join(commit_types) + r")(?:\([^)]+\))?:"
        return bool(re.match(pattern, line, re.IGNORECASE))

    def example(self) -> str:
        return "feat: add new user authentication system"

    def schema(self) -> str:
        return "<type>(<scope>): <subject>"

    def schema_pattern(self) -> str:
        return r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\(.+\))?: .+"

    def info(self) -> str:
        return """\
# cz-lazycommit

This plugin integrates with the lazycommit CLI tool to generate AI-powered commit messages.

## How it works

1. Stages your git changes
2. Calls lazycommit to generate commit message suggestions
3. Shows you the generated commit message
4. Allows you to confirm or edit the message
5. Creates the commit with the final message

## Requirements

- lazycommit CLI tool must be installed and configured
- git repository must have staged changes

## Installation

```bash
pip install cz-lazycommit
```

And make sure lazycommit is available:

```bash
go install github.com/m7medvision/lazycommit@latest
lazycommit config set  # Interactive setup
```

## Usage

```bash
git add <files>
cz --name cz_lazycommit commit
```
"""
