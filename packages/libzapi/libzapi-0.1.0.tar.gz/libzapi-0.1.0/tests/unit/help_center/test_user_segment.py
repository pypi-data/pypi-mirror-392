from hypothesis.strategies import builds, just

from libzapi.domain.models.help_center.user_segment import UserSegment
from hypothesis import given

strategy = builds(
    UserSegment,
    name=just("cciiA"),
)


@given(strategy)
def test_session_logical_key_from_id(model: UserSegment) -> None:
    assert model.logical_key.as_str() == "user_segment:cciia"
