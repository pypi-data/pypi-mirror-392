from gllm_core.schema import Event as Event
from gllm_inference.output_transformer.output_transformer import BaseOutputTransformer as BaseOutputTransformer
from gllm_inference.schema.lm_output import LMOutput as LMOutput

class IdentityOutputTransformer(BaseOutputTransformer):
    """An output transformer that transforms the output of a language model into an identity function.

    This transformer simply returns the output and stream events of the language model as is.
    """
    def transform(self, output: LMOutput) -> LMOutput:
        """Transforms the output of a language model with an identity function.

        This method simply returns the output and stream events of the language model as is.

        Args:
            output (LMOutput): The output of a language model.
        """
