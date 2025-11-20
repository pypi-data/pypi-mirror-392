from mindrove.board_shim import MindRoveError
from mindrove.exit_codes import MindroveExitCodes


def check_memory_layout_row_major(data, ndim):
    if data is None:
        raise MindRoveError('data is None',
                             MindroveExitCodes.EMPTY_BUFFER_ERROR.value)
    if len(data.shape) != ndim:
        raise MindRoveError('wrong shape for filter data array, it should be %dd array' % ndim,
                             MindroveExitCodes.INVALID_ARGUMENTS_ERROR.value)
    if not data.flags['C_CONTIGUOUS']:
        raise MindRoveError('wrong memory layout, should be row major, make sure you didnt tranpose array',
                             MindroveExitCodes.INVALID_ARGUMENTS_ERROR.value)
