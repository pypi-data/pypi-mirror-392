from collections import Counter
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from fnmatch import fnmatch
from typing import Any, Generator
from typing_extensions import Annotated
import os
import httpx
import tomllib
import typer

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}
CONFIG_NAME = "trifold.toml"
STORAGE_REGIONS = ["DE", "UK", "SE", "NY", "LA", "SG", "SYD", "BR", "JH"]

ALWAYS_IGNORE = [".git/*", CONFIG_NAME]

console = Console()
app = typer.Typer()
client = httpx.Client(headers=HEADERS)


class BunnyError(Exception):
    pass


def p_success(text: str) -> None:
    console.print(f"[green]{text}[/green]")


def p_warning(text: str) -> None:
    console.print(f"[yellow]{text}[/yellow]")


def p_error(text: str) -> None:
    console.print(f"[red]{text}[/red]")


def debug(text: str | httpx.Response) -> None:
    console.print(f"[purple]{text}[/purple]")


# price per GB as of Nov 2025
PULL_GEO_ZONES = {
    "ASIA": 0.03,
    "EU": 0.01,
    "AF": 0.06,
    "NA": 0.01,
    "SA": 0.045,
}
GIGABYTE = 1_000_000_000


def _api_key() -> str:
    bunny_api_key = os.getenv("BUNNY_API_KEY")
    if not bunny_api_key:
        bunny_api_key = Prompt.ask("Bunny API Key")
    return bunny_api_key


def _api_post(method: str, payload: dict[str, str], key: str) -> httpx.Response:
    """
    make a bunny.net API POST
    """
    url = "https://api.bunny.net/" + method
    resp = client.post(url, json=payload, headers=HEADERS | {"accessKey": key})
    if resp.status_code >= 400:
        raise BunnyError(resp.text)
    return resp


def create_storage_zone(
    bunny_key: str, name: str, region: str, replication: list[str]
) -> httpx.Response:
    """
    create a bunny.net storage zone (bucket)
    """
    payload = {
        "Name": name,
        "Region": region,
        "ReplicationRegions": replication,
        "ZoneTier": "Standard",
    }
    return _api_post("storagezone", payload, bunny_key)


def create_pull_zone(
    bunny_key: str, storage_zone_id: str, name: str, limit_gb: int
) -> httpx.Response:
    """
    create a bunny.net pull zone (CDN hostname)
    """
    payload = {
        "Name": name,
        # TODO: make configurable
        "Type": "Premium",  # best for sites? Volume does not have geo zones?
        "EnableGeoZoneUS": True,
        "EnableGeoZoneEU": False,
        "EnableGeoZoneASIA": False,
        "EnableGeoZoneSA": False,
        "EnableGeoZoneAF": False,
        "BlockPostRequests": False,
        "MonthlyBandwidthLimit": limit_gb * GIGABYTE,
        "EnableAutoSSL": True,
        "StorageZoneId": storage_zone_id,
        "OriginType": 2,  # Storage Zone origin
        "PreloadingScreenEnabled": False,
        # EnableLogging?,
    }
    return _api_post("pullzone", payload, bunny_key).json()


def add_custom_hostname(bunny_key: str, pull_zone_id: str, hostname: str) -> None:
    """
    add a hostname and initialize SSL
    """
    # TODO: all of these calls can error potentially, so writing this
    #       to be repeatable, but there's got to be a better way than
    #       "just run this until SSL works" with some checks in place
    try:
        resp = _api_post(
            f"pullzone/{pull_zone_id}/addHostname", {"Hostname": hostname}, bunny_key
        )
        debug(resp)
    except BunnyError as e:
        debug(e)
    url = f"https://api.bunny.net/pullzone/loadFreeCertificate?hostname={hostname}"
    try:
        resp = client.get(url, headers=HEADERS | {"AccessKey": bunny_key}).json()
        debug(resp)
    except Exception as e:
        # this seems to time out but succeed?
        debug(e)
        pass
    _api_post(
        f"pullzone/{pull_zone_id}/setForceSSL",
        {"Hostname": hostname, "ForceSSL": True},
        bunny_key,
    )


def list_storage_zones(bunny_key: str) -> dict[str, Any]:
    """
    Get all storage zones (called by zones)
    """
    url = "https://api.bunny.net/storagezone?page=0&perPage=1000&includeDeleted=false"
    zones = client.get(url, headers=HEADERS | {"AccessKey": bunny_key}).json()
    return zones


def get_storage_zone_by_name(key: str, name: str) -> dict:
    """
    Look up a specific storage zone by name, useful for obtaining password.
    """
    for zone in list_storage_zones(key):
        if zone["Name"] == name:
            return zone


