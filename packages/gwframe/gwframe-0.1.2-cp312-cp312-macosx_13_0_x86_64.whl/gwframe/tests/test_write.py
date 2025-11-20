"""Comprehensive tests for gwframe write functionality."""

import numpy as np
import pytest

import gwframe


class TestSimpleWrite:
    """Tests for simple write operations using gwframe.write()."""

    def test_write_basic(self, tmp_path):
        """Test basic write and read-back."""
        tmp_file = tmp_path / "test.gwf"

        # Create test data
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        original_data = np.sin(np.linspace(0, 2 * np.pi, n_samples))

        # Write frame
        gwframe.write(
            str(tmp_file),
            original_data,
            t0=t0,
            sample_rate=sample_rate,
            name="L1:TEST",
            unit="strain",
        )

        # Read back
        result = gwframe.read(str(tmp_file), "L1:TEST")

        # Verify
        assert np.allclose(original_data, result.array)
        assert result.sample_rate == sample_rate
        assert result.t0 == t0
        assert result.name == "L1:TEST"
        assert result.unit == "strain"

    def test_write_with_compression(self, tmp_path):
        """Test writing with GZIP compression."""
        tmp_file = tmp_path / "test_compressed.gwf"

        # Create test data
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        original_data = np.sin(np.linspace(0, 2 * np.pi, n_samples))

        # Write with compression
        gwframe.write(
            str(tmp_file),
            original_data,
            t0=t0,
            sample_rate=sample_rate,
            name="L1:TEST",
            unit="strain",
            compression=gwframe.Compression.GZIP,
        )

        # Read back
        result = gwframe.read(str(tmp_file), "L1:TEST")

        # Verify data integrity after compression
        assert np.allclose(original_data, result.array)
        assert result.sample_rate == sample_rate


class TestFrameWriter:
    """Tests for FrameWriter context manager."""

    def test_write_multiple_frames(self, tmp_path):
        """Test writing multiple frames to a single file."""
        tmp_file = tmp_path / "multiframe.gwf"
        n_frames = 5
        sample_rate = 1000.0
        n_samples = 1000
        t0_base = 1234567890.0

        # Write multiple frames
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            for i in range(n_frames):
                data = np.full(n_samples, float(i))
                writer.write(
                    data,
                    t0=t0_base + i,
                    sample_rate=sample_rate,
                    name="L1:TEST",
                    unit="counts",
                )

        # Read back each frame
        for i in range(n_frames):
            result = gwframe.read(str(tmp_file), "L1:TEST", frame_index=i)
            assert np.all(result.array == float(i))
            assert result.t0 == t0_base + i

    def test_framewriter_with_compression(self, tmp_path):
        """Test FrameWriter with compression."""
        tmp_file = tmp_path / "compressed_multi.gwf"

        with gwframe.FrameWriter(
            str(tmp_file), compression=gwframe.Compression.GZIP
        ) as writer:
            for i in range(3):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="strain",
                )

        # Verify all frames can be read back
        for i in range(3):
            result = gwframe.read(str(tmp_file), "L1:TEST", frame_index=i)
            assert len(result.array) == 1000

    def test_framewriter_multiple_channels(self, tmp_path):
        """Test writing multiple channels per frame."""
        tmp_file = tmp_path / "multichannel.gwf"

        with gwframe.FrameWriter(str(tmp_file)) as writer:
            # Create frame with multiple channels
            data1 = np.random.randn(1000)
            data2 = np.random.randn(500)

            # Write using manual Frame object
            frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
            frame.add_channel("L1:STRAIN", data1, sample_rate=1000, unit="strain")
            frame.add_channel("L1:AUX", data2, sample_rate=500, unit="counts")
            writer.write_frame(frame)

        # Read back both channels
        strain = gwframe.read(str(tmp_file), "L1:STRAIN")
        aux = gwframe.read(str(tmp_file), "L1:AUX")

        assert len(strain.array) == 1000
        assert len(aux.array) == 500
        assert strain.sample_rate == 1000.0
        assert aux.sample_rate == 500.0


