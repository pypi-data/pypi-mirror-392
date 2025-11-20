import functools
from copy import copy
from dataclasses import dataclass
from typing import Callable, List, Optional, Union

import click
from click.exceptions import BadOptionUsage
from click.exceptions import Exit as ClickExit
from click.exceptions import NoSuchOption, UsageError

from dbt.adapters.factory import register_adapter
from dbt.artifacts.schemas.catalog import CatalogArtifact
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.cli import params as p
from dbt.cli import requires
from dbt.cli.exceptions import DbtInternalException, DbtUsageException
from dbt.cli.requires import setup_manifest
from dbt.contracts.graph.manifest import Manifest
from dbt.mp_context import get_mp_context
from dbt_common.events.base_types import EventMsg


@dataclass
class dbtRunnerResult:
    """Contains the result of an invocation of the dbtRunner"""

    success: bool

    exception: Optional[BaseException] = None
    result: Union[
        bool,  # debug
        CatalogArtifact,  # docs generate
        List[str],  # list/ls
        Manifest,  # parse
        None,  # clean, deps, init, source
        RunExecutionResult,  # build, compile, run, seed, snapshot, test, run-operation
    ] = None


# Programmatic invocation
class dbtRunner:
    def __init__(
        self,
        manifest: Optional[Manifest] = None,
        callbacks: Optional[List[Callable[[EventMsg], None]]] = None,
    ) -> None:
        self.manifest = manifest

        if callbacks is None:
            callbacks = []
        self.callbacks = callbacks

    def invoke(self, args: List[str], **kwargs) -> dbtRunnerResult:
        try:
            dbt_ctx = cli.make_context(cli.name, args.copy())
            dbt_ctx.obj = {
                "manifest": self.manifest,
                "callbacks": self.callbacks,
                "dbt_runner_command_args": args,
            }

            for key, value in kwargs.items():
                dbt_ctx.params[key] = value
                # Hack to set parameter source to custom string
                dbt_ctx.set_parameter_source(key, "kwargs")  # type: ignore

            result, success = cli.invoke(dbt_ctx)
            return dbtRunnerResult(
                result=result,
                success=success,
            )
        except requires.ResultExit as e:
            return dbtRunnerResult(
                result=e.result,
                success=False,
            )
        except requires.ExceptionExit as e:
            return dbtRunnerResult(
                exception=e.exception,
                success=False,
            )
        except (BadOptionUsage, NoSuchOption, UsageError) as e:
            return dbtRunnerResult(
                exception=DbtUsageException(e.message),
                success=False,
            )
        except ClickExit as e:
            if e.exit_code == 0:
                return dbtRunnerResult(success=True)
            return dbtRunnerResult(
                exception=DbtInternalException(f"unhandled exit code {e.exit_code}"),
                success=False,
            )
        except BaseException as e:
            return dbtRunnerResult(
                exception=e,
                success=False,
            )


# approach from https://github.com/pallets/click/issues/108#issuecomment-280489786
def global_flags(func):
    @p.cache_selected_only
    @p.debug
    @p.defer
    @p.deprecated_defer
    @p.defer_state
    @p.deprecated_favor_state
    @p.deprecated_print
    @p.deprecated_state
    @p.fail_fast
    @p.favor_state
    @p.indirect_selection
    @p.log_cache_events
    @p.log_file_max_bytes
    @p.log_format
    @p.log_format_file
    @p.log_level
    @p.log_level_file
    @p.log_path
    @p.macro_debugging
    @p.partial_parse
    @p.partial_parse_file_path
    @p.partial_parse_file_diff
    @p.populate_cache
    @p.print
    @p.printer_width
    @p.profile
    @p.quiet
    @p.record_timing_info
    @p.send_anonymous_usage_stats
    @p.single_threaded
    @p.show_all_deprecations
    @p.state
    @p.static_parser
    @p.target
    @p.target_compute
    @p.use_colors
    @p.use_colors_file
    @p.use_experimental_parser
    @p.version
    @p.version_check
    @p.warn_error
    @p.warn_error_options
    @p.write_json
    @p.use_fast_test_edges
    @p.upload_artifacts
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# dbt
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.pass_context
@global_flags
@p.show_resource_report
def cli(ctx, **kwargs):
    """An ELT tool for managing your SQL transformations and data models.
    For more documentation on these commands, visit: docs.getdbt.com
    """


