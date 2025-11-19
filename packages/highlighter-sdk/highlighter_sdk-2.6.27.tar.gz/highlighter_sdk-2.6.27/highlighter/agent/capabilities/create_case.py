import logging
import time
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple
from uuid import UUID

import celpy
from celpy import celtypes
from celpy.evaluation import CELEvalError, CELUnsupportedError
from numpy import isin
from pydantic import BaseModel, ConfigDict, PrivateAttr

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.agent.observations_table import ObservationsTable
from highlighter.cli.cli_logging import ColourStr, format_stream_info
from highlighter.client import HLClient
from highlighter.client.base_models.entities import Entities, Entity

logger = logging.getLogger(__name__)


class Trigger(BaseModel):

    capability_name: Optional[str] = None
    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    def get_state(self, stream, **kwargs) -> bool:
        """Returns True if trigger is in 'on' state, False if in 'off' state."""
        pass


def create_trigger(trigger_params: Dict) -> Trigger:
    """Factory function to create trigger instances based on configuration."""
    trigger_type = trigger_params.get("type", "PeriodicTrigger")
    params = {k: v for k, v in trigger_params.items() if k != "type"}

    logger.debug(f"create_trigger called with: trigger_type='{trigger_type}', params={params}")

    if trigger_type == "PeriodicTrigger":
        trigger = PeriodicTrigger(**params)
        logger.debug(f"Created PeriodicTrigger: {trigger}")
        return trigger
    if trigger_type == "RuleTrigger":
        trigger = RuleTrigger(**params)
        logger.debug(f"Created RuleTrigger: {trigger}")
        return trigger
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")


class PeriodicTrigger(Trigger):
    on_period: float  # sec
    off_period: float  # sec

    _start_time: Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _is_on_period(self) -> bool:
        """Determines if the current time is within an 'on' period."""
        current_time = time.time()

        if self._start_time is None:
            self._start_time = current_time

        elapsed = current_time - self._start_time
        cycle_time = self.on_period + self.off_period

        if cycle_time <= 0:
            # Avoid division by zero; default to 'on' if periods are non-positive.
            return True

        cycle_position = elapsed % cycle_time
        return cycle_position < self.on_period

    def get_state(self, *args, **kwargs) -> bool:
        """Returns True if in 'on' period, False if in 'off' period."""
        return self._is_on_period()


