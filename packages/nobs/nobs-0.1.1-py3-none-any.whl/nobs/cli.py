import functools
from pathlib import Path
import click
import logging
import asyncio

from docker import DockerClient
from pydantic import BaseModel, ValidationError

from nobs.models import Job, NetworkApp, Project, Subscriber, VeloxClient, VeloxServer
from nobs.runners import default_runner


logger = logging.getLogger(__name__)

def async_(func):  # noqa
    """Decorator to run async functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    from dotenv import load_dotenv

    logging.basicConfig(level=logging.INFO)
    logger.info(load_dotenv(".env"))
    pass


def project_at(ref: str) -> Project:
    import importlib

    module_name, attr_name = ref.split(":")

    module = importlib.import_module(module_name)
    project = getattr(module, attr_name)

    assert isinstance(project, Project), f"Expected a project got '{type(project)}'"

    return project


@cli.command()
@click.option("--ref")
@click.option("--server")
@click.option("--env", default="test")
@async_
async def deploy(ref: str | None, server: str | None, env: str) -> None:
    import sys

    click.echo("Deploying project")

    path = Path.cwd().as_posix()

    if ref is None:
        ref = "project:project"

    if server:
        config = VeloxServer(velox_api=server) # type: ignore
    else:
        config = VeloxServer() # type: ignore

    if path not in sys.path:
        sys.path.append(path)


    project = project_at(ref)

    client = VeloxClient(settings=config)
    await client.update(project, env=env)


@cli.command()
@click.argument("name")
@click.option("--ref")
@click.option("--platform")
@async_
async def run(name: str, ref: str | None, platform: str | None) -> None:
    import sys
    import inspect

    if ref is None:
        ref = "project:project"

    path = Path.cwd().as_posix()
    if path not in sys.path:
        sys.path.append(path)

    if platform is None:
        platform = "linux/amd64"

    project = project_at(ref)

    if name not in project.components:
        raise ValueError(f"Unable to find '{name}'")

    comp = project.components[name]

    logger.info(comp)

    if isinstance(comp, NetworkApp):
        command = comp.command
    elif isinstance(comp, Job):
        from dotenv import load_dotenv

        load_dotenv()

        if inspect.iscoroutinefunction(comp.main_function):
            await comp.main_function(comp.arguments)
        else:
            comp.main_function(comp.arguments)
        return
    elif isinstance(comp, Subscriber):
        return
    else:
        command = comp.network_app(Path.cwd()).command

    logger.info(f"Running command {command} in docker file {project.docker_image}")

    if project.docker_image:
        command = ["docker", "run", f"--platform={platform}", project.docker_image, *command]

    _ = default_runner(command)




@cli.command()
@click.option("--project-name")
@click.option("--job-id")
@click.option("--file-ref")
@click.option("--args")
@async_
async def run_job(project_name: str, job_id: str, file_ref: str, args: str) -> None:
    import importlib
    import inspect

    click.echo(f"Running ref: {file_ref}")

    try:
        from logging_loki import LokiHandler # type: ignore

        config = LokiLoggerConfig() # type: ignore

        handler = LokiHandler(
            url=config.loki_push_endpoint,
            auth=(config.loki_user, config.loki_token),
            tags={"job_function": file_ref},
            version="1"
        )

        logging.basicConfig(level=logging.INFO)
        logging.getLogger("").addHandler(handler)
        logger.info("Managed to setup Loki logger")
    except Exception as e:
        print(f"Unable to setup Loki logger for '{file_ref}' due to error: {e}")

    logger.info(f"Running function at '{file_ref}'")
    file, function_name = file_ref.split(":")

    function_module = importlib.import_module(file)
    function = getattr(function_module, function_name)

    assert callable(function)
    sign = inspect.signature(function)   
    params = sign.parameters
    if len(params) == 0:
        if inspect.iscoroutinefunction(function):
            asyncio.run(function())
        else:
            function()
        return

    assert len(params) == 1
    _, param = list(params.items())[0]

    arg_type = param.annotation
    assert not isinstance(arg_type, str), f"Make sure to not use string annotations for {arg_type}"
    assert issubclass(arg_type, BaseModel), f"Expected a subclass of BaseModel got {arg_type}"

    if args:
        encoded_args = arg_type.model_validate_json(args.strip("'"))
    else:
        encoded_args = arg_type()

    try:
        if inspect.iscoroutinefunction(function):
            await function(encoded_args)
        else:
            function(encoded_args)
    except Exception as e:
        logger.exception(e)

        client = VeloxClient()
        await client.notify_about_failure(project_name, job_id=job_id, exception=e)

        raise e




@cli.command()
@click.argument("name")
@async_
async def process_queue(name: str) -> None:
    from nobs.secrets import SqsConfig
    from nobs.models import QueueMessage
    from nobs.queue import QueueBroker, SqsQueueBroker

    broker: QueueBroker = SqsQueueBroker(
        config=SqsConfig() # type: ignore
    )
    queue = broker.with_name(name)

    messages = await queue.receive()
    logger.info(f"Loaded '{len(messages)}' messages from queue")

    while messages:
        message = messages[0]

        try:
            content = QueueMessage.model_validate_json(message.body)
            await content.run()
            await queue.delete(message)
        except Exception as e:
            logger.exception(e)

        if len(messages) > 1:
            messages = messages[1:]
        else:
            messages = await queue.receive()
            logger.info(f"Loaded '{len(messages)}' messages from queue")

    logger.info("No more messages to process. Stopping the worker.")


@cli.command()
@click.argument("name")
@async_
async def subscriber(name: str, ref: str | None = None) -> None:
    import inspect
    import nats
    import sys

    if ref is None:
        ref = "project:project"

    path = Path.cwd().as_posix()
    if path not in sys.path:
        sys.path.append(path)

    project = project_at(ref)

    sub = project.components[name]
    assert isinstance(sub, Subscriber)

    sign = inspect.signature(sub.method)   
    params = sign.parameters

    assert len(params) == 1
    _, param = list(params.items())[0]

    arg_type = param.annotation
    assert not isinstance(arg_type, str), f"Make sure to not use string annotations for {arg_type}"
    assert issubclass(arg_type, BaseModel), f"Expected a subclass of BaseModel got {arg_type}"

    con = await nats.connect("nats://nats:4222")
    subscriber = await con.subscribe(sub.subject)

    while True:
        try:
            message = await subscriber.next_msg()
        except TimeoutError:
            await asyncio.sleep(1)
            continue

        try:
            content = arg_type.model_validate_json(message.data)
            sub.method(content)
        except ValidationError as e:
            logger.exception(e)
            logger.error("Unable to decode message")
        except Exception as e:
            logger.exception(e)


@cli.command()
@async_
async def up(ref: str | None = None) -> None:
    from nobs.docker import compose
    from pathlib import Path 
    import sys

    if ref is None:
        ref = "project:project"

    current_dir = Path.cwd()
    if current_dir.as_posix() not in sys.path:
        sys.path.append(current_dir.as_posix())

    project = project_at(ref)

    if (current_dir / project.name).is_dir():
        src_dir = current_dir / project.name
    else:
        src_dir = current_dir / "src"


    logger.info(f"Updating source code from {src_dir.as_posix()}")

    compose(
        project, 
        base_image=f"{project.name}:latest",
        src_dir=src_dir
    )



def default_docker_image(uv_image: str, source_code_dir: str) -> str:
    return f"""
