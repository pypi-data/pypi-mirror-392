"""Simple test by calling mdtoreveal.main()"""

import sys

from mdtoreveal import main


def test_simple_run(monkeypatch, tmp_path):
    """Test that an html file is created."""
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.html"

    input_file.write_text("# column 1\n\n## slide1\n\n# column 2\n")
    monkeypatch.setattr(
        sys, "argv", ["mdtoreveal", str(input_file), "--output", str(output_file)]
    )
    main()
    assert "column 1" in output_file.read_text()


def test_guess_output(monkeypatch, tmp_path):
    """Test that not giving an output file works."""
    input_file = tmp_path / "slides.md"
    output_file = tmp_path / "slides.html"

    input_file.write_text("# column 1\n\n## slide1\n\n# column 2\n")
    monkeypatch.setattr(sys, "argv", ["mdtoreveal", str(input_file)])
    main()
    assert "column 1" in output_file.read_text()


def test_set_title(monkeypatch, tmp_path):
    """Test that not giving an output file works."""
    input_file = tmp_path / "slides.md"
    output_file = tmp_path / "slides.html"

    input_file.write_text("# column 1\n\n## slide1\n\n# column 2\n")
    monkeypatch.setattr(sys, "argv", ["mdtoreveal", str(input_file), "--title", "BoO"])
    main()
    assert "<title>BoO</title>" in output_file.read_text()
