import datetime
from pathlib import Path
from typing import Optional, Union, List
import logging

import imageio
from io import BytesIO

import prefect
from prefect import task, Parameter, Flow
from prefect.engine.signals import SKIP
from prefect.tasks.shell import ShellTask
from prefect.executors import LocalDaskExecutor

Runable = Optional[Union[str, List[str]]]

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="debug.log",
    format="[%(asctime)s][%(levelname)-4s]: %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)


@task
def curl_cmd(url: str, file: str) -> str:
    """
    The curl command we wish to execute.
    """
    prefect.context.get("logger")
    if Path(file).exists():
        raise SKIP("Image data file already exists.")
    return f"curl -fL -o {file} {url}"


download: Runable = ShellTask(
    name="curl_task", max_retries=2, retry_delay=datetime.timedelta(seconds=10)
)


@task(skip_on_upstream_skip=False)
def load_and_split(fname: str) -> list:
    """
    Loads image data file at `fname` and splits it into
    multiple frames.  Returns a list of bytes, one element
    for each frame.
    """
    prefect.context.get("logger")
    with open(fname, "rb") as f:
        imgs = f.read()

    return [img for img in imgs.split(b"\n" * 4) if img]


@task
def write_to_disk(image: bytes) -> bytes:
    """
    Given a single image represented as bytes, writes the image
    to the present working directory with a filename determined
    by `map_index`.  Returns the image bytes.
    """
    prefect.context.get("logger")
    frame_no = prefect.context.get("map_index")
    Path("src/pipeline/temp/frames").touch()
    # make sure the path exists, as prefect does not populate path for you
    frame_path = Path("src/pipeline/temp/frames/frame_{0:0=2d}.gif".format(frame_no))
    with open(frame_path, "wb") as f:
        f.write(image)
    return image


@task
def combine_to_gif(image_bytes: list, gif_file: Path) -> None:
    """
    Given a list of ordered images represented as bytes,
    combines them into a single GIF stored in the present working directory.
    """
    prefect.context.get("logger")
    images = [imageio.imread(BytesIO(image)) for image in image_bytes]
    imageio.mimsave(gif_file, images)


with Flow("Image ETL") as flow:
    Path("src/pipeline/temp").touch()
    image_path = Path("src/pipeline/temp/image-data.img")
    gif_path = Path("src/pipeline/temp/comb.gif")

    DATA_URL = Parameter(
        "DATA_URL",
        default="https://github.com/cicdw/image-data/blob/master/all-images.img?raw=true",
    )
    DATA_FILE = Parameter("DATA_FILE", default=image_path)

    # Extract
    command = curl_cmd(DATA_URL, DATA_FILE)
    curl = download(command=command)

    # Transform
    # we use the `upstream_tasks` keyword to specify non-data dependencies
    images = load_and_split(fname=DATA_FILE, upstream_tasks=[curl])

    # Load
    frames = write_to_disk.map(images)
    combine_to_gif(frames, gif_path)

if __name__ == "__main__":
    flow.visualize()
    flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=4)
    flow.run()
