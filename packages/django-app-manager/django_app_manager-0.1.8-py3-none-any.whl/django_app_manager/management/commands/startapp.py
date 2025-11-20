import importlib
from pathlib import Path
from django.core.management.base import CommandParser, CommandError
from django.core.management.templates import TemplateCommand
from django.core.management.commands.startapp import Command as StartAppCommand
from django.conf import settings, ENVIRONMENT_VARIABLE
from django.core.management.utils import (
    find_formatters,
    handle_extensions,
    run_formatters,
)
from django.template import Context, Engine
from django.utils.version import get_docs_version
import django
import shutil
import os
import libcst as cst


class Command(TemplateCommand):
    help = StartAppCommand.help
    missing_args_message = StartAppCommand.missing_args_message

    def add_arguments(self, parser: CommandParser):

        super().add_arguments(parser)
        self.settings_module = os.environ[ENVIRONMENT_VARIABLE]
        root_module_set = hasattr(settings, "ROOT_MODULE")
        if root_module_set and settings.ROOT_MODULE != "":
            self.root_module_guess = settings.ROOT_MODULE
        else:
            root_mod_parts = self.settings_module.removesuffix(".settings").split(".")
            if len(root_mod_parts) > 1:
                root_mod_parts = root_mod_parts[:-1]
            else:
                root_mod_parts = []
            self.root_module_guess = ".".join(root_mod_parts)

        if self.root_module_guess != "":
            parser.add_argument(
                "--root-module",
                help=(
                    "The root module used in the created AppConfig.name, recommended to be set with: "
                    + self.settings_module
                    + ".ROOT_MODULE (default: %(default)s"
                    + (" *guessed*" if not root_module_set else "")
                    + ")."
                ),
                default=self.root_module_guess,
            )
        parser.add_argument(
            "-i",
            "--install",
            action="store_true",
            help="Install the new app into the INSTALLED_APPS setting of the project's settings module.",
        )
        parser.add_argument(
            "-iu",
            "--include-urls",
            action="store_true",
            help="Include the new app's URLs into the project's root URLconf.",
        )
        parser.add_argument(
            "-a",
            "--install-all",
            action="store_true",
            help="Install the new app into INSTALLED_APPS and include its URLs into the root URLconf.",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Do not make any changes to settings or URLconf, only create the app structure.",
        )

    def handle(self, **options):
        dry_run = options.pop("dry_run", False)
        app_name = options.pop("name")
        target = options.pop("directory")
        root_module = options.pop("root_module", self.root_module_guess)
        root_module = (root_module + ".") if root_module != "" else ""
        template_result = self.template_handle(
            "app", app_name, target, root_module=root_module, **options
        )
        if options.get("install") or options.get("install_all"):
            self._install_app(app_name, root_module, dry_run=dry_run)
        if options.get("include_urls") or options.get("install_all"):
            self._install_urls(app_name, root_module, dry_run=dry_run)

        return template_result

    def template_handle(
        self, app_or_project, name, target=None, root_module=None, **options
    ):
        self.app_or_project = app_or_project
        self.a_or_an = "an" if app_or_project == "app" else "a"
        self.paths_to_remove = []
        self.verbosity = options["verbosity"]
        if root_module is None:
            root_module = self.root_module_guess
        self.validate_name(name)

        # if some directory is given, make sure it's nicely expanded
        if target is None:
            # top_dir = os.path.join(os.getcwd(), name)
            top_dir = os.path.join(settings.BASE_DIR, name)
            try:
                os.makedirs(top_dir)
            except FileExistsError:
                raise CommandError("'%s' already exists" % top_dir)
            except OSError as e:
                raise CommandError(e)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))
            if app_or_project == "app":
                self.validate_name(os.path.basename(top_dir), "directory")
            if not os.path.exists(top_dir):
                raise CommandError(
                    "Destination directory '%s' does not "
                    "exist, please create it first." % top_dir
                )

        # Find formatters, which are external executables, before input
        # from the templates can sneak into the path.
        formatter_paths = find_formatters()

        extensions = tuple(handle_extensions(options["extensions"]))
        extra_files = []
        excluded_directories = [".git", "__pycache__"]
        for file in options["files"]:
            extra_files.extend(map(lambda x: x.strip(), file.split(",")))
        if exclude := options.get("exclude"):
            for directory in exclude:
                excluded_directories.append(directory.strip())
        if self.verbosity >= 2:
            self.stdout.write(
                "Rendering %s template files with extensions: %s"
                % (app_or_project, ", ".join(extensions))
            )
            self.stdout.write(
                "Rendering %s template files with filenames: %s"
                % (app_or_project, ", ".join(extra_files))
            )
        base_name = "%s_name" % app_or_project
        base_subdir = "%s_template" % app_or_project
        base_directory = "%s_directory" % app_or_project
        camel_case_name = "camel_case_%s_name" % app_or_project
        camel_case_value = "".join(x for x in name.title() if x != "_")

        context = Context(
            {
                **options,
                base_name: name,
                base_directory: top_dir,
                camel_case_name: camel_case_value,
                "root_module": root_module,
                "docs_version": get_docs_version(),
                "django_version": django.__version__,
            },
            autoescape=False,
        )

        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        custom_template_dir = Path(__file__).parent.parent.parent / "conf" / base_subdir
        if options.get("template") is not None or not (
            custom_template_dir.exists() and custom_template_dir.is_dir()
        ):
            template_dir = self.handle_template(options["template"], base_subdir)
        else:
            template_dir = str(custom_template_dir.absolute().resolve())

        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if "exclude" not in options:
                    if dirname.startswith(".") or dirname == "__pycache__":
                        dirs.remove(dirname)
                elif dirname in excluded_directories:
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith((".pyo", ".pyc", ".py.class")):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(
                    top_dir, relative_dir, filename.replace(base_name, name)
                )
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path.removesuffix(old_suffix) + new_suffix
                        break  # Only rewrite once

                if os.path.exists(new_path):
                    raise CommandError(
                        "%s already exists. Overlaying %s %s into an existing "
                        "directory won't replace conflicting files."
                        % (
                            new_path,
                            self.a_or_an,
                            app_or_project,
                        )
                    )

                # Only render the Python files, as we don't want to
                # accidentally render Django templates files
                if new_path.endswith(extensions) or filename in extra_files:
                    with open(old_path, encoding="utf-8") as template_file:
                        content = template_file.read()
                    template = Engine().from_string(content)
                    content = template.render(context)
                    with open(new_path, "w", encoding="utf-8") as new_file:
                        new_file.write(content)
                else:
                    shutil.copyfile(old_path, new_path)

                if self.verbosity >= 2:
                    self.stdout.write("Creating %s" % new_path)
                try:
                    self.apply_umask(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path,
                        self.style.NOTICE,
                    )

        if self.paths_to_remove:
            if self.verbosity >= 2:
                self.stdout.write("Cleaning up temporary files.")
            for path_to_remove in self.paths_to_remove:
                if os.path.isfile(path_to_remove):
                    os.remove(path_to_remove)
                else:
                    shutil.rmtree(path_to_remove)

        run_formatters([top_dir], **formatter_paths, stderr=self.stderr)

    def _install_app(
        self, app_name: str, root_module: str, dry_run: bool = False
    ) -> None:

        settings_module = importlib.import_module(self.settings_module)
        settings_path = Path(settings_module.__file__).resolve()
        settings_cst = cst.parse_module(settings_path.read_bytes())
        if self.verbosity >= 1:
            self.stdout.write(
                f"Installing app '{self.style.NOTICE(app_name)}' into {self.style.WARNING(self.settings_module + '.INSTALLED_APPS')}..."
            )
        transformer = SettingsTransformer(app_name, root_module)
        modified_cst = settings_cst.visit(transformer)
        if not dry_run:
            settings_path.write_text(modified_cst.code, encoding="utf-8")
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully installed app '{app_name}' into {self.settings_module}.INSTALLED_APPS."
                )
            )

    def _install_urls(
        self, app_name: str, root_module: str, dry_run: bool = False
    ) -> None:

        urls_mod = importlib.import_module(settings.ROOT_URLCONF)
        urls_path = Path(urls_mod.__file__).resolve()
        urls_cst = cst.parse_module(urls_path.read_bytes())

        if self.verbosity >= 1:
            self.stdout.write(
                f"Adding URL include for app '{self.style.NOTICE(app_name)}' into {self.style.WARNING(settings.ROOT_URLCONF + '.urlpatterns')}..."
            )
        transformer = UrlsTransformer(app_name, root_module)
        modified_cst = urls_cst.visit(transformer)
        if not dry_run:
            urls_path.write_text(modified_cst.code, encoding="utf-8")
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully added URL include for app '{app_name}' into {settings.ROOT_URLCONF}.urlpatterns."
                )
            )


