from typing import Literal

# Basic Literals
AlphaNumericLiteral = Literal[
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    " ",
]

# MIR MODE_COD
StationModeLiteral = Literal["A", "C", "D", "E", "M", "P", "Q", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "]

# MIR RTST_COD
RetestConditionLiteral = Literal["Y", "N", " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# BIN_PF
BinPassFailLiteral = Literal["P", "F", " "]

# TSR TEST_TYP
TestTypeLiteral = Literal["P", "F", "M", " "]
