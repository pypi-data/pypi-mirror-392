import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema import Event as Event
from gllm_inference.schema.lm_output import LMOutput as LMOutput

class BaseOutputTransformer(ABC, metaclass=abc.ABCMeta):
    """A base class for output transformers used in Gen AI applications.

    The `BaseOutputTransformer` class defines the interface for transforming the output of language models.
    Subclasses must implement the following methods:
    1. `transform`: Transforms the output of a language model.
    2. `_transform_event`: Transforms a stream event of a language model before it is emitted.

    Attributes:
        event_emitter (EventEmitter | None): The event emitter to use for streaming events.
    """
    event_emitter: Incomplete
    def __init__(self, event_emitter: EventEmitter | None = None) -> None:
        """Initializes a new instance of the BaseOutputTransformer class.

        Args:
            event_emitter (EventEmitter | None, optional): The event emitter to use for streaming events.
                Defaults to None.
        """
    @abstractmethod
    def transform(self, output: LMOutput) -> LMOutput:
        """Transforms the output of a language model.

        This abstract method must be implemented by subclasses to define how the output is transformed.

        Args:
            output (LMOutput): The output of a language model.

        Returns:
            LMOutput: The transformed output of a language model.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
    async def emit(self, event: Event) -> None:
        """Transforms a stream event and emits it using the event emitter.

        This method transforms a stream event and emits it using the event emitter.

        Args:
            event (Event): The event to transform and emit.

        Raises:
            ValueError: If the event emitter is not set.
        """
