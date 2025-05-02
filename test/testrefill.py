@pytest.mark.asyncio
async def test_empty_shard_trigger(async_client, monkeypatch):
    async def mock_get_unused_number(*args, **kwargs):
        return None  # Simulate empty shard

    from shard_manager import get_unused_number
    monkeypatch.setattr("shard_manager.get_unused_number", mock_get_unused_number)

    resp = await async_client.get("/random")
    assert resp.status_code == 503
    assert "refilled" in resp.json()["error"]
