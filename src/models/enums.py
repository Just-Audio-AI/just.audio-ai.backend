from enum import Enum


class FileProcessingStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    UPLOADED = "uploaded"


class FileTranscriptionStatus(Enum):
    NOT_STARTED = "not started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileRemoveMelodyStatus(Enum):
    NOT_STARTED = "not started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileRemoveNoiseStatus(Enum):
    NOT_STARTED = "not started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileRemoveVocalStatus(Enum):
    NOT_STARTED = "not started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileImproveAudioStatus(Enum):
    NOT_STARTED = "not started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