class SettingsTransformer(cst.CSTTransformer):
    def __init__(self, app_name: str, root_project_import: str) -> None:
        super().__init__()
        self.app_name = app_name
        self.root_project_import = root_project_import

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> cst.BaseExpression:
        updated_node = self._update_installed_apps(updated_node)

        return updated_node

    def _update_installed_apps(self, node: cst.Assign) -> cst.Assign:
        app_name = f"{self.root_project_import}{self.app_name}"

        if (
            len(node.targets) == 1
            and isinstance(node.targets[0].target, cst.Name)
            and node.targets[0].target.value == "INSTALLED_APPS"
            and isinstance(node.value, cst.List)
            and not any(
                isinstance(el.value, cst.SimpleString)
                and el.value.evaluated_value == app_name
                for el in node.value.elements
            )
        ):
            ## Add the new app to the list on a new line
            if isinstance(
                node.value.lbracket.whitespace_after, cst.ParenthesizedWhitespace
            ):
                whitespace_after = node.value.lbracket.whitespace_after
            else:
                whitespace_after = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(
                        whitespace=cst.SimpleWhitespace(
                            value="",
                        ),
                        comment=None,
                        newline=cst.Newline(
                            value=None,
                        ),
                    ),
                    empty_lines=[],
                    indent=True,
                    last_line=cst.SimpleWhitespace(
                        value="    ",
                    ),
                )
            existing_elements = list(node.value.elements)
            new_elements = []
            for elm in existing_elements:
                updated_elm = elm.with_changes(
                    comma=cst.Comma(whitespace_after=whitespace_after),
                )
                new_elements.append(updated_elm)
            new_elements = list(node.value.elements)
            added_elements = []
            if len(new_elements) == 0:
                use_comma = cst.Comma()
                quote = '"'
            else:
                use_comma = new_elements[-1].comma
                if len(new_elements) >= 2:
                    new_elements[-1] = new_elements[-1].with_changes(
                        comma=new_elements[-2].comma
                    )

                last_elm = new_elements[-1].value
                if isinstance(last_elm, cst.SimpleString):
                    quote = last_elm.quote
                else:
                    quote = '"'

                new_elements.extend(reversed(added_elements))
            new_elements.append(
                cst.Element(
                    value=cst.SimpleString(f"{quote}{app_name}{quote}"),
                    comma=use_comma,
                )
            )
            new_list = node.value.with_changes(elements=new_elements)
            return node.with_changes(value=new_list)
        return node


