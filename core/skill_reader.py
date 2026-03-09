from pathlib import Path
import json


def list_skills(root: Path) -> list[str]:
    """Return skill folder names that contain a SKILL.md file."""
    if not root.exists():
        return []
    return sorted(
        d.name
        for d in root.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )


def load_skill(root: Path, name: str) -> dict:
    """Load skill data from folder: instructions, context, config."""
    skill_dir = root / name
    instructions = _read_file(skill_dir / "SKILL.md")
    context = _read_file(skill_dir / "CONTEXT.txt")
    config = _read_json(skill_dir / "config.json")
    return {"instructions": instructions, "context": context, "config": config}


def save_skill_md(root: Path, name: str, content: str) -> None:
    """Persist edited SKILL.md back to disk."""
    skill_file = root / name / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
