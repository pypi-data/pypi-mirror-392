import numpy as np
import soundfile as sf
import torch

from audiozen.acoustics.io import extract_segment


def prepare_femto_quant_batches(
    audio_fpaths: list[str],
    hop_length: int = 64,
    segment_length: int = 48000,
    target_batch_size: int = 8,
):
    """Load audio files and prepare data for quantization.

    This function takes a list of audio file paths and processes each file to create
    batches of framed audio data. The processing pipeline is as follows:
    1. Load each audio file, ensuring it is a 16kHz mono signal.
    2. Truncate or pad the audio to a fixed `segment_length` to ensure consistent input size.
    3. Apply additional padding to ensure the total length is a multiple of
        `hop_length`.
    4. Reshape the 1D audio signal into 2D frames of size `hop_length`.
    5. Group the processed audio tensors into batches of `target_batch_size`.

    Note:
        The number of files in `audio_fpath_list` must be perfectly divisible
        by `target_batch_size`.

    Args:
        audio_fpath_list: A list of paths to audio files.
        hop_length: The length of each audio frame. Defaults to 64.
        segment_length: The target length in samples to which each file will be
        truncated or padded. Defaults to 48000.
        target_batch_size: The number of audio files to group into a single batch
        tensor. Defaults to 8.

    Returns:
        list[torch.Tensor]: A list of batched tensors. Each tensor in the list has
        a shape of `(target_batch_size, num_frames, hop_length)`.

    Raises:
        AssertionError: If the number of audio files is not divisible by
            `target_batch_size`, if an audio file's sample rate is not 16000,
            or if an audio file is not mono.
    """
    num_files = len(audio_fpaths)
    assert num_files % target_batch_size == 0, (
        f"The number of audio files {len(audio_fpaths)} must be divisible by the target batch size {target_batch_size}."
    )

    quant_inputs = []

    for audio_fpath in audio_fpaths:
        # Read the audio file
        y, sr = sf.read(audio_fpath)
        assert sr == 16000, f"Sample rate must be 16000, but got {sr}"
        assert np.ndim(y) == 1, f"Audio must be mono, but got {np.ndim(y)} dimensions"

        # Pad or truncate the audio to the target length to ensure consistent input size
        y, _ = extract_segment(y, segment_length=segment_length, start_idx=0)

        y = torch.from_numpy(y).float().unsqueeze(0)
        seq_len = y.shape[1]

        # Pad the waveform to be divisible by the frame_length
        if seq_len % hop_length == 0:
            pad_amount = hop_length
        else:
            pad_amount = (hop_length - (seq_len % hop_length)) % hop_length + hop_length

        y = torch.nn.functional.pad(y, (0, pad_amount))

        # Reshape into frames
        y = y.reshape(-1, hop_length)
        quant_inputs.append(y)

    # Group the inputs into batches
    quant_inputs = torch.stack(quant_inputs, dim=0)  # e.g. (num_files, 100, 64)
    quant_inputs = quant_inputs.to("cpu")  # Move to the same device as the model
    quant_input_list = torch.chunk(
        quant_inputs, len(audio_fpaths) // target_batch_size, dim=0
    )

    return quant_input_list