class TestFrameNumber:
    """Tests for frame number tracking and auto-increment."""

    def test_explicit_frame_number(self):
        """Test creating frame with explicit frame_number."""
        frame = gwframe.Frame(
            t0=1234567890.0, duration=1.0, name="L1", run=1, frame_number=42
        )

        assert frame.frame_number == 42

    def test_default_frame_number(self):
        """Test default frame_number is 0."""
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)

        assert frame.frame_number == 0

    def test_framewriter_auto_increment(self, tmp_path):
        """Test FrameWriter auto-increments frame numbers."""
        tmp_file = tmp_path / "auto_increment.gwf"
        initial_frame_number = 10
        n_frames = 5

        with gwframe.FrameWriter(
            str(tmp_file), frame_number=initial_frame_number
        ) as writer:
            # Initial frame number should be set
            assert writer._frame_number == initial_frame_number

            # Write multiple frames
            for i in range(n_frames):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="counts",
                )
                # Frame number should increment after each write
                expected_frame_num = initial_frame_number + i + 1
                assert writer._frame_number == expected_frame_num

        # Verify frames were written (can't easily check frame numbers in file)
        for i in range(n_frames):
            result = gwframe.read(str(tmp_file), "L1:TEST", frame_index=i)
            assert len(result.array) == 1000

    def test_manual_frame_objects_with_framewriter(self, tmp_path):
        """Test writing manual Frame objects with specific frame numbers."""
        tmp_file = tmp_path / "manual_frames.gwf"

        with gwframe.FrameWriter(str(tmp_file), frame_number=100) as writer:
            for i in range(3):
                # Create frame with explicit frame number
                frame = gwframe.Frame(
                    t0=1234567890.0 + i,
                    duration=1.0,
                    name="L1",
                    run=1,
                    frame_number=100 + i,
                )
                data = np.random.randn(1000)
                frame.add_channel("L1:TEST", data, sample_rate=1000, unit="strain")

                writer.write_frame(frame)

        # Verify all frames were written
        for i in range(3):
            result = gwframe.read(str(tmp_file), "L1:TEST", frame_index=i)
            assert len(result.array) == 1000


class TestCompression:
    """Tests for compression modes and settings."""

    def test_compression_modes_exposed(self):
        """Test that all compression modes are exposed."""
        required_modes = [
            "RAW",
            "GZIP",
            "DIFF_GZIP",
            "ZERO_SUPPRESS_WORD_2",
            "ZERO_SUPPRESS_WORD_4",
            "ZERO_SUPPRESS_WORD_8",
            "ZERO_SUPPRESS_OTHERWISE_GZIP",
            "BEST_COMPRESSION",
            # Aliases
            "ZERO_SUPPRESS_SHORT",
            "ZERO_SUPPRESS_INT_FLOAT",
        ]

        for mode in required_modes:
            assert hasattr(gwframe.Compression, mode), f"Missing mode: {mode}"
            value = getattr(gwframe.Compression, mode)
            assert isinstance(value, int), f"Mode {mode} is not an integer"

    def test_write_with_different_compressions(self, tmp_path):
        """Test writing with different compression modes."""
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        original_data = np.random.randn(n_samples)

        compression_modes = [
            ("raw", gwframe.Compression.RAW),
            ("gzip", gwframe.Compression.GZIP),
            ("diff_gzip", gwframe.Compression.DIFF_GZIP),
        ]

        for name, compression in compression_modes:
            tmp_file = tmp_path / f"test_{name}.gwf"

            # Write with specific compression
            gwframe.write(
                str(tmp_file),
                original_data,
                t0=t0,
                sample_rate=sample_rate,
                name="L1:TEST",
                unit="strain",
                compression=compression,
            )

            # Read back and verify
            result = gwframe.read(str(tmp_file), "L1:TEST")
            assert np.allclose(original_data, result.array)

    def test_compression_level(self, tmp_path):
        """Test compression with different compression levels."""
        tmp_file = tmp_path / "test_level.gwf"
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        original_data = np.random.randn(n_samples)

        # Write with GZIP compression level 9
        frame = gwframe.Frame(t0=t0, duration=1.0, name="L1", run=1)
        frame.add_channel(
            "L1:TEST", original_data, sample_rate=sample_rate, unit="strain"
        )
        frame.write(str(tmp_file), compression=gwframe.Compression.GZIP)

        # Read back and verify
        result = gwframe.read(str(tmp_file), "L1:TEST")
        assert np.allclose(original_data, result.array)


