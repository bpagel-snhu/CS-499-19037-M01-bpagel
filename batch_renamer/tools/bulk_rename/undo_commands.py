from pathlib import Path
from ...logging_config import rename_logger as logger
import os

class RenameCommand:
    def __init__(self, old_path: str, new_path: str):
        self.old = old_path
        self.new = new_path

    def execute(self):
        Path(self.old).rename(self.new)

    def undo(self):
        Path(self.new).rename(self.old)

class BatchOperation:
    def __init__(self):
        self.commands: list[RenameCommand] = []
        self.id: int = None  # optional, for future persistence
        self._executed: list[RenameCommand] = []  # Track executed commands

    def add(self, cmd: RenameCommand):
        self.commands.append(cmd)

    def execute_all(self):
        self._executed = []
        for cmd in self.commands:
            try:
                cmd.execute()
                self._executed.append(cmd)
            except Exception as e:
                # Stop on first failure
                break

    def undo(self, folder_path=None, dry_run=False):
        # Evaluate file states
        undone = []
        skipped = []
        conflicts = []
        missing = []
        already_restored = []
        all_new_exist = True
        all_old_exist = True
        folder_files = set()
        if folder_path:
            try:
                folder_files = set(os.listdir(folder_path))
            except Exception as e:
                logger.warning(f"Could not list folder for undo: {e}")
        # Use only executed commands for undo
        commands_to_undo = self._executed if self._executed else self.commands
        for cmd in reversed(commands_to_undo):
            old_exists = Path(cmd.old).exists()
            new_exists = Path(cmd.new).exists()
            if folder_files:
                # Only warn if there are fewer files than the batch size (possible deletion)
                if len(folder_files) < len(self.commands):
                    logger.warning(f"Undo: file count in folder ({len(folder_files)}) is less than batch size ({len(self.commands)})")
            if new_exists and not old_exists:
                all_old_exist = False
            elif old_exists and not new_exists:
                all_new_exist = False
            elif new_exists and old_exists:
                conflicts.append((cmd.old, cmd.new))
                all_new_exist = False
                all_old_exist = False
            elif not new_exists and not old_exists:
                missing.append((cmd.old, cmd.new))
                all_new_exist = False
                all_old_exist = False
        if conflicts:
            return {"status": "conflict", "conflicts": conflicts, "undone": [], "skipped": [], "missing": missing, "already_restored": []}
        if all_old_exist and not all_new_exist:
            return {"status": "already_restored", "conflicts": [], "undone": [], "skipped": [], "missing": missing, "already_restored": [ (cmd.old, cmd.new) for cmd in commands_to_undo ]}
        for cmd in reversed(commands_to_undo):
            old_exists = Path(cmd.old).exists()
            new_exists = Path(cmd.new).exists()
            if new_exists and not old_exists:
                if not dry_run:
                    try:
                        cmd.undo()
                        undone.append((cmd.old, cmd.new))
                    except Exception as e:
                        skipped.append((cmd.old, cmd.new, str(e)))
                else:
                    undone.append((cmd.old, cmd.new))
            elif old_exists and not new_exists:
                already_restored.append((cmd.old, cmd.new))
            elif new_exists and old_exists:
                skipped.append((cmd.old, cmd.new, "conflict"))
            else:
                missing.append((cmd.old, cmd.new))
        status = "partial" if (skipped or missing or already_restored) else "success"
        return {"status": status, "conflicts": conflicts, "undone": undone, "skipped": skipped, "missing": missing, "already_restored": already_restored}