class RuleTrigger(Trigger):
    """Evaluate a CEL expression against the available trigger context."""

    expression: str
    expected_entities: List[str]
    patience: int = 0  # sec - time to wait after last True before returning False
    default_state: bool = False
    log_errors_every_n_frames: int = 100  # Log evaluation errors once every N frames (0 = always log)

    _attribute_collection_warnings: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _evaluation_error_count: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _program_cache: dict = PrivateAttr(default_factory=dict)

    _entity_buffer: ClassVar[Dict] = dict()

    def __init__(self, **data):
        super().__init__(**data)
        self._last_true_trigger = None
        self._prev_state = self.default_state

    def get_state(self, stream, *, data_sample, **kwargs) -> bool:

        # Log entry with stream info
        logger.debug(
            "=== get_state() called ===",
            extra={"stream_id": stream.stream_id, "capability_name": self.capability_name or "RuleTrigger"},
        )

        is_entities = lambda x: isinstance(x, Entities) or (
            isinstance(x, dict) and x and isinstance(x[list(x)[0]], Entity)
        )

        self._entity_buffer.update(kwargs)
        logger.debug(f"{self._entity_buffer.keys()}")
        if not all([e in self._entity_buffer for e in self.expected_entities]):
            logger.debug(f"s:{stream.stream_id} - no trigger update, {self._entity_buffer.keys()}")
            return self._prev_state
        logger.debug(f"s:{stream.stream_id} - evaluating trigger")

        # if "beaking" in kwargs:
        #    print(ColourStr.green(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))
        # elif ("clustering" in kwargs) and ("motion" in kwargs):
        #    print(ColourStr.blue(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))
        # else:
        #    print(ColourStr.red(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))

        observations_table = ObservationsTable()
        for ents in self._entity_buffer.values():
            for e in ents.values():
                observations_table.add_entity(e, data_sample, stream.stream_id)

        # If no rows exist in the observations table (entities with no observations or no entities),
        # create a row with data_sample info but no entity data
        # This allows data_sample expressions to be evaluated even when no entities/observations are detected
        if len(observations_table._rows) == 0:
            data_sample_row = ObservationsTable.Row(
                entity=None,  # No entity detected
                stream=ObservationsTable.Row.Stream(id=stream.stream_id),
                data_sample=ObservationsTable.Row.DataSample(
                    recorded_at=data_sample.recorded_at,
                    content_type=data_sample.content_type,
                    stream_frame_index=data_sample.stream_frame_index,
                    media_frame_index=data_sample.media_frame_index,
                ),
                annotation=None,  # No annotation
                attribute={},
            )
            observations_table._rows[str(data_sample_row.id)] = data_sample_row

        observations_table.show()

        state = self._prev_state
        try:
            now = time.perf_counter()
            result = observations_table.any(self.expression)
            capability_label = self.capability_name or self.__class__.__name__
            logger.info(
                "%s stream %s: %s ---> evaluates to %s",
                capability_label,
                stream.stream_id,
                self.expression,
                result,
            )

            if result:
                self._last_true_trigger = time.perf_counter()
                state = True
            elif (self._last_true_trigger is not None) and ((now - self._last_true_trigger) > self.patience):
                state = False

            self._entity_buffer.clear()
            self._prev_state = state
            observations_table.clear()

        except Exception as exc:
            # Rate-limit error logging to avoid spam
            stream_id = getattr(stream, "stream_id", "unknown")
            error_key = f"{stream_id}:{type(exc).__name__}"
            self._evaluation_error_count[error_key] += 1

            # Log on first occurrence, then every Nth frame (if configured)
            # When log_errors_every_n_frames=0, always log
            should_log = (
                self.log_errors_every_n_frames == 0
                or self._evaluation_error_count[error_key] == 1
                or self._evaluation_error_count[error_key] % self.log_errors_every_n_frames == 0
            )

            if should_log:
                logger.warning(
                    "RuleTrigger evaluation failed for '%s' (count: %d): %s",
                    self.expression,
                    self._evaluation_error_count[error_key],
                    exc,
                )

        return state


class _StreamTrigger:

    def __init__(self, trigger: Callable, case_is_recording: bool):
        self.trigger = trigger
        self.case_is_recording = case_is_recording


@dataclass
class _RecordAllStreamsState:
    active: bool = False
    owner_stream_id: Optional[str] = None
    owner_capability: Optional[str] = None
    task_context: Optional[Any] = None
    lock: Lock = field(default_factory=Lock)


_RECORD_ALL_STREAMS_STATES: Dict[int, _RecordAllStreamsState] = {}


class RecordingAction(Enum):
    START_RECORDING = 0
    STOP_RECORDING = 1
    CONTINUE_RECORDING = 2
    CONTINUE_WAITING = 3


