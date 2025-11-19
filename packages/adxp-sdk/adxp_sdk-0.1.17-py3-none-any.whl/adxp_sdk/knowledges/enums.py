from enum import Enum


class RetrievalMode(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"


class LoaderType(str, Enum):
    Default = "Default"
    DataIngestionTool = "DataIngestionTool"
    CustomLoader = "CustomLoader"


class SplitterType(str, Enum):
    RecursiveCharacter = "RecursiveCharacter"
    Character = "Character"
    Hybrid = "Hybrid"
    Sematic = "Semantic"
    CustomSplitter = "CustomSplitter"
    NotSplit = "NotSplit"

