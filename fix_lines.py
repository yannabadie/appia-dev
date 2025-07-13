#!/usr/bin/env python3
"""Script pour corriger automatiquement les lignes trop longues."""

import re


def fix_long_lines(file_path, max_length=79):
    """Corrige les lignes trop longues dans un fichier Python."""

    with open(file_path, "r") as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for _i, line in enumerate(lines):
        stripped = line.rstrip()

        # Si la ligne est trop longue
        if len(stripped) > max_length:
            # Patterns courants à corriger

            # Assertions longues
            if "assert " in stripped and "," in stripped:
                # Coupure après la première condition
                match = re.match(r"^(\s*assert\s+.+?),\s*(.+)$", stripped)
                if match:
                    condition, message = match.group(1), match.group(2)
                    base_indent = re.match(r"^(\s*)", stripped).group(1)
                    new_lines.append(f"{condition} (\n")
                    new_lines.append(f"{base_indent}    {message}\n")
                    modified = True
                    continue

            # F-strings longs
            if 'f"' in stripped and len(stripped) > max_length:
                # Essayer de couper les f-strings
                if '"' in stripped[stripped.find('f"') + 2 :]:
                    base_indent = re.match(r"^(\s*)", stripped).group(1)
                    # Solution simple: couper au milieu si possible
                    mid = len(stripped) // 2
                    # Chercher un bon point de coupure près du milieu
                    for offset in range(20):
                        for pos in [mid - offset, mid + offset]:
                            if 0 < pos < len(stripped) and stripped[pos] in [
                                " ",
                                "/",
                                ":",
                                "=",
                            ]:
                                new_lines.append(stripped[: pos + 1] + " \\\n")
                                new_lines.append(
                                    base_indent + "    " + stripped[pos + 1 :] + "\n"
                                )
                                modified = True
                                break
                        if modified:
                            break
                    if modified:
                        continue

            # URLs et chaînes longues
            if ("http" in stripped or "api." in stripped) and '"' in stripped:
                base_indent = re.match(r"^(\s*)", stripped).group(1)
                # Couper après les URLs ou chaînes
                for char in [", ", '" ', "/ ", "= "]:
                    if char in stripped:
                        pos = stripped.find(char)
                        if pos > 40:  # Assez long pour couper
                            new_lines.append(stripped[: pos + len(char)] + "\\\n")
                            new_lines.append(
                                base_indent
                                + "    "
                                + stripped[pos + len(char) :]
                                + "\n"
                            )
                            modified = True
                            break
                if modified:
                    continue

        new_lines.append(line)

    if modified:
        with open(file_path, "w") as f:
            f.writelines(new_lines)
        return True
    return False


if __name__ == "__main__":
    files = [
        "/workspaces/appia-dev/tests/test_connectivity.py",
        "/workspaces/appia-dev/tests/test_api_integration.py",
    ]

    for file_path in files:
        if fix_long_lines(file_path):
            print(f"Fixed {file_path}")
        else:
            print(f"No changes needed for {file_path}")
