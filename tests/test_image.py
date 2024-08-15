import pytest
import typst

from pypst.image import Image


def test_simple_image():
    image = Image("image.png")
    assert image.render() == '#image("image.png")'


def test_image_with_format():
    image = Image("image.png", format="jpg")
    assert image.render() == '#image("image.png", format: "jpg")'


def test_image_with_width():
    image = Image("image.png", width="100px")
    assert image.render() == '#image("image.png", width: 100px)'


def test_image_with_height():
    image = Image("image.png", height="100px")
    assert image.render() == '#image("image.png", height: 100px)'


def test_image_with_alt():
    image = Image("image.png", alt='"This is an image"')
    assert image.render() == '#image("image.png", alt: "This is an image")'


def test_image_with_fit():
    image = Image("image.png", fit="contain")
    assert image.render() == '#image("image.png", fit: "contain")'


@pytest.mark.integration
@pytest.mark.parametrize(
    "image",
    [
        Image("image.png"),
        Image('"image.png"'),
        Image("image.png", format="png", width="100pt", alt='"This is an image"'),
        Image("image.png", width="100pt", height="100pt", fit="contain"),
    ],
)
def test_compilation(image, image_on_disk, tmp_path):
    with open(tmp_path / "test.typ", mode="wt") as f:
        f.write(image.render())

    typst.compile(tmp_path / "test.typ")
