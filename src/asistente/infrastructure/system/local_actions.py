import os
from pathlib import Path
import stat
import subprocess
from difflib import get_close_matches


class LocalFiles:
    def __init__(self, root: Path, preview=False):
        self.root = root.absolute()
        self.preview = preview

    def path(self, name):
        # Only direct children: no traversal, ADS, devices, junctions or directories.
        if not name or name != name.strip() or name.endswith('.') or any(c in name for c in '/\\:<>"|?*') or any(ord(c) < 32 for c in name):
            raise ValueError("Usa solo un nombre de archivo, sin rutas ni símbolos reservados.")
        if name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))} or name in ('.', '..'):
            raise ValueError("Nombre reservado por Windows.")
        path = self.root / name
        for item in (path, self.root, *self.root.parents):
            if item.exists() or item.is_symlink():
                info = item.lstat()
                if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    raise ValueError("No se permiten enlaces ni junctions en la carpeta autorizada.")
        if path.exists() and not path.is_file():
            raise ValueError("Solo se permiten archivos individuales.")
        return path

    def inspect(self, name):
        info = self.path(name).stat()
        if info.st_nlink > 1:
            raise ValueError("No se permiten archivos con enlaces físicos.")
        return (info.st_ino, info.st_size, info.st_mtime_ns)

    def create(self, name):
        path = self.path(name)
        if self.preview:
            print(f"[Simulación: crear] {path}")
            return
        self.root.mkdir(parents=True, exist_ok=True)
        self.path(name)
        with path.open('x', encoding='utf-8'):
            pass

    def search(self, query):
        if not query.strip():
            raise ValueError("Indica parte del nombre que buscas.")
        self.path('validacion.txt')
        if not self.root.exists():
            return []
        names = []
        for item in self.root.iterdir():
            try:
                if self.path(item.name).is_file():
                    names.append(item.name)
            except ValueError:
                continue
        exact = [n for n in names if query.casefold() in n.casefold()]
        return sorted(exact or get_close_matches(query, names, n=10, cutoff=0.6))[:20]

    def trash(self, name, token):
        if self.inspect(name) != token:
            raise ValueError("El archivo cambió desde la confirmación; solicita el borrado nuevamente.")
        if self.preview:
            print(f"[Simulación: papelera] {name}")
            return
        from send2trash import send2trash
        send2trash(str(self.path(name)))


class ConfiguredLauncher:
    def __init__(self, entries, base, preview=False):
        self.entries, self.base, self.preview = entries, base, preview

    def open(self, name):
        from asistente.application.text_normalizer import normalize
        lookup = {normalize(k): v for k, v in self.entries.items()}
        key = normalize(name)
        if key not in lookup:
            suggestions = get_close_matches(key, lookup, n=1, cutoff=0.6)
            raise ValueError("Programa no configurado." + (f" ¿Quisiste decir {suggestions[0]}?" if suggestions else ""))
        value = lookup[key]
        if not isinstance(value, str) or not value:
            raise ValueError("Configura una ruta de ejecutable como texto, sin argumentos.")
        path = Path(os.path.expandvars(value)).expanduser()
        if not path.is_absolute():
            path = self.base / path
        if path.suffix.lower() != '.exe' or not path.is_file():
            raise ValueError("El programa debe apuntar a un archivo .exe existente.")
        if self.preview:
            print(f"[Simulación: programa] {path}")
        else:
            subprocess.Popen([str(path)], shell=False, cwd=path.parent)
