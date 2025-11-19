from threading import Thread
from contextlib import suppress
from dataclasses import dataclass
import logging
from pathlib import Path
from time import sleep
from docker import DockerClient
from nobs.models import CompiledProject, Project, Job, NetworkApp, NetworkAppable, Subscriber

logger = logging.getLogger(__name__)

@dataclass
class Container:
    name: str
    image: str
    restart: str
    environments: dict[str, str]
    volumes: list[str]
    ports: list[str]

    additional_secrets: dict[str, str]


def needed_containers(project: CompiledProject) -> list[Container]:
    containers = []

    needed_res = {
        val.name: val.data_type
        for val in project.shared_secrets
        if val.data_type in ["PostgresDsn", "RedisDsn"]
    }

    current_dir = Path.cwd().absolute()
    data_dir = current_dir / ".data"

    for dtype in set(needed_res.values()):
        if dtype == "PostgresDsn":

            protocol = "postgresql"

            with suppress(ImportError):
                import psycopg
                protocol = "postgresql+psycopg"

            with suppress(ImportError):
                import psycopg2
                protocol = "postgresql+psycopg2"

            with suppress(ImportError):
                import asyncpg
                protocol = "postgresql+asyncpg"


            containers.append(
                Container(
                    name="psql",
                    image="postgres:15",
                    restart="always",
                    environments={
                        "POSTGRES_USER": "user",
                        "POSTGRES_PASSWORD": "pass",
                        "POSTGRES_DB": "db"
                    },
                    volumes=[f"{data_dir.as_posix()}/postgresql:/var/lib/postgresql/data"],
                    ports={"5432/tcp": 5432},

                    additional_secrets={
                        name: f"{protocol}://user:pass@psql:5432/db"
                        for name, dtype in needed_res.items()
                        if dtype == "PostgresDsn"
                    }
                )
            )

        if dtype == "RedisDsn":
            containers.append(
                Container(
                    name="redis",
                    image="redis:7.2.11",
                    restart="always",
                    environments={},
                    volumes=[
                        f"{data_dir.as_posix()}/valkey:/data"
                    ],
                    ports={"6379/tcp": 6379},

                    additional_secrets={
                        name: "redis://redis:6379"
                        for name, dtype in needed_res.items()
                        if dtype == "RedisDsn"
                    }
                )
            )


    if project.subscribers:
        nats_url = "nats://nats:4222"
        secrets = {
            val.name: "nats://nats:4222"
            for val in project.subscribers[0].secrets or []
            if val.data_type == "NatsDns"
        }

        if not secrets:
            secrets["NATS_URL"] = nats_url

        containers.append(
            Container(
                name="nats",
                image="nats:2.12.2-alpine",
                restart="always",
                environments={},
                volumes=[],
                ports={"4222/tcp": 4222},
                additional_secrets=secrets
            )
        )

    return containers


def stream_container(container_id: str) -> None:
    client = DockerClient.from_env()
    cont = client.containers.get(container_id)
    
    for log in cont.logs(stream=True, follow=True):
        print(f"[{cont.name}] {log.decode('utf-8').rstrip()}")


def compose(project: Project, base_image: str, src_dir: Path) -> None:
    from docker.models.containers import Container as ContainerType

    client = DockerClient.from_env()
    containers: list[ContainerType] = []
    log_treads: list[Thread] = []

    compiled = CompiledProject.from_project(project)

    networks = [
        net for net in client.networks.list()
        if net.name == project.name
    ]

    conts: list[ContainerType] = client.containers.list(
        all=True, filters={"label": "nobs"}
    )

    logger.info(conts)
    for cont in conts:
        cont.remove(force=True)

    if networks:
        network = networks[0]
    else:
        network = client.networks.create(name=project.name, driver="bridge")

    secret_vals: dict[str, str] = {}
    read_only_volume = {
        src_dir.absolute().as_posix(): {
            "bind": f"/app/{src_dir.name}",
            "mode": "ro"
        }
    }

    for container in needed_containers(compiled):
        logger.info(f"Creating resource {container.name}")

        cont = client.containers.run(
            image=container.image,
            environment=container.environments,
            volumes=container.volumes,
            network=network.name,
            detach=True,
            name=container.name,
            remove=True,
            labels=["nobs"],
            ports=container.ports,

            # restart_policy=container.restart,
            # ports=container.ports,
        )

        secret_vals.update(container.additional_secrets)

        logger.info(f"Waiting for {project.name}")
        while cont.status != "running":
            cont = client.containers.get(cont.id)
            sleep(1)

        containers.append(cont)
        thread = Thread(target=stream_container, args=(cont.id,))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    for container in compiled.network_apps:

        logger.info(f"Creating app {container.name}")

        if "uvicorn" in container.command[-1] and "--reload" not in container.command:
            container.command[-1] = container.command[-1] + " --reload"

        logger.info(container.command)
        cont = client.containers.run(
            image=base_image,
            name=container.name,
            environment={
                **(container.environments or {}),
                **secret_vals
            },
            volumes=read_only_volume,
            command=container.command,
            network=network.name,
            detach=True,
            labels=["nobs"],
            ports={f"{container.port}/tcp": container.port},
        )
        containers.append(cont)

        thread = Thread(target=stream_container, args=(cont.id,))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    for container in compiled.subscribers:
        logger.info(f"Creating subscriber {container.name}")
        cont = client.containers.run(
            image=base_image,
            name=container.name,
            environment={
                **(container.environments or {}),
                **secret_vals
            },
            volumes=read_only_volume,
            command=["/bin/bash", "-c", f"nobs subscriber {container.name}"],
            network=network.name,
            detach=True,
            labels=["nobs"]
        )

        containers.append(cont)

        thread = Thread(target=stream_container, args=(cont.id,))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)

    logger.info(containers)

    try:
        while True:
            sleep(10000)
    except KeyboardInterrupt:
        logger.info(f"Shutting down all containers")
        for container in reversed(containers):
            container.stop()

    logger.info("Stopped all containers")