class UrlsTransformer(cst.CSTTransformer):
    def __init__(self, app_name: str, root_project_import: str) -> None:
        super().__init__()
        self.app_name = app_name
        self.root_project_import = root_project_import

        self.required_imports: set[tuple[str, tuple[str]]] = set(
            [
                ("django.urls", ("path", "include")),
            ]
        )

    def leave_Module(self, original_node, updated_node: cst.Module):
        found_imports: set[tuple[str, set[str]]] = set()
        new_module_body: list[cst.SimpleStatementLine] = []
        for stmt in updated_node.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                new_body = []
                for elem in stmt.body:
                    if isinstance(elem, cst.ImportFrom):
                        module_name = ""
                        if isinstance(elem.module, cst.Name):
                            module_name = elem.module.value
                        elif isinstance(elem.module, cst.Attribute):
                            names = []
                            attr = elem.module
                            while isinstance(attr, cst.Attribute):
                                names.append(attr.attr.value)
                                attr = attr.value
                            if isinstance(attr, cst.Name):
                                names.append(attr.value)
                            module_name = ".".join(reversed(names))
                        imported_names = [
                            alias.name.value
                            for alias in elem.names
                            if isinstance(alias, cst.ImportAlias)
                        ]
                        new_names = list(elem.names)
                        for req_module, req_names in self.required_imports:
                            if module_name == req_module:
                                needed_ = set(req_names) - set(imported_names)
                                new_names.extend(
                                    [
                                        cst.ImportAlias(name=cst.Name(name))
                                        for name in needed_
                                    ]
                                )
                                found_imports.add((req_module, req_names))

                        new_body.append(elem.with_changes(names=new_names))
                    else:
                        new_body.append(elem)
                new_module_body.append(stmt.with_changes(body=new_body))
            else:
                new_module_body.append(stmt)

        needed_imports = self.required_imports - found_imports
        if len(needed_imports) == 0:
            return updated_node.with_changes(body=new_module_body)

        last_import_index = updated_node.body.index(
            next(
                (
                    stmt
                    for stmt in reversed(new_module_body)
                    if isinstance(stmt, cst.SimpleStatementLine)
                    and any(
                        isinstance(elem, cst.Import) or isinstance(elem, cst.ImportFrom)
                        for elem in stmt.body
                    )
                ),
                None,
            )
        )

        new_imports = []
        for module_name, names in needed_imports:
            import_from = cst.ImportFrom(
                module=cst.Name(module_name),
                names=(
                    cst.ImportStar()
                    if names == ["*"]
                    else [cst.ImportAlias(name=cst.Name(name)) for name in names]
                ),
            )
            new_imports.append(
                cst.SimpleStatementLine(
                    body=[import_from],
                )
            )
        for imp in reversed(new_imports):
            new_module_body.insert(last_import_index + 1, imp)

        return updated_node.with_changes(body=new_module_body)

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> cst.BaseExpression:
        updated_node = self._update_urlpatterns(updated_node)

        return updated_node

    # def _ensure_imports(self, node: cst.Module) -> cst.Module:

    def _update_urlpatterns(self, node: cst.Assign) -> cst.Assign:
        app_name = f"{self.root_project_import}{self.app_name}"

        if (
            len(node.targets) == 1
            and isinstance(node.targets[0].target, cst.Name)
            and node.targets[0].target.value == "urlpatterns"
            and isinstance(node.value, cst.List)
            and not any(
                isinstance(el.value, cst.Call)
                and isinstance(el.value.func, cst.Name)
                and el.value.func.value == "path"
                and any(
                    isinstance(arg.value, cst.Call)
                    and isinstance(arg.value.func, cst.Name)
                    and arg.value.func.value == "include"
                    and (
                        (
                            isinstance(arg.value.args[0].value, cst.Tuple)
                            and isinstance(
                                arg.value.args[0].value.elements[0].value,
                                cst.SimpleString,
                            )
                            and arg.value.args[0]
                            .value.elements[0]
                            .value.evaluated_value
                            == f"{app_name}.urls"
                        )
                        or (
                            isinstance(arg.value.args[0].value, cst.SimpleString)
                            and arg.value.args[0].value.evaluated_value
                            == f"{app_name}.urls"
                        )
                    )
                    for arg in el.value.args
                )
                for el in node.value.elements
            )
        ):
            ## Add the new app to the list on a new line

            if isinstance(
                node.value.lbracket.whitespace_after, cst.ParenthesizedWhitespace
            ):
                whitespace_after = node.value.lbracket.whitespace_after
            else:
                whitespace_after = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(
                        whitespace=cst.SimpleWhitespace(
                            value="",
                        ),
                        comment=None,
                        newline=cst.Newline(
                            value=None,
                        ),
                    ),
                    empty_lines=[],
                    indent=True,
                    last_line=cst.SimpleWhitespace(
                        value="    ",
                    ),
                )
            existing_elements = list(node.value.elements)
            new_elements = []
            for elm in existing_elements:
                updated_elm = elm.with_changes(
                    comma=cst.Comma(whitespace_after=whitespace_after),
                )
                new_elements.append(updated_elm)
            added_elements = []
            if len(new_elements) == 0:
                use_comma = cst.Comma()
                quote = '"'
            else:
                use_comma = new_elements[-1].comma
                if len(new_elements) >= 2:
                    new_elements[-1] = new_elements[-1].with_changes(
                        comma=new_elements[-2].comma
                    )
                last_elm = new_elements[-1].value
                if isinstance(last_elm, cst.SimpleString):
                    quote = last_elm.quote
                else:
                    quote = '"'

                new_elements.extend(reversed(added_elements))

            new_elements.append(
                cst.Element(
                    value=cst.Call(
                        func=cst.Name("path"),
                        args=[
                            cst.Arg(
                                value=cst.SimpleString(
                                    f"{quote}{self.app_name}/{quote}"
                                ),
                            ),
                            cst.Arg(
                                value=cst.Call(
                                    func=cst.Name("include"),
                                    args=[
                                        cst.Arg(
                                            value=cst.Tuple(
                                                elements=[
                                                    cst.Element(
                                                        value=cst.SimpleString(
                                                            value=f"{quote}{app_name}.urls{quote}",
                                                        ),
                                                        comma=cst.Comma(
                                                            whitespace_after=cst.SimpleWhitespace(
                                                                " "
                                                            )
                                                        ),
                                                    ),
                                                    cst.Element(
                                                        value=cst.SimpleString(
                                                            value=f"{quote}{self.app_name}{quote}",
                                                        ),
                                                        comma=cst.MaybeSentinel.DEFAULT,
                                                    ),
                                                ]
                                            )
                                        ),
                                        cst.Arg(
                                            value=cst.SimpleString(
                                                value=f"{quote}{self.app_name}{quote}",
                                            )
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    comma=use_comma,
                ),
            )
            new_list = node.value.with_changes(elements=new_elements)
            return node.with_changes(value=new_list)
        return node
