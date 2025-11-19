# adb_utils.py
import subprocess

def run_adb_command(args: str) -> str:
    result = subprocess.run(
        f"adb {args}",
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # 1. Если ненулевой код — точно ошибка
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "ADB command failed"
        raise RuntimeError(err)

    # 2. Если код 0, но в stderr есть признаки ошибки — тоже ошибка
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()

    # Ищем типичные ошибки content query / am start
    if stderr and (
        "Error while accessing provider" in stderr or
        "java.lang." in stderr or
        "SecurityException" in stderr or
        "ActivityNotFoundException" in stderr or
        "IllegalArgumentException" in stderr or
        "NullPointerException" in stderr
    ):
        raise RuntimeError(stderr)

    # 3. Дополнительно: если stdout содержит "Error:" (иногда в stdout!)
    if stdout and "Error:" in stdout:
        raise RuntimeError(stdout)

    # Успех
    return stdout or stderr  # иногда результат в stderr (редко)