def load_config() -> dict[str, Any]:
    with open(CONFIG_NAME, "rb") as f:
        config = tomllib.load(f)
    # TODO: give option to save password, or require key to always be present
    if "password" not in config:
        key = _api_key()
        config["password"] = get_storage_zone_by_name(key, config["storage_zone"])[
            "Password"
        ]
    return config


def get_full_storage_zone(region: str, zone: str, password: str, dir: str) -> Generator[str, None, None]:
    url = f"https://{region_prefix(region)}storage.bunnycdn.com/{zone}/{dir}/"
    response = client.get(url, headers={"accessKey": password})
    for obj in response.json():
        full_name = obj["Path"].split("/", 2)[2] + obj["ObjectName"]
        if obj["IsDirectory"]:
            yield from get_full_storage_zone(region, zone, password, full_name)
        else:
            yield full_name


def diff_storage_zone(config: dict[str, Any]) -> list[tuple[str, str]]:
    remote = set(
        get_full_storage_zone(
            config["region"],
            config["storage_zone"],
            config["password"],
            config["remote_path"],
        )
    )
    local_dir = Path.cwd() / config["local_path"]
    local_files = {
        str(f.relative_to(local_dir)) for f in local_dir.rglob("*") if f.is_file()
    }
    results = []
    only_local = local_files - remote
    only_remote = remote - local_files
    both = local_files & remote
    for f in only_local:
        if is_ignored(f, config["ignore"] + ALWAYS_IGNORE):
            results.append((f, "ignored"))
        else:
            results.append((f, "only_local"))
    for f in only_remote:
        results.append((f, "only_remote"))
    for f in both:
        # TODO: check status using hash
        results.append((f, "both"))
    return results


def is_ignored(path: str, ignorelist: list[str])-> bool:
    for pattern in ignorelist:
        if fnmatch(path, pattern):
            return True
    return False


def show_plan(file_status_list: list[tuple[str, str]], verbosity: int) -> None:
    counts = Counter()
    if verbosity >= 1:
        table = Table(show_header=True, header_style="bold")
        table.add_column("File")
        table.add_column("Status")
    for filename, status in file_status_list:
        counts[status] += 1
        if verbosity >= 1:
            if status == "only_local":
                table.add_row(filename, f"[yellow]{status}[/yellow]")
            elif status == "only_remote":
                table.add_row(filename, f"[magenta]{status}[/magenta]")
            elif status == "ignored":
                if verbosity >= 2:
                    table.add_row(filename, f"[dim]{status}[/dim]")
            else:
                table.add_row(filename, f"[blue]{status}[/blue]")
    if verbosity >= 1:
        console.print(table)
    console.print(f"[green]{counts['only_local']} only_local[/green] | ", end="")
    console.print(f"[yellow]{counts['only_remote']} only_remote[/yellow] | ", end="")
    console.print(f"[blue]{counts['both']} both[/blue]")


def execute_plan(config: dict[str, Any], file_status_list: list[tuple[str, str]], delete: bool=False) -> None:
    upload_count = 0
    delete_count = 0

    local_dir = Path.cwd() / config["local_path"]

    for filename, status in file_status_list:
        match status:
            case "only_local":
                upload_file(
                    config["region"],
                    config["storage_zone"],
                    config["password"],
                    filename,
                    local_dir,
                )
                upload_count += 1
            case "only_remote":
                if delete:
                    delete_remote_file(
                        config["region"],
                        config["storage_zone"],
                        config["password"],
                        filename,
                    )
                delete_count += 1
            case "both":
                # TODO: check status using hash
                upload_file(
                    config["region"],
                    config["storage_zone"],
                    config["password"],
                    filename,
                    local_dir,
                )
                upload_count += 1

    # print actions
    p_success(f"\nuploaded: {upload_count}")
    if delete:
        p_warning(f"deleted: {delete_count}")
    else:
        p_warning(f"[yellow]would delete: {delete_count}[/yellow]")


def region_prefix(region: str) -> str:
    return "" if region == "DE" else f"{region.lower()}."


def upload_file(
    region: str, zone: str, password: str, local_path: str, local_dir: Path
) -> None:
    """
    upload a file

    called by publish
    """
    url = f"https://{region_prefix(region)}storage.bunnycdn.com/{zone}/{local_path}"
    with open(local_dir / local_path, "rb") as file:
        resp = client.put(url, headers=HEADERS | {"AccessKey": password}, data=file)
        # expect 201
        if resp.status_code != 201:
            debug(resp)  # 201s
            resp.raise_for_status()


