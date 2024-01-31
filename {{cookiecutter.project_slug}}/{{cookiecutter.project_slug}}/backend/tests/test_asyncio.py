async def hello_world():
    return "hello world"


async def test_hello_world():
    given = await hello_world()
    assert given == "hello world"
