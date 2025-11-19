import pytest
from autoresumex.generator import generate

PROFILE = {"name": "Test", "contact": "t@test.com"}

def test_missing():
    with pytest.raises(ValueError):
        generate({}, save="out.pdf")

def test_generate(tmp_path):
    out = tmp_path/"out.pdf"
    generate(PROFILE, save=str(out))
    assert out.exists()
