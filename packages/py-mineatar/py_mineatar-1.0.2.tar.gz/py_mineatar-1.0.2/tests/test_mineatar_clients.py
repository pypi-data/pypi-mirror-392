# test_mineatar_clients.py
import hashlib
import pytest
from mineatar import MineatarClient, AsyncMineatarClient

UUID = "069a79f4-44e9-4726-a5be-fca90e38aaf5"

EXPECTED_HASHES = {
    "skin": "981022ae35bf44c2c69caf1df1afb392c012620df720c9476385398e93b3458537fdcf8a2760a2d02908e0065aa672c3f54bd4c0544a806ce555a85d8cf6ae01",
    "head": "de3769ad90e044a63fae2a64612e94a8b0998a41bd6dc4a36a9786f8a65b6789307462e041d76e6b79edcc4146596d8e1fdb084be6436306486efe94e83e506b",
    "fullbody": "fe0be5181eeecb7ee6bed3d6443a24c2c0c62004fae1355297aa3a7def78270c001723aa85c5c1314d048038f248de0d3147a7d2a2af48b814359a087a076822",
}


def sha512(data: bytes) -> str:
    return hashlib.sha512(data).hexdigest()


# -----------------------
# Synchronous tests
# -----------------------
def test_sync_client_hashes():
    client = MineatarClient()
    with client:
        skin = client.get_skin(UUID)
        head = client.get_head(UUID)
        fullbody = client.get_fullbody(UUID)

        assert sha512(skin) == EXPECTED_HASHES["skin"]
        assert sha512(head) == EXPECTED_HASHES["head"]
        assert sha512(fullbody) == EXPECTED_HASHES["fullbody"]


# -----------------------
# Asynchronous tests
# -----------------------
@pytest.mark.asyncio
async def test_async_client_hashes():
    client = AsyncMineatarClient()

    async with client:
        skin = await client.get_skin(UUID)
        head = await client.get_head(UUID)
        fullbody = await client.get_fullbody(UUID)

        assert sha512(skin) == EXPECTED_HASHES["skin"]
        assert sha512(head) == EXPECTED_HASHES["head"]
        assert sha512(fullbody) == EXPECTED_HASHES["fullbody"]