class TestFrameMetadata:
    """Tests for frame metadata (detector, run, etc.)."""

    def test_frame_with_full_metadata(self, tmp_path):
        """Test creating frame with all metadata fields."""
        tmp_file = tmp_path / "metadata.gwf"

        frame = gwframe.Frame(
            t0=1234567890.0,
            duration=1.0,
            name="L1",
            run=42,
            frame_number=100,
        )

        data = np.random.randn(1000)
        frame.add_channel(
            "L1:TEST",
            data,
            sample_rate=1000,
            unit="strain",
            channel_type="proc",
        )

        # Add history
        frame.add_history("gwframe", "Test frame created by gwframe")

        frame.write(str(tmp_file))

        # Read back and verify
        result = gwframe.read(str(tmp_file), "L1:TEST")
        assert len(result.array) == 1000
        assert result.t0 == 1234567890.0

    def test_frame_without_detector(self, tmp_path):
        """Test creating frame without detector name."""
        tmp_file = tmp_path / "no_detector.gwf"

        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="TEST", run=1)

        data = np.random.randn(1000)
        frame.add_channel("TEST:CHANNEL", data, sample_rate=1000, unit="counts")

        frame.write(str(tmp_file))

        # Read back
        result = gwframe.read(str(tmp_file), "TEST:CHANNEL")
        assert len(result.array) == 1000


def test_framewriter_error_when_not_opened(tmp_path):
    """Test that FrameWriter raises error if used outside context manager."""
    tmp_file = tmp_path / "test.gwf"
    writer = gwframe.FrameWriter(str(tmp_file))

    # Should raise error when not in 'with' block
    with pytest.raises(RuntimeError, match="not opened"):
        writer.write(
            np.random.randn(100),
            t0=1234567890.0,
            sample_rate=100,
            name="L1:TEST",
        )


def test_write_frame_without_context(tmp_path):
    """Test write_frame raises error outside context manager."""
    tmp_file = tmp_path / "test.gwf"
    writer = gwframe.FrameWriter(str(tmp_file))
    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")

    with pytest.raises(RuntimeError, match="not opened"):
        writer.write_frame(frame)


def test_write_single_array_without_name_raises_error(tmp_path):
    """Test that writing single array without name parameter raises error."""
    tmp_file = tmp_path / "test.gwf"
    data = np.random.randn(1000)

    with pytest.raises(ValueError, match="name parameter required"):
        gwframe.write(
            str(tmp_file),
            data,  # Single array
            t0=1234567890.0,
            sample_rate=1000,
            # Missing name parameter
        )


def test_framewriter_write_single_array_without_name(tmp_path):
    """Test FrameWriter.write() with single array but no name raises error."""
    tmp_file = tmp_path / "test.gwf"

    with (
        gwframe.FrameWriter(str(tmp_file)) as writer,
        pytest.raises(ValueError, match="name parameter required"),
    ):
        writer.write(
            np.random.randn(1000),
            t0=1234567890.0,
            sample_rate=1000,
            # Missing name parameter
        )


def test_add_channel_wrong_dimensions(tmp_path):
    """Test that adding non-1D data raises error."""
    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")

    # 2D array should raise error
    data_2d = np.random.randn(10, 10)
    with pytest.raises(ValueError, match="must be 1D array"):
        frame.add_channel("L1:TEST", data_2d, sample_rate=1000)


def test_unsupported_channel_type():
    """Test that unsupported channel_type raises error."""
    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")
    data = np.random.randn(1000)

    with pytest.raises(ValueError, match="Unsupported channel_type"):
        frame.add_channel(
            "L1:TEST",
            data,
            sample_rate=1000,
            channel_type="invalid_type",
        )


