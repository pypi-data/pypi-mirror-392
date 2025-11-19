from typing import TextIO


def _report_errors(errors, buffer: TextIO):
    if buffer is None or not errors:
        return
    errors.append("")  # So \n is added at the end of the last line
    buffer.writelines("\n".join(errors))
