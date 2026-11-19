"""A tiny example showing how to add a feature module."""

from universal_framework import AppConfig, Application, ModuleDefinition


def greet(app: Application) -> str:
    message = f"Hello from {app.config.app_name}!"
    print(message)
    return message


def main() -> None:
    config = AppConfig(app_name="My First App")
    app = Application(config)
    app.register_module(ModuleDefinition(name="greeting", handler=greet))

    with app:
        app.run_module("greeting")


if __name__ == "__main__":
    main()