class TestWriteBytes:
    """Tests for write_bytes functionality."""

    def test_write_bytes_basic_roundtrip(self):
        """Test basic round-trip: write_bytes -> read_bytes."""
        # Create test data
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        original_data = np.sin(np.linspace(0, 2 * np.pi, n_samples))

        # Write to bytes
        gwf_bytes = gwframe.write_bytes(
            original_data,
            t0=t0,
            sample_rate=sample_rate,
            name="L1:TEST",
            unit="strain",
        )

        # Verify we got bytes
        assert isinstance(gwf_bytes, bytes)
        assert len(gwf_bytes) > 0

        # Read back from bytes
        result = gwframe.read_bytes(gwf_bytes, "L1:TEST")

        # Verify data integrity
        np.testing.assert_array_equal(original_data, result.array)
        assert result.sample_rate == sample_rate
        assert result.t0 == t0
        assert result.name == "L1:TEST"
        assert result.unit == "strain"

    def test_write_bytes_equals_write_file(self, tmp_path):
        """Test that write_bytes produces identical output to write."""
        tmp_file = tmp_path / "test.gwf"

        # Create test data
        n_samples = 1000
        sample_rate = 1000.0
        t0 = 1234567890.0
        data = np.sin(np.linspace(0, 2 * np.pi, n_samples))

        # Write to file
        gwframe.write(
            str(tmp_file),
            data,
            t0=t0,
            sample_rate=sample_rate,
            name="L1:TEST",
        )

        # Write to bytes with same parameters
        gwf_bytes = gwframe.write_bytes(
            data,
            t0=t0,
            sample_rate=sample_rate,
            name="L1:TEST",
        )

        # Read file bytes
        with open(tmp_file, "rb") as f:
            file_bytes = f.read()

        # Compare
        assert gwf_bytes == file_bytes

    def test_frame_write_bytes_roundtrip(self):
        """Test Frame.write_bytes() method."""
        # Create frame
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")
        data = np.random.randn(16384)
        frame.add_channel("L1:TEST", data, sample_rate=16384)

        # Write to bytes
        gwf_bytes = frame.write_bytes()

        # Verify we got bytes
        assert isinstance(gwf_bytes, bytes)
        assert len(gwf_bytes) > 0

        # Read back
        result = gwframe.read_bytes(gwf_bytes, "L1:TEST")

        # Verify
        np.testing.assert_array_equal(data, result.array)
        assert result.sample_rate == 16384
        assert result.t0 == 1234567890.0

    def test_write_bytes_with_compression(self):
        """Test write_bytes with different compression schemes."""
        data = np.random.randn(1000)
        t0 = 1234567890.0

        # Test with no compression
        bytes_raw = gwframe.write_bytes(
            data,
            t0=t0,
            sample_rate=1000,
            name="L1:TEST",
            compression=gwframe.Compression.RAW,
        )

        # Test with gzip compression
        bytes_gzip = gwframe.write_bytes(
            data,
            t0=t0,
            sample_rate=1000,
            name="L1:TEST",
            compression=gwframe.Compression.GZIP,
            compression_level=9,
        )

        # Verify both are valid
        result_raw = gwframe.read_bytes(bytes_raw, "L1:TEST")
        result_gzip = gwframe.read_bytes(bytes_gzip, "L1:TEST")

        np.testing.assert_array_equal(data, result_raw.array)
        np.testing.assert_array_equal(data, result_gzip.array)

        # Compressed should be smaller (for random data with high compression)
        assert len(bytes_gzip) < len(bytes_raw)

    def test_frame_writer_bytesio(self):
        """Test FrameWriter with BytesIO destination."""
        from io import BytesIO

        buffer = BytesIO()

        # Write multiple frames to BytesIO
        with gwframe.FrameWriter(buffer) as writer:
            for i in range(5):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                )

        # Get bytes
        gwf_bytes = buffer.getvalue()

        # Verify we can read all 5 frames
        for i in range(5):
            result = gwframe.read_bytes(gwf_bytes, "L1:TEST", frame_index=i)
            assert len(result.array) == 1000
            assert result.t0 == 1234567890.0 + i

    def test_frame_writer_bytesio_equals_file(self, tmp_path):
        """Test that FrameWriter produces identical output for file and BytesIO."""
        from io import BytesIO

        tmp_file = tmp_path / "test.gwf"

        # Generate test data
        frames_data = [np.random.randn(1000) for _ in range(3)]

        # Write to file
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            for i, data in enumerate(frames_data):
                writer.write(
                    data, t0=1234567890.0 + i, sample_rate=1000, name="L1:TEST"
                )

        # Write to BytesIO
        buffer = BytesIO()
        with gwframe.FrameWriter(buffer) as writer:
            for i, data in enumerate(frames_data):
                writer.write(
                    data, t0=1234567890.0 + i, sample_rate=1000, name="L1:TEST"
                )

        # Compare bytes
        with open(tmp_file, "rb") as f:
            file_bytes = f.read()

        buffer_bytes = buffer.getvalue()

        assert file_bytes == buffer_bytes

    def test_write_bytes_multiple_channels(self):
        """Test write_bytes with multiple channels."""
        # Create test data
        data1 = np.random.randn(1000)
        data2 = np.random.randn(1000)
        channels = {"L1:CHAN1": data1, "L1:CHAN2": data2}

        # Write to bytes
        gwf_bytes = gwframe.write_bytes(
            channels,
            t0=1234567890.0,
            sample_rate=1000,
            name="L1",
        )

        # Read back
        result = gwframe.read_bytes(gwf_bytes, channel=None)

        # Verify both channels
        assert "L1:CHAN1" in result
        assert "L1:CHAN2" in result
        np.testing.assert_array_equal(data1, result["L1:CHAN1"].array)
        np.testing.assert_array_equal(data2, result["L1:CHAN2"].array)
