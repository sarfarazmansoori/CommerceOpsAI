from src.agents.bedrock_explainer import explain_investigation


SAMPLE_RESULT = {
    "order_id": "ORD-1002",
    "diagnosis": "inventory_shortage",
    "evidence": ["Available quantity: 0", "Required quantity: 1"],
    "recommended_action": "escalate_inventory_shortage",
    "requires_human_approval": True,
}


def test_bedrock_disabled_returns_none(monkeypatch):
    monkeypatch.setenv("BEDROCK_ENABLED", "false")

    assert explain_investigation(SAMPLE_RESULT) is None


def test_missing_model_id_returns_none(monkeypatch):
    monkeypatch.setenv("BEDROCK_ENABLED", "true")
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)

    assert explain_investigation(SAMPLE_RESULT) is None


def test_bedrock_error_falls_back_safely(monkeypatch):
    import src.agents.bedrock_explainer as module

    class FakeClient:
        def converse(self, **kwargs):
            raise module.ClientError(
                {
                    "Error": {
                        "Code": "AccessDeniedException",
                        "Message": "Access denied",
                    }
                },
                "Converse",
            )

    class FakeBoto3:
        def client(self, *args, **kwargs):
            return FakeClient()

    monkeypatch.setenv("BEDROCK_ENABLED", "true")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "test-model")
    monkeypatch.setattr(module, "boto3", FakeBoto3())

    assert explain_investigation(SAMPLE_RESULT) is None


def test_successful_explanation_is_returned(monkeypatch):
    import src.agents.bedrock_explainer as module

    class FakeClient:
        def converse(self, **kwargs):
            return {
                "output": {
                    "message": {
                        "content": [
                            {"text": "Inventory is insufficient."}
                        ]
                    }
                }
            }

    class FakeBoto3:
        def client(self, *args, **kwargs):
            return FakeClient()

    monkeypatch.setenv("BEDROCK_ENABLED", "true")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "test-model")
    monkeypatch.setattr(module, "boto3", FakeBoto3())

    assert explain_investigation(SAMPLE_RESULT) == (
        "Inventory is insufficient."
    )