# dbt build
@cli.command("build")
@click.pass_context
@global_flags
@p.empty
@p.event_time_start
@p.event_time_end
@p.exclude
@p.export_saved_queries
@p.full_refresh
@p.deprecated_include_saved_query
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.sample
@p.select
@p.selector
@p.show
@p.store_failures
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def build(ctx, **kwargs):
    """Run all seeds, models, snapshots, and tests in DAG order"""
    from dbt.task.build import BuildTask

    task = BuildTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt clean
@cli.command("clean")
@click.pass_context
@global_flags
@p.clean_project_files_only
@p.profiles_dir
@p.project_dir
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.unset_profile
@requires.project
def clean(ctx, **kwargs):
    """Delete all folders in the clean-targets list (usually the dbt_packages and target directories.)"""
    from dbt.task.clean import CleanTask

    with CleanTask(ctx.obj["flags"], ctx.obj["project"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt docs
@cli.group()
@click.pass_context
@global_flags
def docs(ctx, **kwargs):
    """Generate or serve the documentation website for your project"""


# dbt docs generate
@docs.command("generate")
@click.pass_context
@global_flags
@p.compile_docs
@p.exclude
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.empty_catalog
@p.static
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest(write=False)
def docs_generate(ctx, **kwargs):
    """Generate the documentation website for your project"""
    from dbt.task.docs.generate import GenerateTask

    task = GenerateTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt docs serve
@docs.command("serve")
@click.pass_context
@global_flags
@p.browser
@p.host
@p.port
@p.profiles_dir
@p.project_dir
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def docs_serve(ctx, **kwargs):
    """Serve the documentation website for your project"""
    from dbt.task.docs.serve import ServeTask

    task = ServeTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt compile
@cli.command("compile")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.show_output_format
@p.introspect
@p.profiles_dir
@p.project_dir
@p.empty
@p.select
@p.selector
@p.inline
@p.compile_inject_ephemeral_ctes
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def compile(ctx, **kwargs):
    """Generates executable SQL from source, model, test, and analysis files. Compiled SQL files are written to the
    target/ directory."""
    from dbt.task.compile import CompileTask

    task = CompileTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt show
@cli.command("show")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.show_output_format
@p.show_limit
@p.introspect
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.inline
@p.inline_direct
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def show(ctx, **kwargs):
    """Generates executable SQL for a named resource or inline query, runs that SQL, and returns a preview of the
    results. Does not materialize anything to the warehouse."""
    from dbt.task.show import ShowTask, ShowTaskDirect

    if ctx.obj["flags"].inline_direct:
        # Issue the inline query directly, with no templating. Does not require
        # loading the manifest.
        register_adapter(ctx.obj["runtime_config"], get_mp_context())
        task = ShowTaskDirect(
            ctx.obj["flags"],
            ctx.obj["runtime_config"],
        )
    else:
        setup_manifest(ctx)
        task = ShowTask(
            ctx.obj["flags"],
            ctx.obj["runtime_config"],
            ctx.obj["manifest"],
        )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt debug
@cli.command("debug")
@click.pass_context
@global_flags
@p.debug_connection
@p.config_dir
@p.profiles_dir_exists_false
@p.project_dir
@p.vars
@requires.postflight
@requires.preflight
def debug(ctx, **kwargs):
    """Show information on the current dbt environment and check dependencies, then test the database connection. Not to be confused with the --debug option which increases verbosity."""
    from dbt.task.debug import DebugTask

    task = DebugTask(
        ctx.obj["flags"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt deps
@cli.command("deps")
@click.pass_context
@global_flags
@p.profiles_dir_exists_false
@p.project_dir
@p.vars
@p.source
@p.lock
@p.upgrade
@p.add_package
@requires.postflight
@requires.preflight
@requires.unset_profile
@requires.project
def deps(ctx, **kwargs):
    """Install dbt packages specified.
    In the following case, a new `package-lock.yml` will be generated and the packages are installed:
    - user updated the packages.yml
    - user specify the flag --update, which means for packages that are specified as a
      range, dbt-core will try to install the newer version
    Otherwise, deps will use `package-lock.yml` as source of truth to install packages.

    There is a way to add new packages by providing an `--add-package` flag to deps command
    which will allow user to specify a package they want to add in the format of packagename@version.
    """
    from dbt.task.deps import DepsTask

    flags = ctx.obj["flags"]
    if flags.ADD_PACKAGE:
        if not flags.ADD_PACKAGE["version"] and flags.SOURCE != "local":
            raise BadOptionUsage(
                message=f"Version is required in --add-package when a package when source is {flags.SOURCE}",
                option_name="--add-package",
            )
    with DepsTask(flags, ctx.obj["project"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt init
@cli.command("init")
@click.pass_context
@global_flags
# for backwards compatibility, accept 'project_name' as an optional positional argument
@click.argument("project_name", required=False)
@p.profiles_dir_exists_false
@p.project_dir
@p.skip_profile_setup
@p.vars
@requires.postflight
@requires.preflight
def init(ctx, **kwargs):
    """Initialize a new dbt project."""
    from dbt.task.init import InitTask

    with InitTask(ctx.obj["flags"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt list
@cli.command("list")
@click.pass_context
@global_flags
@p.exclude
@p.models
@p.output
@p.output_keys
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.raw_select
@p.selector
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def list(ctx, **kwargs):
    """List the resources in your project"""
    from dbt.task.list import ListTask

    task = ListTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# Alias "list" to "ls"
ls = copy(cli.commands["list"])
ls.hidden = True
cli.add_command(ls, "ls")


# dbt parse
@cli.command("parse")
@click.pass_context
@global_flags
@p.profiles_dir
@p.project_dir
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest(write_perf_info=True)
def parse(ctx, **kwargs):
    """Parses the project and provides information on performance"""
    # manifest generation and writing happens in @requires.manifest
    return ctx.obj["manifest"], True


# dbt run
@cli.command("run")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.empty
@p.event_time_start
@p.event_time_end
@p.sample
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def run(ctx, **kwargs):
    """Compile SQL and execute against the current target database."""
    from dbt.task.run import RunTask

    task = RunTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt retry
@cli.command("retry")
@click.pass_context
@global_flags
@p.project_dir
@p.profiles_dir
@p.vars
@p.target_path
@p.threads
@p.full_refresh
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def retry(ctx, **kwargs):
    """Retry the nodes that failed in the previous run."""
    from dbt.task.retry import RetryTask

    # Retry will parse manifest inside the task after we consolidate the flags
    task = RetryTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt clone
@cli.command("clone")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
@requires.postflight
def clone(ctx, **kwargs):
    """Create clones of selected nodes based on their location in the manifest provided to --state."""
    from dbt.task.clone import CloneTask

    task = CloneTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt run operation
@cli.command("run-operation")
@click.pass_context
@global_flags
@click.argument("macro")
@p.args
@p.profiles_dir
@p.project_dir
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def run_operation(ctx, **kwargs):
    """Run the named macro with any supplied arguments."""
    from dbt.task.run_operation import RunOperationTask

    task = RunOperationTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt seed
@cli.command("seed")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.show
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def seed(ctx, **kwargs):
    """Load data from csv files into your data warehouse."""
    from dbt.task.seed import SeedTask

    task = SeedTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )
    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt snapshot
@cli.command("snapshot")
@click.pass_context
@global_flags
@p.empty
@p.exclude
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def snapshot(ctx, **kwargs):
    """Execute snapshots defined in your project"""
    from dbt.task.snapshot import SnapshotTask

    task = SnapshotTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt source
@cli.group()
@click.pass_context
@global_flags
def source(ctx, **kwargs):
    """Manage your project's sources"""


# dbt source freshness
@source.command("freshness")
@click.pass_context
@global_flags
@p.exclude
@p.output_path  # TODO: Is this ok to re-use?  We have three different output params, how much can we consolidate?
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def freshness(ctx, **kwargs):
    """check the current freshness of the project's sources"""
    from dbt.task.freshness import FreshnessTask

    task = FreshnessTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# Alias "source freshness" to "snapshot-freshness"
snapshot_freshness = copy(cli.commands["source"].commands["freshness"])  # type: ignore
snapshot_freshness.hidden = True
cli.commands["source"].add_command(snapshot_freshness, "snapshot-freshness")  # type: ignore


# dbt test
@cli.command("test")
@click.pass_context
@global_flags
@p.exclude
@p.resource_type
@p.exclude_resource_type
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.store_failures
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def test(ctx, **kwargs):
    """Runs tests on data in deployed models. Run this after `dbt run`"""
    from dbt.task.test import TestTask

    task = TestTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# DVT migrate command - migrate from .dbt/ to .dvt/
@cli.command("migrate")
@click.pass_context
@p.profiles_dir
@p.project_dir
def migrate(ctx, **kwargs):
    """Migrate configuration from .dbt/ to .dvt/ directory"""
    from pathlib import Path
    import shutil
    from dbt.flags import get_flags

    flags = get_flags()
    home = Path.home()

    old_dbt_dir = home / ".dbt"
    new_dvt_dir = home / ".dvt"

    if not old_dbt_dir.exists():
        click.echo("No .dbt/ directory found - nothing to migrate")
        return True, True

    if new_dvt_dir.exists():
        response = click.confirm(
            f".dvt/ directory already exists at {new_dvt_dir}. Overwrite files?"
        )
        if not response:
            click.echo("Migration cancelled")
            return False, False

    # Create .dvt directory
    new_dvt_dir.mkdir(parents=True, exist_ok=True)

    # Copy profiles.yml if it exists
    old_profiles = old_dbt_dir / "profiles.yml"
    new_profiles = new_dvt_dir / "profiles.yml"

    migrated_files = []

    if old_profiles.exists():
        shutil.copy2(old_profiles, new_profiles)
        migrated_files.append("profiles.yml")
        click.echo(f"✓ Copied {old_profiles} → {new_profiles}")

    # Initialize default computes.yml
    from dbt.config.compute import ComputeRegistry
    computes_file = new_dvt_dir / "computes.yml"
    if not computes_file.exists():
        # Initialize using the static method
        ComputeRegistry.initialize_default_computes(str(new_dvt_dir.parent))
        migrated_files.append("computes.yml (initialized with defaults)")
        click.echo(f"✓ Created {computes_file} with default engines")

    if migrated_files:
        click.echo("")
        click.echo(f"Migration complete! Migrated {len(migrated_files)} files:")
        for f in migrated_files:
            click.echo(f"  - {f}")
        click.echo("")
        click.echo("Your .dbt/ directory has been preserved.")
        click.echo("DVT will now use .dvt/ for all configurations.")
    else:
        click.echo("No files to migrate")

    return True, True


# DVT target (connection) management commands
@cli.group("target")
@click.pass_context
def target(ctx):
    """Manage connection targets in profiles.yml"""
    pass


@target.command("list")
@click.option("--profile", help="Profile name to list targets from")
@click.pass_context
@p.profiles_dir
def target_list(ctx, profile, profiles_dir, **kwargs):
    """List available targets in profiles.yml"""
    from dbt.config.profile import read_profile

    profiles = read_profile(profiles_dir)

    if not profiles:
        click.echo("No profiles found in profiles.yml")
        return True, True

    if profile:
        # Show targets for specific profile
        if profile not in profiles:
            click.echo(f"Profile '{profile}' not found")
            return False, False

        profile_data = profiles[profile]
        # Check if DVT format (connections) or legacy (outputs)
        connections = profile_data.get("connections", profile_data.get("outputs", {}))

        if not connections:
            click.echo(f"No targets found in profile '{profile}'")
            return True, True

        default_target = profile_data.get("default_target", profile_data.get("target", "unknown"))

        click.echo(f"Profile: {profile}")
        click.echo(f"Default target: {default_target}")
        click.echo("")
        click.echo("Available targets:")
        for target_name, target_config in connections.items():
            default_marker = " (default)" if target_name == default_target else ""
            adapter_type = target_config.get("type", "unknown")
            click.echo(f"  {target_name} ({adapter_type}){default_marker}")

    else:
        # Show all profiles
        click.echo("Available profiles:")
        click.echo("")
        for profile_name, profile_data in profiles.items():
            connections = profile_data.get("connections", profile_data.get("outputs", {}))
            target_count = len(connections)
            default_target = profile_data.get("default_target", profile_data.get("target", "unknown"))
            click.echo(f"  {profile_name}")
            click.echo(f"    Default target: {default_target}")
            click.echo(f"    Targets: {target_count}")
            click.echo("")

    return True, True


@target.command("test")
@click.argument("target_name")
@click.option("--profile", help="Profile name (defaults to project profile)")
@click.pass_context
@p.profiles_dir
@p.project_dir
def target_test(ctx, target_name, profile, profiles_dir, project_dir, **kwargs):
    """Test connection to a target"""
    click.echo(f"Testing target '{target_name}'...")
    click.echo("Note: Full connection test requires 'dvt debug' command")
    click.echo("This validates that the target exists in profiles.yml")

    from dbt.config.profile import read_profile

    profiles = read_profile(profiles_dir)

    if profile:
        if profile not in profiles:
            click.echo(f"✗ Profile '{profile}' not found")
            return False, False

        profile_data = profiles[profile]
    else:
        # Try to find target in any profile
        found = False
        for prof_name, prof_data in profiles.items():
            connections = prof_data.get("connections", prof_data.get("outputs", {}))
            if target_name in connections:
                profile_data = prof_data
                profile = prof_name
                found = True
                break

        if not found:
            click.echo(f"✗ Target '{target_name}' not found in any profile")
            return False, False

    connections = profile_data.get("connections", profile_data.get("outputs", {}))

    if target_name not in connections:
        click.echo(f"✗ Target '{target_name}' not found in profile '{profile}'")
        return False, False

    target_config = connections[target_name]
    adapter_type = target_config.get("type", "unknown")

    click.echo(f"✓ Target '{target_name}' found in profile '{profile}'")
    click.echo(f"  Adapter type: {adapter_type}")

    return True, True


# DVT compute cluster management commands
@cli.group("compute")
@click.pass_context
def compute(ctx):
    """Manage compute engines for DVT federated execution"""
    pass


@compute.command("add")
@click.argument("name")
@click.option("--type", "cluster_type", required=True, help="Engine type (duckdb or spark)")
@click.option("--master", help="Spark master URL (required for Spark)")
@click.option("--config", "config_str", help="Additional config as key=value pairs (comma-separated)")
@click.option("--description", help="Engine description")
@click.option("--replace", is_flag=True, help="Replace existing engine with same name")
@click.pass_context
@p.project_dir
def compute_add(ctx, name, cluster_type, master, config_str, description, replace, project_dir, **kwargs):
    """Add a compute engine to .dvt/computes.yml"""
    from dbt.config.compute import ComputeRegistry

    registry = ComputeRegistry(project_dir)

    # Build config dict
    config = {}
    if master:
        config["master"] = master

    if config_str:
        for pair in config_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                config[key.strip()] = value.strip()

    # Validate Spark config
    if cluster_type == "spark" and "master" not in config:
        raise DbtUsageException("Spark engines require --master option")

    # Register cluster
    registry.register(
        name=name,
        cluster_type=cluster_type,
        config=config,
        description=description,
        replace=replace
    )

    click.echo(f"Added compute engine '{name}' (type: {cluster_type}) to .dvt/computes.yml")
    return True, True


@compute.command("list")
@click.pass_context
@p.project_dir
def compute_list(ctx, project_dir, **kwargs):
    """List compute engines from .dvt/computes.yml"""
    from dbt.config.compute import ComputeRegistry

    registry = ComputeRegistry(project_dir)
    clusters = registry.list()
    target_compute = registry.target_compute

    if not clusters:
        click.echo("No compute engines configured")
        return True, True

    click.echo(f"Default target_compute: {target_compute}")
    click.echo("")
    click.echo("Available compute engines:")
    click.echo("")
    for cluster in clusters:
        default_marker = " (default)" if cluster.name == target_compute else ""
        click.echo(f"  {cluster.name} ({cluster.type}){default_marker}")
        if cluster.description:
            click.echo(f"    Description: {cluster.description}")
        click.echo(f"    Config: {cluster.config}")
        click.echo("")

    return True, True


@compute.command("test")
@click.argument("name")
@click.pass_context
@p.project_dir
def compute_test(ctx, name, project_dir, **kwargs):
    """Test connection to a compute engine"""
    from dbt.config.compute import ComputeRegistry

    registry = ComputeRegistry(project_dir)
    cluster = registry.get(name)

    if not cluster:
        click.echo(f"Error: Compute engine '{name}' not found")
        return False, False

    click.echo(f"Testing compute engine '{name}' ({cluster.type})...")

    # Basic validation
    if cluster.type == "duckdb":
        click.echo("✓ DuckDB engine configured (embedded, always available)")
        click.echo(f"  Config: {cluster.config}")
        return True, True
    elif cluster.type == "spark":
        if "master" in cluster.config:
            click.echo(f"✓ Spark master: {cluster.config['master']}")
            click.echo("  Note: Full Spark connection test requires running 'dvt run' with this engine")
            return True, True
        else:
            click.echo("✗ Spark engine missing 'master' configuration")
            return False, False
    else:
        click.echo(f"✗ Unknown engine type: {cluster.type}")
        return False, False


@compute.command("remove")
@click.argument("name")
@click.pass_context
@p.project_dir
def compute_remove(ctx, name, project_dir, **kwargs):
    """Remove a compute engine from .dvt/computes.yml"""
    from dbt.config.compute import ComputeRegistry

    registry = ComputeRegistry(project_dir)
    registry.remove(name)

    click.echo(f"Removed compute engine '{name}' from .dvt/computes.yml")
    return True, True


# Support running as a module
if __name__ == "__main__":
    cli()
