# ingdavidmurcia-de-toolkit
CLI personalizada para controlar una VM de Le Wagon desde la terminal local.

## 🚀 Instalación

## 1. Clona el repositorio:
git clone https://github.com/IngDavidMurcia/data-engineering-challenges.git

## Navega al paquete:
cd 01-Software-Engineering-Best-Practices/01-Setup/02-Package-Creation/ingdavidmurcia-de-toolkit

## Instala dependencias con Poetry:
poetry install

## 🛠️ Comandos disponibles
poetry run deng --help

## start - Inicia tu VM en GCP:
poetry run deng start

## stop - Detiene tu VM:
poetry run deng stop

## connect - Abre VS Code conectado por SSH a tu VM:
poetry run deng connect


💡 Asegúrate de tener configurado gcloud, acceso SSH y la extensión Remote - SSH en VS Code.

# 🔐 Requisitos
Python 3.12+
Poetry
Google Cloud SDK
VS Code con extensión Remote - SSH
Acceso a una VM en GCP con permisos de control

# 📦 Publicación (opcional)
Para publicar este paquete en PyPI o Gemfury, asegúrate de:
Tener un archivo pyproject.toml bien configurado
Incluir este README.md
Ejecutar:
poetry build
poetry publish

# 👨‍💻 Autor
David Murcia
Bootcamp Le Wagon – Data Engineering
GitHub: @IngDavidMurcia
