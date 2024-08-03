import pytest

from postit.registry import TaggerRegistry, tagger

# TODO: Add tests for module importing


def test_tagger_registry_singleton():
    registry1 = TaggerRegistry()
    registry2 = TaggerRegistry()
    assert registry1 is registry2


def test_tagger_registry_add_and_get():
    @TaggerRegistry.add()
    def sample_tagger():
        return "sample"

    assert TaggerRegistry.get("sample_tagger")() == "sample"

    with pytest.raises(ValueError):
        TaggerRegistry.get("non_existent_tagger")


def test_tagger_registry_all():
    @TaggerRegistry.add()
    def another_tagger():
        return "another"

    all_taggers = TaggerRegistry.all()
    assert "sample_tagger" in all_taggers
    assert "another_tagger" in all_taggers
    assert all_taggers["another_tagger"]() == "another"


def test_tagger_decorator():
    @tagger
    class SampleTagger:
        pass

    assert TaggerRegistry.get("SampleTagger") is SampleTagger
