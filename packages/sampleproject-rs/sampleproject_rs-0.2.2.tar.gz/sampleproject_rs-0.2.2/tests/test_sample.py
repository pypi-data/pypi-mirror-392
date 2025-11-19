import subprocess


def test_add_one():
    from sample import simple

    assert simple.add_one(20) == 21


def test_sample_command():
    result = subprocess.run(["sample"], capture_output=True, text=True, check=True)
    assert result.stdout == "Call your main application code here\n"
