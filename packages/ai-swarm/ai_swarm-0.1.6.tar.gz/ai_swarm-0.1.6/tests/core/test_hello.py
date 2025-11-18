from swarm.core import hello


def test_hello_msg() -> None:
    result = hello.hello_msg("Swarm")
    assert result == "Hello, Swarm"