def delete_remote_file(region: str, zone: str, password: str, local_path: Path) -> None:
    """
    delete a remote file

    called by publish (--delete)
    """
    url = f"https://{region_prefix(region)}.storage.bunnycdn.com/{zone}/{local_path}"
    resp = client.delete(url, headers=HEADERS | {"AccessKey": password})
    if resp.status_code != 200:
        debug(resp)
        resp.raise_for_status()


def show_prices_table(key: str) -> None:
    """
    show available regions (limited to those known to be valid from web UI)
    """
    resp = client.get("https://api.bunny.net/region", headers={"AccessKey": key})
    table = Table(show_header=True, header_style="bold")
    table.add_column("Region")
    # prices in API are not for storage costs, do not use
    # table.add_column("Price/GB")
    table.add_column("Name")
    for region in resp.json():
        if region["RegionCode"] in STORAGE_REGIONS:
            table.add_row(region["RegionCode"], region["Name"])
    console.print(table)


# Typer Commands ##############


@app.command()
def init() -> int | None:
    """
    Initialize a new hosted site & write a trifold.toml
    """
    bunny_api_key = _api_key()
    zone_name = Prompt.ask("storage zone name")

    # TODO: SSD storage option (no regions, 0.08/GB, much faster?)

    show_prices_table(bunny_api_key)
    region = Prompt.ask("region", choices=STORAGE_REGIONS, default="DE")

    # prompt for replication regions
    replication_regions = []
    while True:
        rep_region = Prompt.ask(
            "add replication region? (blank to stop)",
            choices=STORAGE_REGIONS + [""],
            default="",
        )
        if rep_region:
            replication_regions.append(rep_region)
        else:
            break

    # storage zone
    szone = get_storage_zone_by_name(bunny_api_key, zone_name)

    if szone:
        p_error(f"storage zone '{zone_name}' already exists, exiting")
        console.print(f"  id: {szone['Id']}")
        console.print(f"  region: {szone['Region']}")
        console.print(f"  replication regions: {szone['ReplicationRegions']}")
        return -1

    create_storage_zone(bunny_api_key, zone_name, region, replication_regions)
    p_success(f"created storage zone '{zone_name}'")
    szone = get_storage_zone_by_name(bunny_api_key, zone_name)

    # pull zone
    max_gb = IntPrompt.ask("Monthly bandwidth limit (GB): ", default=10)
    pzone = create_pull_zone(bunny_api_key, szone["Id"], zone_name, max_gb)
    p_success(f"created pull zone '{zone_name}'")

    pull_zone_id = pzone["Id"]

    # paths
    remote_path = Prompt.ask("remote path", default="")
    local_path = Prompt.ask("local path", default="")
    config_content = f"""storage_zone = "{zone_name}"
region = "{region}"
remote_path = "{remote_path}"
local_path = "{local_path}"
pull_zone_id = "{pull_zone_id}"
ignore = []
"""
    with open(CONFIG_NAME, "w") as f:
        f.write(config_content)

    p_success(f"Created {CONFIG_NAME}")


@app.command()
def status(
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
) -> None:
    """
    Show differences between local and remote.
    """
    config = load_config()
    plan = diff_storage_zone(config)
    show_plan(plan, verbose)


@app.command()
def hostname_add(hostname: str) -> None:
    """
    Add a custom hostname to the site.
    """
    config = load_config()
    if not Confirm.ask(
        f"does a DNS record already exist pointing {hostname} => {config['storage_zone']}.b-cdn.net?"
    ):
        p_error("ensure DNS has been set, then try again")
        return
    add_custom_hostname(_api_key(), config["pull_zone_id"], hostname)


@app.command()
def publish(delete: bool = False) -> None:
    """
    Publish local files to remote & purge cache.
    """
    config = load_config()
    plan = diff_storage_zone(config)
    show_plan(plan, 0)
    execute_plan(config, plan, delete)
    _api_post(f"pullzone/{config['pull_zone_id']}/purgeCache", {}, _api_key())
    p_success("cache purged!")


@app.command()
def zones() -> None:
    """
    Show all bunny.net zones and their current status.
    """
    key = _api_key()
    existing_zones = list_storage_zones(key)
    for zone in existing_zones:
        # StorageUsed
        print(zone["Id"], zone["Name"], zone["Region"], zone["ReplicationRegions"])
        for pullzone in zone["PullZones"]:
            print(" " * 2, pullzone["Id"], pullzone["Name"])
            for host in pullzone["Hostnames"]:
                # HasCertificate
                print(" " * 4, host["Id"], host["Value"], host["ForceSSL"])


if __name__ == "__main__":
    app()
