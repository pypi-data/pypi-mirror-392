# Tests for workflow classes
#

import pytest

from comopy.utils.workflow import (
    BasePass,
    BaseStage,
    JobPipeline,
    PassGroup,
)


class PassA1(BasePass):
    def __call__(self, input):
        return input + "-A1"


class PassA2(BasePass):
    def __call__(self, input):
        return input + "-A2"


class StageA(BaseStage):
    def check_input(self, input):
        if not isinstance(input, str):
            raise TypeError("Input is not a string.")


class PassB1(BasePass):
    def __call__(self, input):
        return input + "-B1"


class BadPass(BasePass):
    def __call__(self, input):
        return None


def test_workflow():
    # empty pipeline
    assert JobPipeline()("Hello") == "Hello"
    assert JobPipeline()(123) == 123

    group = PassGroup(PassA1(), PassA2())
    pipeline = JobPipeline(StageA(group), BaseStage(PassB1()))
    s = pipeline("Hello")
    assert s == "Hello-A1-A2-B1"

    # check_input()
    with pytest.raises(TypeError, match=r"not a string"):
        pipeline(1)

    # Bad pass in stage
    pipeline = JobPipeline(StageA(group), BaseStage(BadPass(), "BadStage"))
    with pytest.raises(Exception, match=r"No return value from BadStage"):
        s = pipeline("Hello")

    # Bad pass in group
    group = PassGroup(PassA1(), BadPass())
    pipeline = JobPipeline(StageA(group), BaseStage(PassB1()))
    with pytest.raises(Exception, match=r"No return value from BadPass"):
        s = pipeline("Hello")
