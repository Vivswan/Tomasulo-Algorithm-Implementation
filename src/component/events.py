from typing import Tuple, Union

stage_event_type = Union[int, Tuple[int, int]]


class StageEvent:
    issue: stage_event_type
    execute: stage_event_type
    memory: stage_event_type
    write_back: stage_event_type
    commit: stage_event_type
