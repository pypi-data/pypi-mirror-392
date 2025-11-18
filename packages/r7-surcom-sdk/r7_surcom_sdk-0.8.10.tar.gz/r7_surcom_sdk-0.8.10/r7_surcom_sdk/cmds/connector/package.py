import logging
import os
import shutil

import yaml

from r7_surcom_sdk.lib import (ExtLibraryAPI, SurcomSDKException, constants,
                               docker_helpers, sdk_helpers, sdk_config)
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class PackageCommand(SurcomSDKSubCommand):
    """
    [help]
    Package a connector for submission.
    ---

    [description]
    Creates a ZIP package of your connector that you can use to install
on the {PLATFORM_NAME}.

The package will be saved in the connector `build` directory.

If you specify the `--orchestrator` flag, a plugin image will also be built
for use with the Orchestrator. The plugin image will be saved as a `.tar` file
in the `build` directory which you can copy to your Orchestrator server using SCP or similar.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -c <path_connector>
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_PACKAGE

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)
        self.cmd_parser.add_argument(*Args.dir_output.flag, **Args.dir_output.kwargs)
        self.cmd_parser.add_argument(*Args.keep_build_files.flag, **Args.keep_build_files.kwargs)
        self.cmd_parser.add_argument(Args.build_number.flag, **Args.build_number.kwargs)
        self.cmd_parser.add_argument(Args.skip_validate.flag, **Args.skip_validate.kwargs)
        self.cmd_parser.add_argument(Args.orchestrator.flag, **Args.orchestrator.kwargs)
        self.cmd_parser.add_argument(Args.no_cache.flag, **Args.no_cache.kwargs)

    def _render_manifest_yaml(
        self,
        conn_spec: dict,
        path_md_file: str
    ) -> sdk_helpers.RenderedConnectorTemplate:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :param path_md_file: path to the markdown file
        :type path_md_file: str
        :return: a RenderedConnectorTemplate of package/manifest.yaml template
        :rtype: RenderedConnectorTemplate
        """

        # Get the docs from the markdown file
        md = sdk_helpers.parse_docs_from_markdown_file(path_docs_file=path_md_file)

        # NOTE: a connector developer only needs to provide
        # the `current_changes` in the connector.spec.yaml file

        # Generate the current changelog entry
        changelog = [sdk_helpers.generate_changelog_entry(
            version=conn_spec.get("version"),
            changes=conn_spec.get("current_changes", [])
        )]

        # TODO: have way to get the older changes from the connector.spec.yaml file
        # If the connector.spec.yaml file has older changes, use them
        # to overwrite what is in the Extensions Library
        older_changes = []

        # Create an instance of the Extensions Library API
        el_client = ExtLibraryAPI()

        if el_client.is_enabled():

            LOG.debug("Using the Extensions Library API to get the connector version history")

            # If its enabled, get the version history
            version_history = el_client.get_connector_version_history(connector_id=conn_spec.get("id"))

            # Here we convert the version history into our noetic changelog format
            for v in version_history:
                older_changes.append(
                    sdk_helpers.generate_changelog_entry(
                        version=v.get("version", None),
                        changes=[v.get("changes")] if v.get("changes") else [],
                        date=v.get("date")
                    )
                )

        changelog.extend(older_changes)

        template_data = {
            "noetic_builtins_version": constants.NOETIC_BUILTINS_VERSION,
            "changelog": changelog,
        }

        template_data.update(conn_spec)

        template_data["environment_name"] = constants.RUNTIME_MAP.get(conn_spec.get("runtime"))

        template_data = template_data | md

        # NOTE: here we do not want to escape the jinja template
        # because we want to keep the markdown formatting
        return sdk_helpers.render_jinja_template(
            template=constants.MANIFEST_YAML,
            templates_path=constants.TEMPLATE_PATH_PACKAGE,
            data=template_data,
            autoescape=False
        )

    def _render_action_files(
        self,
        actions: dict,
        imports: list[dict],
        plugin_id: str,
    ) -> dict[sdk_helpers.RenderedConnectorTemplate]:

        rtn_dict = {}

        for action_name, action in actions.items():
            # Render __init__.py
            init_py = sdk_helpers.render_jinja_template(
                template=constants.TEMPLATE_INIT_PY,
                templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_ACTION}",
                data={"action_name": action_name}
            )

            # Render schema.py
            action["input_schema"] = sdk_helpers.plugin_build_schema(action.get("input", {}))
            action["output_schema"] = sdk_helpers.plugin_build_schema(action.get("output", {}))

            schema_py = sdk_helpers.render_jinja_template(
                template=constants.FILENAME_SCHEMA_PY,
                templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_ACTION}",
                autoescape=False,
                data={
                    "base_module": constants.INSIGHT_CONNECT_MODULE,
                    "action_name": action_name,
                    "action": action,
                }
            )

            # Render action.py
            action_template_name = constants.TEMPLATE_ACTION_IMPORT_FN_PY \
                if action.get("action_type") == "import" else constants.TEMPLATE_ACTION_LEGACY_FN_PY

            fn_import = [i for i in imports if i.get("name") == action_name]

            if fn_import:
                fn_import = fn_import[0]
                # TODO: here we assume the function is in a functions dir. We need
                # to handle other cases (legacy connectors)
                action_import = f"from {plugin_id}.util.functions.{fn_import.get('module')} "
                action_import += f"import {fn_import.get('name')}"
            else:
                action_import = None

            action_py = sdk_helpers.render_jinja_template(
                template=action_template_name,
                templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_ACTION}",
                data={
                    "base_module": constants.INSIGHT_CONNECT_MODULE,
                    "action_name": action_name,
                    "action_import": action_import,
                }
            )

            rtn_dict[action_name] = {
                "init_py": init_py,
                "schema_py": schema_py,
                "action_py": action_py
            }

        return rtn_dict

    def _package_zip(
        self,
        path_connector_package: str,
        path_connector: str,
        path_docs_dir: str,
        path_generated_zip: str,
        conn_spec: dict,

    ) -> dict:

        manifest_yaml = self._render_manifest_yaml(
            conn_spec=conn_spec,
            path_md_file=os.path.join(path_docs_dir, constants.FILENAME_INSTRUCTIONS)
        )

        main_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_MAIN_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
        )

        requirements_txt = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_REQ_TXT,
            templates_path=constants.TEMPLATE_PATH_PACKAGE,
            data=conn_spec
        )

        # Write manifest.yaml
        sdk_helpers.write_file(
            path=os.path.join(path_connector_package, constants.MANIFEST_YAML),
            contents=manifest_yaml.rendered_template
        )

        #  Copy any screenshots if they exist
        if os.path.exists(path_docs_dir):
            sdk_helpers.copy_files_in_dir(
                path_src_dir=path_docs_dir,
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_DOCS),
                file_exts=[".png"],
            )

        # Write requirements.txt
        sdk_helpers.write_file(
            path=os.path.join(path_connector_package, constants.TEMPLATE_REQ_TXT),
            contents=requirements_txt.rendered_template
        )

        # Copy icon.svg
        shutil.copy(
            src=os.path.join(path_connector, constants.FILENAME_ICON),
            dst=os.path.join(path_connector_package, constants.FILENAME_ICON)
        )

        # Copy types/
        sdk_helpers.copy_files_in_dir(
            path_src_dir=os.path.join(path_connector, constants.DIR_NAME_TYPES),
            path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_TYPES),
            file_exts=[".yaml"],
        )

        # Copy functions/
        sdk_helpers.copy_files_in_dir(
            path_src_dir=os.path.join(path_connector, constants.DIR_NAME_FNS),
            path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_FNS),
            file_exts=[".py"],
        )

        # Write __main__.py to functions/ dir
        sdk_helpers.write_file(
            path=os.path.join(path_connector_package, constants.DIR_NAME_FNS, constants.TEMPLATE_MAIN_PY),
            contents=main_py.rendered_template
        )

        # If a sample_data directory exists, copy it
        path_sample_data = os.path.join(path_connector, constants.DIR_NAME_SAMPLE_DATA)
        if os.path.exists(path_sample_data):
            sdk_helpers.copy_files_in_dir(
                path_src_dir=path_sample_data,
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_SAMPLE_DATA),
                file_exts=[".json"]
            )

        # If a data directory exists, copy it
        path_data = os.path.join(path_connector, constants.DIR_NAME_DATA)
        if os.path.exists(path_data):
            sdk_helpers.copy_files_in_dir(
                path_src_dir=path_data,
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_DATA),
                file_exts=[".json"]
            )

        # If a sample_data directory exists, copy it
        path_sample_data = os.path.join(path_connector, constants.DIR_NAME_SAMPLE_DATA)
        if os.path.exists(path_sample_data):
            sdk_helpers.copy_files_in_dir(
                path_src_dir=path_sample_data,
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_SAMPLE_DATA),
                file_exts=[".json"]
            )

        # If a refdocs directory exists, copy it
        path_refdocs = os.path.join(path_connector, constants.DIR_NAME_REFDOCS)
        if os.path.exists(path_refdocs):
            sdk_helpers.copy_files_in_dir(
                path_src_dir=path_refdocs,
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_REFDOCS),
                file_exts=[".json", ".yaml", ".yml"]
            )

        # If an old .zip exists, force remove it to avoid caching issues
        if os.path.exists(f"{path_generated_zip}.zip"):
            os.remove(f"{path_generated_zip}.zip")

        # Make unsigned .zip
        shutil.make_archive(
            base_name=path_generated_zip,
            format="zip",
            root_dir=path_connector_package
        )

        return yaml.safe_load(manifest_yaml.rendered_template)

    def _package_plugin(
        self,
        args,
        conn_spec: dict,
        connector_manifest: dict,
        path_plugin_package: str,
        path_connector: str,
        path_build_dir: str,
    ) -> str:

        plugin_id = sdk_helpers.get_plugin_id_from_conn_spec(conn_spec=conn_spec)
        path_plugin_src = os.path.join(path_plugin_package, plugin_id)
        path_plugin_src_actions = os.path.join(path_plugin_src, "actions")
        path_plugin_src_connection = os.path.join(path_plugin_src, "connection")
        path_plugin_src_util = os.path.join(path_plugin_src, "util")

        actions = sdk_helpers.plugin_get_actions(manifest=connector_manifest)

        imports = sdk_helpers.get_imports_from_file(
            path_to_file=os.path.join(path_connector, constants.DIR_NAME_FNS, constants.TEMPLATE_INIT_PY)
        )

        # NOTE: we add the plugin_id to the conn_spec
        conn_spec["plugin_id"] = plugin_id

        # Render the files
        requirements_txt = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_REQ_TXT,
            templates_path=constants.TEMPLATE_PATH_PLUGIN,
            data=conn_spec
        )

        pyproject_toml = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_PYPROJECT_TOML,
            templates_path=constants.TEMPLATE_PATH_PLUGIN,
            data=conn_spec
        )

        entrypoint_sh = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_ENTRYPOINT_SH,
            templates_path=constants.TEMPLATE_PATH_PLUGIN,
            data=conn_spec
        )

        # Check if we should use Artifactory for the r7-surcom-api
        use_artifactory = sdk_config.get_config(
            option=constants.CONFIG_NAME_USE_ARTIFACTORY,
            option_type="bool",
            default=False
        )

        if use_artifactory:
            sdk_helpers.print_log_msg(
                f"'{constants.CONFIG_NAME_USE_ARTIFACTORY}' is True. We will use Artifactory "
                "to install the r7-surcom-api",
                log_level=logging.WARNING
            )

        dockerfile = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_DOCKERFILE,
            templates_path=constants.TEMPLATE_PATH_PLUGIN,
            data={
                "use_artifactory": use_artifactory
            }
        )

        main_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_MAIN_PY,
            templates_path=constants.TEMPLATE_PATH_PLUGIN_SRC,
            data={
                "conn_spec": conn_spec,
                "action_names": actions.keys(),
                "base_module": constants.INSIGHT_CONNECT_MODULE
            }
        )

        icon_plugin_wrapper = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_PLUGIN_WRAPPER,
            templates_path=constants.TEMPLATE_PATH_PLUGIN_UTIL,
        )

        connection_init = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_INIT_PY,
            templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_CONNECTION}"
        )

        connection_py = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_CONNECTION_PY,
            templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_CONNECTION}",
            data={
                "base_module": constants.INSIGHT_CONNECT_MODULE
            }
        )

        connection_schema_py = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_SCHEMA_PY,
            templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_CONNECTION}",
            data={
                "base_module": constants.INSIGHT_CONNECT_MODULE
            }
        )

        actions_init_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_INIT_PY,
            templates_path=f"{constants.TEMPLATE_PATH_PLUGIN_ACTIONS}",
            data={"action_names": actions.keys()}
        )

        action_files = self._render_action_files(
            actions=actions,
            imports=imports,
            plugin_id=plugin_id
        )

        # Write plugin/requirements.txt
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_package, constants.TEMPLATE_REQ_TXT),
            contents=requirements_txt.rendered_template
        )

        # Write plugin/pyproject.toml
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_package, constants.TEMPLATE_PYPROJECT_TOML),
            contents=pyproject_toml.rendered_template
        )

        # Write plugin/entrypoint.sh
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_package, constants.FILENAME_ENTRYPOINT_SH),
            contents=entrypoint_sh.rendered_template
        )

        # Write plugin/Dockerfile
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_package, constants.FILENAME_DOCKERFILE),
            contents=dockerfile.rendered_template
        )

        # Write plugin/src/__main__.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src, constants.TEMPLATE_MAIN_PY),
            contents=main_py.rendered_template
        )

        # Write plugin/src/__init__.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src, constants.TEMPLATE_INIT_PY),
            contents=""
        )

        # Copy types/ to plugin/src/types
        sdk_helpers.copy_files_in_dir(
            path_src_dir=os.path.join(path_connector, constants.DIR_NAME_TYPES),
            path_dst_dir=os.path.join(path_plugin_src, constants.DIR_NAME_TYPES),
            file_exts=[".yaml"],
        )

        # Write plugin/src/util/__init__.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_util, constants.TEMPLATE_INIT_PY),
            contents=""
        )

        # Write plugin/src/util/icon_plugin_wrapper.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_util, constants.FILENAME_PLUGIN_WRAPPER),
            contents=icon_plugin_wrapper.rendered_template
        )

        # Copy functions/ to plugin/src/util/functions
        sdk_helpers.copy_files_in_dir(
            path_src_dir=os.path.join(path_connector, constants.DIR_NAME_FNS),
            path_dst_dir=os.path.join(path_plugin_src_util, constants.DIR_NAME_FNS),
            file_exts=[".py"],
        )

        # Write plugin/src/connection/__init__.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_connection, constants.TEMPLATE_INIT_PY),
            contents=connection_init.rendered_template
        )

        # Write plugin/src/connection/connection.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_connection, constants.FILENAME_CONNECTION_PY),
            contents=connection_py.rendered_template
        )

        # Write plugin/src/connection/schema.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_connection, constants.FILENAME_SCHEMA_PY),
            contents=connection_schema_py.rendered_template
        )

        # Write plugin/src/actions/__init__.py
        sdk_helpers.write_file(
            path=os.path.join(path_plugin_src_actions, constants.TEMPLATE_INIT_PY),
            contents=actions_init_py.rendered_template
        )

        # For each action write its files
        for action_name, action_file in action_files.items():

            # Write plugin/src/actions/<action_name>/__init__.py
            sdk_helpers.write_file(
                path=os.path.join(path_plugin_src_actions, action_name, constants.TEMPLATE_INIT_PY),
                contents=action_file.get("init_py").rendered_template
            )

            # Write plugin/src/actions/<action_name>/schema.py
            sdk_helpers.write_file(
                path=os.path.join(path_plugin_src_actions, action_name, constants.FILENAME_SCHEMA_PY),
                contents=action_file.get("schema_py").rendered_template
            )
            # Write plugin/src/actions/<action_name>/action.py
            sdk_helpers.write_file(
                path=os.path.join(path_plugin_src_actions, action_name, constants.FILENAME_ACTION_PY),
                contents=action_file.get("action_py").rendered_template
            )

        docker_tag = f"rapid7/{plugin_id}:{conn_spec.get('version')}"

        # Remove any existing containers and images
        docker_helpers.delete_containers(docker_tag=docker_tag)
        docker_helpers.delete_image(docker_tag=docker_tag)

        cli_args = ["docker", "build", "-t", docker_tag, path_plugin_package]

        if args.verbose:
            cli_args.append("--progress=plain")

        if args.no_cache:
            cli_args.append("--no-cache")

        sdk_helpers.print_log_msg(f"Building a new plugin image '{docker_tag}'")

        sdk_helpers.run_subprocess(cli_args, capture_output=False)

        docker_tar = f"{plugin_id}-v{conn_spec.get('version')}.tar"
        path_docker_tar = os.path.join(path_build_dir, docker_tar)

        cli_args = ["docker", "save", "-o", path_docker_tar, docker_tag]

        sdk_helpers.print_log_msg("Saving plugin image...")

        sdk_helpers.run_subprocess(cli_args, capture_output=False)

        return docker_tar

    def run(self, args, cmd_validate=None):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Packaging the connector at '{args.path_connector}'", divider=True)

        if hasattr(args, "skip_validate") and not args.skip_validate and cmd_validate:

            sdk_helpers.print_log_msg("Before packaging, running validations...", log_level=logging.WARNING)
            args.is_ci = None
            args.multiple_connectors = None
            args.path_all_connectors_dir = None
            args.skip_validations = []
            cmd_validate.run(args=args)

        path_connector = os.path.abspath(args.path_connector)

        # Check if the connector directory is valid. Raise an exception if it is not.
        sdk_helpers.is_connector_directory(path=path_connector)

        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)
        path_docs_dir = os.path.join(path_connector, constants.DIR_NAME_DOCS)
        path_build_dir = os.path.join(path_connector, constants.DIR_NAME_BUILD)
        path_output = sdk_helpers.get_output_dir(dir_output=args.dir_output, default=path_build_dir)
        path_connector_package = os.path.join(path_output, constants.DIR_NAME_SURCOM_CONNECTOR)
        path_plugin_package = os.path.join(path_output, constants.DIR_NAME_SURCOM_PLUGIN)

        # If the build/surcom_connector dir already exists, remove it
        if os.path.exists(path_connector_package):
            # NOTE: this is relatively safe to do because it will only
            # remove the directory if it is called constants.DIR_NAME_SURCOM_CONNECTOR
            shutil.rmtree(path_connector_package)

        # If the build/surcom_plugin dir already exists, remove it
        if os.path.exists(path_plugin_package):
            # NOTE: this is relatively safe to do because it will only
            # remove the directory if it is called constants.DIR_NAME_SURCOM_PLUGIN
            shutil.rmtree(path_plugin_package)

        # Because we call the command from other subcommands, there
        # is a chance that this may not be set
        keep_build_files = getattr(args, "keep_build_files", False)

        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)

        # If a build number was provided, replace it in the conn_spec
        if hasattr(args, "build_number") and args.build_number:
            conn_spec = sdk_helpers.replace_build_number(conn_spec=conn_spec, build_number=args.build_number)

        zip_file_name = f"{conn_spec.get('id').replace('.', '-')}-v{conn_spec.get('version')}"
        path_generated_zip = os.path.join(path_output, zip_file_name)

        try:

            sdk_helpers.print_log_msg("Creating the Connector .zip file...", log_level=logging.WARNING)

            connector_manifest = self._package_zip(
                path_connector_package=path_connector_package,
                path_connector=path_connector,
                path_docs_dir=path_docs_dir,
                path_generated_zip=path_generated_zip,
                conn_spec=conn_spec
            )

            sdk_helpers.print_log_msg(f"A Connector package was created at '{path_generated_zip}.zip'")

            if hasattr(args, "orchestrator") and args.orchestrator:

                sdk_helpers.print_log_msg("Generating the Plugin files for Orchestrator...", log_level=logging.WARNING)

                docker_tar = self._package_plugin(
                    args=args,
                    conn_spec=conn_spec,
                    connector_manifest=connector_manifest,
                    path_plugin_package=path_plugin_package,
                    path_connector=path_connector,
                    path_build_dir=path_build_dir
                )

                sdk_helpers.print_log_msg(f"The plugin image '{docker_tar}' have been saved in the build directory. "
                                          f"You can copy it to your Orchestrator using SCP or similar.")

        except Exception as e:

            # There was a problem, remove the .zip if created
            if os.path.exists(f"{path_generated_zip}.zip") and not keep_build_files:
                # NOTE: this is relatively safe to do because it will only
                # remove the directory if it is called constants.DIR_NAME_SURCOM_CONNECTOR
                shutil.rmtree(f"{path_generated_zip}.zip")

            raise e

        finally:
            # Remove the build files, unless specified otherwise

            # Remove the Connector files
            if os.path.exists(path_connector_package) and not keep_build_files:
                shutil.rmtree(path_connector_package)

            # Remove the Plugin files
            if os.path.exists(path_plugin_package) and not keep_build_files:
                shutil.rmtree(path_plugin_package)

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