FROM {uv_image} AS builder

WORKDIR /app

ADD uv.lock pyproject.toml /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-install-project

ADD {source_code_dir} /app/{source_code_dir}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM {uv_image}

COPY --from=builder --chown=app:app /app/.venv /app/.venv

WORKDIR /app

ADD {source_code_dir} /app/{source_code_dir}

ENV PATH="/app/.venv/bin:$PATH"
"""


@cli.command()
@click.option("--context")
@async_
async def build_image(ref: str | None = None, context: str | None = None) -> None:
    from pathlib import Path 
    import sys

    if ref is None:
        ref = "project:project"

    path = Path.cwd().as_posix()
    if path not in sys.path:
        sys.path.append(path)

    project = project_at(ref)

    if project.docker_image is not None:
        click.echo("Found docker image definition so will skip build.")
        return 

    pyproject_path = Path("pyproject.toml")
    docker_file = Path("Dockerfile")

    if not pyproject_path.is_file():
        raise ValueError("Expected a pyproject.toml file using uv.")


    should_delete_dockerfile = False


    if not docker_file.is_file():
        source_code_dir_name = project.name.replace("-", "_").replace("/", "")
        source_code_dir = Path(source_code_dir_name)
        uv_image = "ghcr.io/astral-sh/uv:python3.13-bookworm-slim"

        if source_code_dir.is_dir():
            raise ValueError(f"Expected to find source code at '{source_code_dir_name}', but found nothing.")

        docker_file.write_text(default_docker_image(uv_image, source_code_dir_name))
        should_delete_dockerfile = True


    platform = "linux/amd64"
    reg_url = f"{project.name}:latest"

    click.echo(f"Creating an image tagged {reg_url}")


    build_dir = Path.cwd()

    if context:
        context_path = (build_dir / context).resolve().as_posix()
        click.echo(f"Using context {context_path} with dockerfile {docker_file.resolve().as_posix()}")
        default_runner([
            "docker", "build", context_path, "-t", reg_url, "-f", docker_file.resolve().as_posix(), "--platform", platform
        ])
    else:
        default_runner([
            "docker", "build", ".", "-t", reg_url, "-f", docker_file.resolve().as_posix(), "--platform", platform
        ])

    if should_delete_dockerfile:
        docker_file.unlink(True)


if __name__ == "__main__":
    cli()
