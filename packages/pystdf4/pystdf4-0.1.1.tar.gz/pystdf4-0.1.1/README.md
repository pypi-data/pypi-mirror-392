# 📦 PyStdf4

**PyStdf4** is a modern, high-performance Python library for creating and parsing **STDF (Standard Test Data Format) v4** files, widely used in semiconductor testing and manufacturing.

It provides a clean, Pythonic interface that abstracts low-level binary handling, letting engineers focus on data modeling instead of byte-level details.

---

## 🔍 Overview

With **PyStdf4**, you can efficiently:

- Generate STDF v4 files using structured Python objects
- Build records with a robust, extensible field/record system
- Work with a high-performance dynamic byte buffer optimized for large datasets
- Integrate seamlessly into automated test and analysis pipelines

> ⚠️ STDF file **parsing (reader API)** is under active development.

---

## 🧪 Example Usage

### Installation

```bash
python -m pip install pystdf4
```

### Writing an STDF v4 file

```python
import time
from pystdf4 import Stdf4Writer

with Stdf4Writer('example.stdf') as stdf:
    # File Attributes Record
    stdf.FAR(CPU_TYPE=2, STDF_VER=4)

    # Master Information Record
    stdf.MIR(
        SETUP_T=int(time.time()),
        START_T=int(time.time()),
        STAT_NUM=0,
        BURN_TIM=0,
        LOT_ID="Example Lot",
        JOB_NAM="Example Job",
        PART_TYP="",
        NODE_NAM="",
        TSTR_TYP="",
    )

    # Add other records here...

```

---

## 📋 STDF Record Implementation Status

| Record | Type | Sub | Status        | Notes                  |
| ------ | ---- | --- | ------------- | ---------------------- |
| FAR    | 0    | 10  | ✔️ Complete   | Required first record  |
| ATR    | 0    | 20  | ✔️ Complete   | Audit trail            |
| MIR    | 1    | 10  | ✔️ Complete   | Lot-level info         |
| MRR    | 1    | 20  | ✔️ Complete   | End of lot summary     |
| PCR    | 1    | 30  | ✔️ Complete   | Part statistics        |
| HBR    | 1    | 40  | ✔️ Complete   | Physical bin counts    |
| SBR    | 1    | 50  | ✔️ Complete   | Logical bin counts     |
| PMR    | 1    | 60  | ✔️ Complete   | Pin mapping            |
| PGR    | 1    | 62  | ✔️ Complete   | Pin grouping           |
| PLR    | 1    | 63  | ✔️ Complete   | Pin display properties |
| RDR    | 1    | 70  | ✔️ Complete   | Retest info            |
| SDR    | 1    | 80  | ✔️ Complete   | Site configuration     |
| WIR    | 2    | 10  | ✔️ Complete   | Wafer start marker     |
| WRR    | 2    | 20  | ✔️ Complete   | Wafer summary          |
| WCR    | 2    | 30  | ✔️ Complete   | Wafer config           |
| PIR    | 5    | 10  | ✔️ Complete   | Part start marker      |
| PRR    | 5    | 20  | ✔️ Complete   | Part results           |
| TSR    | 10   | 30  | ✔️ Complete   | Test summary           |
| PTR    | 15   | 10  | ✔️ Complete   | Parametric test        |
| MPR    | 15   | 15  | ⚠️ Incomplete | Multiple parametric    |
| FTR    | 15   | 20  | ⚠️ Incomplete | Functional test        |
| BPS    | 20   | 10  | ✔️ Complete   | Program section start  |
| EPS    | 20   | 20  | ✔️ Complete   | Program section end    |
| GDR    | 50   | 10  | ⚠️ Incomplete | User-defined data      |
| DTR    | 50   | 30  | ✔️ Complete   | Datalog comments       |

---

## 📘 STDF v4 Data Types and Python Implementation

### STDF Type Codes

STDF defines compact type codes specifying how values are stored and interpreted in records. Below is a concise overview of commonly used types:

| Code     | Description                                   | C Type Specifier | Notes                                        |
| :------- | :-------------------------------------------- | :--------------- | :------------------------------------------- |
| `C*12`   | Fixed-length char (12 bytes)                  | `char[12]`       | Left-justified, pad with spaces              |
| `C*n`    | Variable-length char (1-byte length prefix)   | `char[]`         | Length 0–255                                 |
| `C*f`    | External-length string                        | `char[]`         | Length defined by another field              |
| `U*1`    | 1-byte unsigned integer                       | `unsigned char`  | 0–255                                        |
| `U*2`    | 2-byte unsigned integer                       | `unsigned short` | 0–65,535                                     |
| `U*4`    | 4-byte unsigned integer                       | `unsigned long`  | 0–4,294,967,295                              |
| `I*1`    | 1-byte signed integer                         | `char`           | –128 to 127                                  |
| `I*2`    | 2-byte signed integer                         | `short`          | –32,768 to 32,767                            |
| `I*4`    | 4-byte signed integer                         | `long`           | –2,147,483,648 to 2,147,483,647              |
| `R*4`    | 4-byte float (IEEE 754)                       | `float`          | Single precision                             |
| `R*8`    | 8-byte float (IEEE 754)                       | `double`         | Double precision                             |
| `B*6`    | Fixed-length binary (6 bytes)                 | `char[6]`        | Raw binary                                   |
| `V*n`    | Variable-type field                           | —                | First byte = type code, up to 255 bytes data |
| `B*n`    | Variable-length binary (1-byte length prefix) | `char[]`         | Data starts at second byte                   |
| `D*n`    | Variable-length bit field                     | `char[]`         | First two bytes = bit count; padding zeros   |
| `N*1`    | Nibble array (4-bit units)                    | `char`           | High nibble zeroed if odd count              |
| `kxTYPE` | Array of specified type                       | `TYPE[]`         | Length determined by another field           |

_For full STDF v4 type reference, see `pystdf4/doc/stdf-spec.pdf`._

### Python Implementation

PyStdf4 uses a hierarchy of classes to represent STDF fields and records, with each class implementing a specific type of field or record. The hierarchy is as follows:

```

FieldBase(pyT) (ABC)
├── ImmediateField(pyT)
│   ├── C_1, C_12, B_1, B_6
│   ├── C_n, B_n, C_f
│   └── D_n, N_1 [⚠️ Not Implemented Yet]
│
├── DeferredField(pyT)
│   ├── U_1, U_2, U_4
│   ├── I_1, I_2, I_4
│   └── R_4, R_8
│
├── VariableField
│   └── V_n [⚠️ Not Implemented Yet]
│
└── ArrayField
    ├── kxU_1, kxU_2, kxC_n
    └── kxN_1 [⚠️ Not Implemented Yet]

```

These classes handle type conversion, byte parsing, and STDF serialization, ensuring consistency between Python objects and STDF binary data.

---

## 🗺️ Roadmap

| Version  | Goals                                                                                                                            |
| -------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **v0.x** | ✅ Core STDF types & common records<br>⬜ Fully functional `StdfWriter`<br>⬜ Robust Pythonic writing API                        |
| **v1.x** | ⬜ SmartWriter (auto record creation)<br>⬜ High-level APIs for stats & aggregation<br>⬜ Intelligent record dependency handling |
| **v2.x** | ⬜ `StdfReader` (efficient parsing)<br>⬜ Integration with analysis pipelines<br>⬜ Full read/write compatibility                |

---

## 📜 License

MIT © 2025 — Developed for efficient and reliable STDF data manipulation in modern semiconductor workflows.
