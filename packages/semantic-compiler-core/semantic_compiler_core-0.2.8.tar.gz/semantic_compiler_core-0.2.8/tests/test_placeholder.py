def test_placeholder():
    assert True


from semantic_compiler_core.sir_model import DecisionPipeline, sir_from_dict


def test_sir_from_dict_minimal():
    data = {
        "type": "DecisionPipeline",
        "name": "test",
        "input_name": "txn",
        "steps": []
    }
    p = sir_from_dict(data)
    assert isinstance(p, DecisionPipeline)
    assert p.name == "test"

