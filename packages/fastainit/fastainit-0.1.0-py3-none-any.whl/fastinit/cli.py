import argparse
import locale
from textwrap import dedent
from pathlib import Path
import pyfiglet


def get_lang():
    lang, _ = locale.getlocale()
    if lang is None:
        return "en"
    return lang

def safe_mkdir(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def print_banner():
    banner = pyfiglet.figlet_format("fastinit")
    my_name = "by jp066"
    banner += f"\n{' ' * (len(banner.splitlines()[0]) - len(my_name))}{my_name}\n"
    if get_lang().startswith("pt"):
        help_text = "- Use 'fastinit new <nome_projeto>' para criar um novo projeto FastAPI.\n" \
                    "- Use 'fastinit g module <nome_projeto> <nome_modulo>' para criar um novo módulo."
        banner += f"\n{' ' * (len(banner.splitlines()[0]) - len(help_text))}{help_text}\n"

    else:
        help_text = "- Use 'fastinit new <project_name>' to create a new FastAPI project.\n" \
                    "- Use 'fastinit g module <project_name> <module_name>' to create a new module."
        banner += f"\n{' ' * (len(banner.splitlines()[0]) - len(help_text))}{help_text}\n"
    banner_paint = "\033[95m" + banner + "\033[0m"
    print(banner_paint)

def create_project(name: str):
    base = Path(name)
    if base.exists():
        print(f"Projeto '{name}' já existe. Aborte para evitar sobrescrever.")
        return

    dirs = [
        base / "app" / "api" / "v1" / "routes",
        base / "app" / "models",
        base / "app" / "schemas",
        base / "app" / "services",
        base / "app" / "core",
        base / "app" / "db",
    ]

    for d in dirs:
        safe_mkdir(d)

    files = {
        base / "app" / "main.py": dedent("""\
            from fastapi import FastAPI
            from app.api.v1.routes import router as api_router

            app = FastAPI()
            app.include_router(api_router)
        """),

        base / "app" / "api" / "v1" / "routes" / "__init__.py": dedent("""\
            from fastapi import APIRouter
            router = APIRouter()
        """),

        base / "app" / "core" / "config.py": dedent("""\
            from pydantic import BaseSettings

            class Settings(BaseSettings):
                APP_NAME: str = "FastAPI App"

            settings = Settings()
        """),

        base / "app" / "db" / "session.py": "# Configure database session here\n",

        base / "README.md": f"# {name}\n\nProjeto FastAPI gerado com fastinit.\n",

        base / "requirements.txt": "fastapi\nuvicorn\npydantic\n",
    }

    for path, content in files.items():
        with open(path, "w", encoding="utf8") as f:
            f.write(content)

    lang = get_lang()
    if lang.startswith("pt"):
        print(f"✔ Projeto '{name}' criado com sucesso.")
        print("Dá uma olhada no meu github aí -> https://github.com/jp066")
    else:
        print(f"✔ Project '{name}' created successfully.")
        print("Check out my github -> https://github.com/jp066")

def create_module(project_name: str, module_name: str):
    base = Path(project_name)
    if not base.exists():
        if get_lang().startswith("pt"):
            print(f"Projeto '{project_name}' não encontrado. Aborte.")
        else:
            print(f"Project '{project_name}' not found. Aborting.")
        return

    routes_dir = base / "app" / "api" / "v1" / "routes"
    schemas_dir = base / "app" / "schemas"
    models_dir = base / "app" / "models"
    services_dir = base / "app" / "services"

    for d in [routes_dir, schemas_dir, models_dir, services_dir]:
        safe_mkdir(d)

    files = {
        routes_dir / f"{module_name}.py": dedent(f"""\
            from fastapi import APIRouter
            router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])

            @router.get("/")
            def list_{module_name}():
                return {{"message": "list {module_name}"}}
        """),

        schemas_dir / f"{module_name}.py": dedent(f"""\
            from pydantic import BaseModel

            class {module_name.capitalize()}(BaseModel):
                id: int
                name: str
        """),

        models_dir / f"{module_name}.py": dedent(f"""\
            # SQLAlchemy model for {module_name}
            # Add Base import and table definition here
        """),

        services_dir / f"{module_name}_service.py": dedent(f"""\
            # Business logic service for {module_name}
            def get_all():
                return ["example"]
        """),
    }

    for path, content in files.items():
        with open(path, "w", encoding="utf8") as f:
            f.write(content)

    lang = get_lang()
    if lang.startswith("pt"):
        print(f"✔ Módulo '{module_name}' criado com sucesso no projeto '{project_name}'.")
        print("Vê lá meu github po -> https://github.com/jp066")
    else:
        print(f"✔ Module '{module_name}' created successfully in project '{project_name}'.")
        print("Check out my github -> https://github.com/jp066")


def main():
#    print_banner()
    parser = argparse.ArgumentParser(description="fastinit CLI - Gerador de projetos FastAPI")
    subparsers = parser.add_subparsers(dest="command", required=False)

    new_parser = subparsers.add_parser("new", help="Criar novo projeto FastAPI")
    new_parser.add_argument("name", help="Nome do projeto")
    
    init_parser = subparsers.add_parser("init", help="Inicializar fastinit no diretório atual")
    init_parser.add_argument("init", help="Nome do projeto") # Se o usuario apenas digitar 'fastinit init', o argparse espera um argumento
    
    g_parser = subparsers.add_parser("g", help="Gerar módulo no projeto")
    g_parser.add_argument("project", help="Nome do projeto")
    g_parser.add_argument("type", choices=["module"], help="Tipo de artefato a gerar")
    g_parser.add_argument("name", help="Nome do módulo")
    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)
    elif args.command == "g":
        if args.type == "module":
            create_module(args.project, args.name)
    elif not args.command: # Se nenhum comando for fornecido, apenas exibe o banner
        print_banner()

if __name__ == "__main__":
    main()