class CreateCase(Capability):
    """
    Capability that monitors incoming data and creates cases when trigger conditions are met.

    Uses simple delta-from-start-time triggering initially.
    """

    def _capability_label(self) -> str:
        return getattr(getattr(self, "definition", None), "name", self.__class__.__name__)

    def _get_record_all_streams_state(self) -> _RecordAllStreamsState:
        key_source = getattr(self.pipeline, "agent", None) or self.pipeline
        key = id(key_source)
        state = _RECORD_ALL_STREAMS_STATES.get(key)
        if state is None:
            state = _RecordAllStreamsState()
            _RECORD_ALL_STREAMS_STATES[key] = state
        return state

    class InitParameters(Capability.InitParameters):

        # Case creation parameters
        new_case_workflow_order_id: UUID
        new_case_entity_id: Optional[UUID] = None
        case_record_capabilities: List[str] = []
        new_case_task_step_id: Optional[str] = None
        record_all_streams: bool = False

        # Case metadata
        case_name_template: Optional[str] = None

        # Trigger configuration
        trigger_params: Dict = {"type": "PeriodicTrigger", "on_period": 30, "off_period": 300}

    class StreamParameters(InitParameters):
        pass

    def __init__(self, context):
        super().__init__(context)
        self.stream_triggers = {}
        self._streams = {}
        # (case_is_recording, trigger)
        START_RECORDING = (False, True)
        STOP_RECORDING = (True, False)
        CONTINUE_RECORDING = (True, True)
        CONTINUE_WAITING = (False, False)
        self._actions = {
            START_RECORDING: self._start_recording,
            STOP_RECORDING: self._stop_recording,
            CONTINUE_RECORDING: self._continue_recording,
            CONTINUE_WAITING: self._continue_waiting,
        }
        self._shared_task_context = None

    def start_stream(self, stream, stream_id, use_create_frame=True):
        """Initialize stream state"""
        stream_event, result = super().start_stream(stream, stream_id, use_create_frame=use_create_frame)

        # Get init parameters for this stream
        init_params = self.stream_parameters(stream_id)

        logger.debug(
            "=== start_stream() ===",
            extra={"stream_id": stream_id, "capability_name": self._capability_label()},
        )
        logger.debug(f"trigger_params: {init_params.trigger_params}")

        # Initialize trigger instance
        case_create_trigger = create_trigger(init_params.trigger_params)
        case_create_trigger.capability_name = self._capability_label()
        logger.debug(f"Created trigger of type: {type(case_create_trigger)}")

        self.stream_triggers[stream_id] = _StreamTrigger(case_create_trigger, False)
        self._streams[stream_id] = stream

        # Initialize client
        self.client = HLClient.get_client()
        return stream_event, result

    def stop_stream(self, stream, stream_id):
        """Clean up stream state and close open cases"""
        if stream_id in self.stream_triggers:
            stream_trigger = self.stream_triggers[stream_id]

            # Close any open cases before cleaning up
            if stream_trigger.case_is_recording:
                try:
                    parameters = self.stream_parameters(stream_id)
                    self._stop_recording(stream, parameters, stream_trigger)
                    self.logger.debug(
                        "Closed case during stream cleanup",
                        extra={"stream_id": stream_id, "capability_name": self._capability_label()},
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to close case during cleanup: {e}")

            del self.stream_triggers[stream_id]
        self._streams.pop(stream_id, None)

        # Finalize any pending recordings in TaskContext
        if self._shared_task_context:
            try:
                self._shared_task_context.finalise_submissions_on_recording_state_off()
            except Exception as e:
                self.logger.warning(f"Failed to finalize recordings during cleanup: {e}")

        shared_state = self._get_record_all_streams_state()
        with shared_state.lock:
            shared_context = shared_state.task_context
        if shared_context and shared_context is not self._shared_task_context:
            try:
                shared_context.finalise_submissions_on_recording_state_off()
            except Exception as e:
                self.logger.warning(f"Failed to finalize shared recordings during cleanup: {e}")

        return super().stop_stream(stream, stream_id)

    def process_frame(self, stream, data_samples, **kwargs) -> Tuple[StreamEvent, dict]:
        """
        Process incoming frame data and trigger case creation using Trigger class.

        Accepts arbitrary inputs from upstream capabilities via kwargs.
        """
        stream_id = stream.stream_id
        capability_name = self._capability_label()
        logger.debug(
            f"=== process_frame() called with {len(data_samples)} data_samples ===",
            extra={"stream_id": stream_id, "capability_name": capability_name},
        )

        # Check if stream is still active (may have been cleaned up during shutdown)
        if stream_id not in self.stream_triggers:
            self.logger.debug(
                "no longer active, skipping frame processing",
                extra={"stream_id": stream_id, "capability_name": capability_name},
            )
            response = {"data_samples": data_samples}
            response.update(kwargs)
            return StreamEvent.OKAY, response

        parameters = self.stream_parameters(stream_id)
        stream_trigger = self.stream_triggers[stream_id]
        capability_label = self._capability_label()
        logger.info(
            "%s stream %s trigger type: %s, case_is_recording: %s, record_all_streams=%s",
            capability_label,
            stream_id,
            type(stream_trigger.trigger),
            stream_trigger.case_is_recording,
            getattr(parameters, "record_all_streams", False),
        )

        if not stream_trigger.trigger:
            self.logger.warning(
                "No trigger found", extra={"stream_id": stream_id, "capability_name": capability_name}
            )
            return StreamEvent.OKAY, kwargs

        # ToDo: remove when entities are batched to corrispond to data_samples
        if len(data_samples) != 1:
            self.logger.warning(
                f"Expected 1 data sample, but got {len(data_samples)}. Processing first sample only."
            )

        raw_value = getattr(parameters, "record_all_streams", False)
        record_all_streams = raw_value if isinstance(raw_value, bool) else False

        for i, ds in enumerate(data_samples):
            trigger_kwargs = {"data_sample": ds}

            # ToDo: Entities are not batched. For now, we'll just assume
            # that we have one data_sample per tick.
            # trigger_kwargs.update({k: kwargs[k][i] for k in kwargs})
            trigger_kwargs.update(kwargs)

            case_is_recording = stream_trigger.case_is_recording
            logger.debug(f"Calling trigger.get_state() with kwargs: {list(trigger_kwargs.keys())}")
            trigger_state_on = stream_trigger.trigger.get_state(stream, **trigger_kwargs)
            logger.debug(f"Trigger returned: {trigger_state_on}, case_is_recording: {case_is_recording}")
            logger.debug(f"Action key: ({case_is_recording}, {trigger_state_on})")
            if record_all_streams:
                state = self._get_record_all_streams_state()
                with state.lock:
                    active = state.active
                if not active and trigger_state_on:
                    self._start_recording(stream, parameters, stream_trigger)
                elif active and not trigger_state_on:
                    self._stop_recording(stream, parameters, stream_trigger)

                # When state doesn't change, do nothing
                continue

            self._actions[(case_is_recording, trigger_state_on)](stream, parameters, stream_trigger)

        response = {"data_samples": data_samples}
        response.update(kwargs)
        return StreamEvent.OKAY, response

    def _start_recording(self, stream, parameters, stream_trigger):
        raw_value = getattr(parameters, "record_all_streams", False)
        record_all_streams = raw_value if isinstance(raw_value, bool) else False
        capability_label = self._capability_label()
        shared_state = self._get_record_all_streams_state() if record_all_streams else None
        owner_stream_id = shared_state.owner_stream_id if shared_state else None
        owner_capability = shared_state.owner_capability if shared_state else None
        active = shared_state.active if shared_state else stream_trigger.case_is_recording

        logger.debug(
            "_start_recording: capability=%s, stream=%s, record_all_streams=%s, owner_stream=%s, owner_capability=%s, active=%s",
            capability_label,
            stream.stream_id,
            record_all_streams,
            owner_stream_id,
            owner_capability,
            active,
        )

        if record_all_streams and shared_state:
            with shared_state.lock:
                if shared_state.active:
                    stream_trigger.case_is_recording = True
                    return

        case_name = None
        if parameters.case_name_template:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            case_name = parameters.case_name_template.format(timestamp=timestamp, stream_id=stream.stream_id)

        task_context, is_shared_context = self._get_task_context(
            None if record_all_streams else stream,
            create_if_missing=True,
        )
        if task_context is None:
            self.logger.warning("Unable to start recording; no task context available")
            return

        recorders = self._collect_recorders(
            stream,
            stream.stream_id,
            parameters,
            include_all_streams=record_all_streams,
        )

        if not recorders:
            stream_info_plain = format_stream_info(stream.stream_id, capability_label)
            raise ValueError(
                f"{stream_info_plain}: No recorders found with capabilities "
                f"{parameters.case_record_capabilities}. Ensure recording is enabled."
            )

        log_context = format_stream_info(stream.stream_id, capability_label)

        task_context.start_recording(
            recorders,
            parameters.new_case_workflow_order_id,
            case_name=case_name,
            entity_id=parameters.new_case_entity_id,
            log_context=log_context,
        )
        if is_shared_context:
            if record_all_streams and shared_state:
                with shared_state.lock:
                    shared_state.task_context = task_context
            else:
                self._shared_task_context = task_context

        if record_all_streams and shared_state:
            with shared_state.lock:
                shared_state.active = True
                shared_state.owner_stream_id = stream.stream_id
                shared_state.owner_capability = capability_label
            for trigger in self.stream_triggers.values():
                trigger.case_is_recording = True
        else:
            stream_trigger.case_is_recording = True

    def _stop_recording(self, stream, parameters, stream_trigger):
        raw_value = getattr(parameters, "record_all_streams", False)
        record_all_streams = raw_value if isinstance(raw_value, bool) else False
        capability_label = self._capability_label()
        shared_state = self._get_record_all_streams_state() if record_all_streams else None

        if record_all_streams and shared_state:
            with shared_state.lock:
                owner_stream_id = shared_state.owner_stream_id
                owner_capability = shared_state.owner_capability
                is_active = shared_state.active
            if not is_active or owner_stream_id is None:
                stream_trigger.case_is_recording = False
                return
            if stream.stream_id != owner_stream_id or owner_capability != capability_label:
                # Only the owning capability+stream pair stops the shared session
                return
        else:
            owner_stream_id = stream.stream_id if stream else None
            is_active = stream_trigger.case_is_recording

        logger.debug(
            "_stop_recording: capability=%s, stream=%s, record_all_streams=%s, owner_stream=%s, active=%s",
            capability_label,
            stream.stream_id if stream else "<none>",
            record_all_streams,
            owner_stream_id,
            is_active,
        )

        task_context, is_shared_context = self._get_task_context(
            None if record_all_streams else stream,
            create_if_missing=False,
        )
        if task_context is None:
            self.logger.warning("Attempted to stop recording but no task context exists")
            stream_trigger.case_is_recording = False
            return

        task_context.stop_recording()
        if is_shared_context:
            if record_all_streams and shared_state:
                with shared_state.lock:
                    shared_state.task_context = None
            else:
                self._shared_task_context = None

        if record_all_streams and shared_state:
            with shared_state.lock:
                shared_state.active = False
                shared_state.owner_stream_id = None
                shared_state.owner_capability = None
                shared_state.task_context = None
            for trigger in self.stream_triggers.values():
                trigger.case_is_recording = False
        else:
            stream_trigger.case_is_recording = False

    def _continue_recording(self, stream, parameters, stream_trigger):
        # No action
        pass

    def _continue_waiting(self, stream, parameters, stream_trigger):
        # No action
        pass

    def _get_task_context(self, stream, *, create_if_missing: bool):
        if stream is None:
            shared_state = self._get_record_all_streams_state()
            with shared_state.lock:
                if shared_state.task_context is not None:
                    return shared_state.task_context, True
                if not create_if_missing:
                    return None, True

                from highlighter.client.tasks import TaskContext

                shared_state.task_context = TaskContext()
                return shared_state.task_context, True

        stream_context = None
        if getattr(stream, "variables", None):
            stream_context = stream.variables.get("task")

        if stream_context is not None:
            return stream_context, False

        if self._shared_task_context is None:
            if not create_if_missing:
                return None, True

            from highlighter.client.tasks import TaskContext

            self._shared_task_context = TaskContext()

        return self._shared_task_context, True

    def _collect_recorders(self, stream, stream_id, parameters, *, include_all_streams=False):
        """Gather recorders for the configured capabilities.

        When `include_all_streams` is True (multi-stream case), this walks every
        active stream via the Agent recorder manager (if available) or by
        inspecting each capability's legacy `_dsps` registry. Otherwise it only
        fetches recorders for the current stream. Results are deduplicated so the
        same recorder object is never passed twice.
        """
        agent = getattr(self.pipeline, "agent", None)
        recorders: List = []

        if agent:
            if include_all_streams:
                recorders = agent.get_all_recorders_for_capabilities(parameters.case_record_capabilities)
            else:
                recorders = agent.get_recorders_for_capabilities(
                    stream_id,
                    parameters.case_record_capabilities,
                )
        else:
            targets = list(self.stream_triggers.keys()) if include_all_streams else [stream_id]
            for sid in targets:
                for name in parameters.case_record_capabilities:
                    node = self.pipeline.pipeline_graph.get_node(name)
                    if node and hasattr(node.element, "_dsps"):
                        if sid in node.element._dsps:
                            recorders.append(node.element._dsps[sid])

        return self._deduplicate_recorders(recorders)

    @staticmethod
    def _deduplicate_recorders(recorders: List) -> List:
        deduped = []
        seen = set()
        for recorder in recorders:
            marker = id(recorder)
            if marker in seen:
                continue
            seen.add(marker)
            deduped.append(recorder)
        return deduped
