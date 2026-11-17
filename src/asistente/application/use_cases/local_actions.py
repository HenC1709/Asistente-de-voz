from asistente.domain.entities import CommandResult
from asistente.application.text_normalizer import normalize


class LocalActions:
    def __init__(self, files, launcher, monotonic):
        self.files, self.launcher, self.monotonic = files, launcher, monotonic
        self.pending = None

    def launch(self, name):
        self.launcher.open(name)
        return CommandResult(f"Abriendo {name}.")

    def search(self, name):
        matches = self.files.search(name)
        return CommandResult("Coincidencias: " + ", ".join(matches) if matches else "No encontré archivos.")

    def create(self, name):
        self.files.create(name)
        return CommandResult(f"Creado: {name}.")

    def delete(self, name):
        self.pending = None
        token = self.files.inspect(name)
        self.pending = (name, token, self.monotonic() + 20)
        return CommandResult(f"¿Enviar {name} a la papelera? Di confirmar borrado {name} en 20 segundos, o cancelar borrado.")

    def confirm(self, name):
        pending, self.pending = self.pending, None
        if not pending or self.monotonic() >= pending[2] or normalize(name) != normalize(pending[0]):
            return CommandResult("Confirmación inválida o vencida. Solicita el borrado nuevamente.")
        self.files.trash(pending[0], pending[1])
        return CommandResult(f"Enviado a la papelera: {pending[0]}.")

    def cancel(self, _):
        self.pending = None
        return CommandResult("Borrado cancelado.")
