def get_default_repository_path(slug: str) -> str:
    """
    Convert a repository slug to a repository URL.
    """
    slug = slug.strip().lower()
    return f"universal-mcp-{slug}"


def get_default_package_name(slug: str) -> str:
    """
    Convert a repository slug to a package name.
    """
    slug = slug.strip().lower()
    package_name = f"universal_mcp_{slug.replace('-', '_')}"
    return package_name


def get_default_module_path(slug: str) -> str:
    """
    Convert a repository slug to a module path.
    """
    package_name = get_default_package_name(slug)
    module_path = f"{package_name}.app"
    return module_path


def get_default_class_name(slug: str) -> str:
    """
    Convert a repository slug to a class name.
    """
    slug = slug.strip().lower()
    class_name = "".join(part.capitalize() for part in slug.split("-")) + "App"
    return class_name
