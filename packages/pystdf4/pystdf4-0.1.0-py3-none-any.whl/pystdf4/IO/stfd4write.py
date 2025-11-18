from typing import Any, Callable, Literal, Optional, Sequence, Tuple

from .base import StdfIOBase


class Stfd4Writer(StdfIOBase):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def to_bytes(self) -> bytes:
        self.write_buffers()
        return self.buffer.to_bytes()

    def write_fields(self, rec_typ: int, rec_sub: int, field_writer: Callable):
        # Step 1: Write the header of the record
        record_start = self._write_header((rec_typ, rec_sub))

        # Step 2: Write the fields of the record
        field_writer(self)

        # Step 3: Update the length of the record
        record_end = self.buffer.offset
        record_length = record_end - (record_start + 4)
        self.buffer._mv[record_start : record_start + 2] = record_length.to_bytes(2, byteorder="little")

    def _write_header(self, header: Tuple[int, int]) -> int:
        """
        Write the header of a record to the file.
        """
        packer_size = self.header_packer.size
        self.buffer._ensure_capacity(packer_size)
        start = self.buffer.offset
        self.header_packer.pack_into(self.buffer._mv, start, 0, *header)
        self.buffer.offset += packer_size
        return start

    def write_buffers(self):
        for scalar_field in (self.U_1, self.U_2, self.U_4, self.I_1, self.I_2, self.I_4, self.R_4, self.R_8):
            scalar_field.flush_cache_to_buffer(self.buffer)

    def ATR(self, MOD_TIM: int, CMD_LINE: str):
        """Audit Trail Record"""

        # Implementation here
        def write_fields(self):
            self.U_4.pack_into(self.buffer, MOD_TIM)
            self.C_n.pack_into(self.buffer, CMD_LINE)

        self.write_fields(0, 20, write_fields)

    def BPS(self, SEQ_NAME: str = ""):
        """Begin Program Section Record"""
        # Implementation here
        pass

    def DTR(self, TEXT_DAT: str):
        """Datalog Text Record"""
        # Implementation here
        pass

    def EPS(self):
        """End Program Section Record"""
        # Implementation here
        pass

    def FAR(self, CPU_TYPE: int, STDF_VER: int):
        """File Attributes Record"""

        # Implementation here
        def write_fields(self):
            self.U_1.pack_into(self.buffer, CPU_TYPE)
            self.U_1.pack_into(self.buffer, STDF_VER)

        self.write_fields(0, 10, write_fields)

    def FTR(
        self,
        TEST_NUM: int,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_FLG: bytes,
        OPT_FLAG: bytes,
        RTN_ICNT: int,
        PGM_ICNT: int,
        CYCL_CNT: int = 0,
        REL_VADR: int = 0,
        REPT_CNT: int = 0,
        NUM_FAIL: int = 0,
        XFAIL_AD: int = 0,
        YFAIL_AD: int = 0,
        VECT_OFF: int = 0,
        RTN_INDX: Optional[Sequence[int]] = None,
        RTN_STAT: Optional[Sequence[bytes]] = None,
        PGM_INDX: Optional[Sequence[int]] = None,
        PGM_STAT: Optional[Sequence[bytes]] = None,
        FAIL_PIN: bytes = b"",
        VECT_NAM: str = "",
        TIME_SET: str = "",
        OP_CODE: str = "",
        TEST_TXT: str = "",
        ALARM_ID: str = "",
        PROG_TXT: str = "",
        RSLT_TXT: str = "",
        PATG_NUM: int = 255,
        SPIN_MAP: bytes = b"",
    ):
        """Functional Test Record"""
        # Implementation here
        pass

    def GDR(self, FLD_CNT: int, GEN_DATA: Any):
        """Generic Data Record"""
        # Implementation here
        pass

    def HBR(
        self,
        SITE_NUM: int,
        HBIN_NUM: int,
        HBIN_CNT: int,
        HEAD_NUM: int = 255,
        HBIN_PF: Literal["P", "F", " "] = " ",
        HBIN_NAM: str = "",
    ):
        """Hardware Bin Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)
            self.U_2.pack_into(self.buffer, HBIN_NUM)
            self.U_4.pack_into(self.buffer, HBIN_CNT)
            self.C_1.pack_into(self.buffer, HBIN_PF)
            self.C_n.pack_into(self.buffer, HBIN_NAM)

        self.write_fields(1, 40, write_fields)

    def MIR(
        self,
        SETUP_T: int,
        START_T: int,
        STAT_NUM: int,
        LOT_ID: str,
        PART_TYP: str,
        NODE_NAM: str,
        TSTR_TYP: str,
        JOB_NAM: str,
        MODE_COD: Literal[
            "A",
            "C",
            "D",
            "E",
            "M",
            "P",
            "Q",
            "0",
            "1",
            "2",
            # Implementation here
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            " ",
        ] = " ",
        RTST_COD: Literal["Y", "N", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "] = " ",
        PROT_COD: str = " ",
        BURN_TIM: int = 65535,
        CMOD_COD: str = " ",
        JOB_REV: str = "",
        SBLOT_ID: str = "",
        OPER_NAM: str = "",
        EXEC_TYP: str = "",
        EXEC_VER: str = "",
        TEST_COD: str = "",
        TST_TEMP: str = "",
        USER_TXT: str = "",
        AUX_FILE: str = "",
        PKG_TYP: str = "",
        FAMLY_ID: str = "",
        DATE_COD: str = "",
        FACIL_ID: str = "",
        FLOOR_ID: str = "",
        PROC_ID: str = "",
        OPER_FRQ: str = "",
        SPEC_NAM: str = "",
        SPEC_VER: str = "",
        FLOW_ID: str = "",
        SETUP_ID: str = "",
        DSGN_REV: str = "",
        ENG_ID: str = "",
        ROM_COD: str = "",
        SERL_NUM: str = "",
        SUPR_NAM: str = "",
    ):
        """Master Information Record"""
        # Implementation here

        def write_fields(self):
            self.U_4.pack_into(self.buffer, SETUP_T)
            self.U_4.pack_into(self.buffer, START_T)
            self.U_1.pack_into(self.buffer, STAT_NUM)
            self.C_1.pack_into(self.buffer, MODE_COD)
            self.C_1.pack_into(self.buffer, RTST_COD)
            self.C_1.pack_into(self.buffer, PROT_COD)
            self.U_2.pack_into(self.buffer, BURN_TIM)
            self.C_1.pack_into(self.buffer, CMOD_COD)
            self.C_n.pack_into(self.buffer, LOT_ID)
            self.C_n.pack_into(self.buffer, PART_TYP)
            self.C_n.pack_into(self.buffer, NODE_NAM)
            self.C_n.pack_into(self.buffer, TSTR_TYP)
            self.C_n.pack_into(self.buffer, JOB_NAM)
            self.C_n.pack_into(self.buffer, JOB_REV)
            self.C_n.pack_into(self.buffer, SBLOT_ID)
            self.C_n.pack_into(self.buffer, OPER_NAM)
            self.C_n.pack_into(self.buffer, EXEC_TYP)
            self.C_n.pack_into(self.buffer, EXEC_VER)
            self.C_n.pack_into(self.buffer, TEST_COD)
            self.C_n.pack_into(self.buffer, TST_TEMP)
            self.C_n.pack_into(self.buffer, USER_TXT)
            self.C_n.pack_into(self.buffer, AUX_FILE)
            self.C_n.pack_into(self.buffer, PKG_TYP)
            self.C_n.pack_into(self.buffer, FAMLY_ID)
            self.C_n.pack_into(self.buffer, DATE_COD)
            self.C_n.pack_into(self.buffer, FACIL_ID)
            self.C_n.pack_into(self.buffer, FLOOR_ID)
            self.C_n.pack_into(self.buffer, PROC_ID)
            self.C_n.pack_into(self.buffer, OPER_FRQ)
            self.C_n.pack_into(self.buffer, SPEC_NAM)
            self.C_n.pack_into(self.buffer, SPEC_VER)
            self.C_n.pack_into(self.buffer, FLOW_ID)
            self.C_n.pack_into(self.buffer, SETUP_ID)
            self.C_n.pack_into(self.buffer, DSGN_REV)
            self.C_n.pack_into(self.buffer, ENG_ID)
            self.C_n.pack_into(self.buffer, ROM_COD)
            self.C_n.pack_into(self.buffer, SERL_NUM)
            self.C_n.pack_into(self.buffer, SUPR_NAM)

        self.write_fields(1, 10, write_fields)

    def MPR(
        self,
        TEST_NUM: int,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_FLG: bytes,
        PARM_FLG: bytes,
        RTN_ICNT: int,
        RSLT_CNT: int,
        OPT_FLAG: bytes,
        RTN_STAT: Optional[Sequence[bytes]] = None,
        RTN_RSLT: Optional[Sequence[float]] = None,
        TEST_TXT: str = "",
        ALARM_ID: str = "",
        RES_SCAL: int = 0,
        LLM_SCAL: int = 0,
        HLM_SCAL: int = 0,
        LO_LIMIT: float = 0.0,
        HI_LIMIT: float = 0.0,
        START_IN: float = 0.0,
        INCR_IN: float = 0.0,
        RTN_INDX: Optional[Sequence[int]] = None,
        UNITS: str = "",
        UNITS_IN: str = "",
        C_RESFMT: str = "",
        C_LLMFMT: str = "",
        C_HLMFMT: str = "",
        LO_SPEC: float = 0.0,
        HI_SPEC: float = 0.0,
    ):
        """Multiple-Result Parametric Record"""
        # Implementation here

    def MRR(
        self,
        FINISH_T: int,
        DISP_COD: str = " ",
        USR_DESC: str = "",
        EXC_DESC: str = "",
    ):
        """Master Results Record"""
        # Implementation here

        def write_fields(self):
            self.U_4.pack_into(self.buffer, FINISH_T)
            self.C_1.pack_into(self.buffer, DISP_COD)
            self.C_n.pack_into(self.buffer, USR_DESC)
            self.C_n.pack_into(self.buffer, EXC_DESC)

        self.write_fields(1, 20, write_fields)

    def PCR(
        self,
        SITE_NUM: int,
        PART_CNT: int,
        HEAD_NUM: int = 255,
        RTST_CNT: int = 4294967295,
        ABRT_CNT: int = 4294967295,
        GOOD_CNT: int = 4294967295,
        FUNC_CNT: int = 4294967295,
    ):
        """Part Count Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)
            self.U_4.pack_into(self.buffer, PART_CNT)
            self.U_4.pack_into(self.buffer, RTST_CNT)
            self.U_4.pack_into(self.buffer, ABRT_CNT)
            self.U_4.pack_into(self.buffer, GOOD_CNT)
            self.U_4.pack_into(self.buffer, FUNC_CNT)

        self.write_fields(1, 30, write_fields)

    def PGR(
        self,
        GRP_INDX: int,
        INDX_CNT: int,
        PMR_INDX: Optional[Sequence[int]] = None,
        GRP_NAM: str = "",
    ):
        """Pin Group Record"""
        # Implementation here
        pass

    def PIR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
    ):
        """Part Information Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)

        self.write_fields(5, 10, write_fields)

    def PLR(
        self,
        GRP_CNT: int,
        GRP_INDX: Optional[Sequence[int]] = None,
        GRP_MODE: Optional[Sequence[int]] = None,
        GRP_RADX: Optional[Sequence[int]] = None,
        PGM_CHAR: Optional[Sequence[str]] = None,
        RTN_CHAR: Optional[Sequence[str]] = None,
        PGM_CHAL: Optional[Sequence[str]] = None,
        RTN_CHAL: Optional[Sequence[str]] = None,
    ):
        """Pin List Record"""
        # Implementation here
        pass

    def PMR(
        self,
        PMR_INDX: int,
        CHAN_TYP: int = 0,
        CHAN_NAM: str = "",
        PHY_NAM: str = "",
        LOG_NAM: str = "",
        HEAD_NUM: int = 1,
        SITE_NUM: int = 1,
    ):
        """Pin Map Record"""
        # Implementation here
        pass

    def PRR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        PART_FLG: bytes,
        NUM_TEST: int,
        HARD_BIN: int,
        SOFT_BIN: int = 65535,
        X_COORD: int = -32768,
        Y_COORD: int = -32768,
        TEST_T: int = 0,
        PART_ID: str = "",
        PART_TXT: str = "",
        PART_FIX: bytes = b"",
    ):
        """Part Results Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)
            self.B_1.pack_into(self.buffer, PART_FLG)
            self.U_2.pack_into(self.buffer, NUM_TEST)
            self.U_2.pack_into(self.buffer, HARD_BIN)
            self.U_2.pack_into(self.buffer, SOFT_BIN)
            self.I_2.pack_into(self.buffer, X_COORD)
            self.I_2.pack_into(self.buffer, Y_COORD)
            self.U_4.pack_into(self.buffer, TEST_T)
            self.C_n.pack_into(self.buffer, PART_ID)
            self.C_n.pack_into(self.buffer, PART_TXT)
            self.B_n.pack_into(self.buffer, PART_FIX)

        self.write_fields(5, 20, write_fields)

    def PTR(
        self,
        TEST_NUM: int,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_FLG: bytes,
        PARM_FLG: bytes,
        OPT_FLAG: bytes,
        RESULT: float = 0.0,
        TEST_TXT: str = "",
        ALARM_ID: str = "",
        RES_SCAL: int = 0,
        LLM_SCAL: int = 0,
        HLM_SCAL: int = 0,
        LO_LIMIT: float = 0.0,
        HI_LIMIT: float = 0.0,
        UNITS: str = "",
        C_RESFMT: str = "",
        C_LLMFMT: str = "",
        C_HLMFMT: str = "",
        LO_SPEC: float = 0.0,
        HI_SPEC: float = 0.0,
    ):
        """Parametric Test Record"""

        def write_fields(self):
            self.U_4.pack_into(self.buffer, TEST_NUM)
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)
            self.B_1.pack_into(self.buffer, TEST_FLG)
            self.B_1.pack_into(self.buffer, PARM_FLG)
            self.R_4.pack_into(self.buffer, RESULT)
            self.C_n.pack_into(self.buffer, TEST_TXT)
            self.C_n.pack_into(self.buffer, ALARM_ID)
            self.B_1.pack_into(self.buffer, OPT_FLAG)
            self.I_1.pack_into(self.buffer, RES_SCAL)
            self.I_1.pack_into(self.buffer, LLM_SCAL)
            self.I_1.pack_into(self.buffer, HLM_SCAL)
            self.R_4.pack_into(self.buffer, LO_LIMIT)
            self.R_4.pack_into(self.buffer, HI_LIMIT)
            self.C_n.pack_into(self.buffer, UNITS)
            self.C_n.pack_into(self.buffer, C_RESFMT)
            self.C_n.pack_into(self.buffer, C_LLMFMT)
            self.C_n.pack_into(self.buffer, C_HLMFMT)
            self.R_4.pack_into(self.buffer, LO_SPEC)
            self.R_4.pack_into(self.buffer, HI_SPEC)

        self.write_fields(15, 10, write_fields)

    def RDR(self, NUM_BINS: int, RTST_BIN: Optional[Sequence[int]] = None):
        """Retest Data Record"""
        # Implementation here
        pass

    def SBR(
        self,
        SITE_NUM: int,
        SBIN_NUM: int,
        SBIN_CNT: int,
        HEAD_NUM: int = 255,
        SBIN_PF: Literal["P", "F", " "] = " ",
        SBIN_NAM: str = "",
    ):
        """Software Bin Record"""
        # Implementation here
        pass

    def SDR(
        self,
        HEAD_NUM: int,
        SITE_GRP: int,
        SITE_CNT: int,
        SITE_NUM: Optional[Sequence[int]] = None,
        HAND_TYP: str = "",
        HAND_ID: str = "",
        CARD_TYP: str = "",
        CARD_ID: str = "",
        LOAD_TYP: str = "",
        LOAD_ID: str = "",
        DIB_TYP: str = "",
        DIB_ID: str = "",
        CABL_TYP: str = "",
        CABL_ID: str = "",
        CONT_TYP: str = "",
        CONT_ID: str = "",
        LASR_TYP: str = "",
        LASR_ID: str = "",
        EXTR_TYP: str = "",
        EXTR_ID: str = "",
    ):
        """Site Description Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_GRP)
            self.U_1.pack_into(self.buffer, SITE_CNT)
            # self.KxU_1.pack_into(SITE_CNT, SITE_NUM)
            self.C_n.pack_into(self.buffer, HAND_TYP)
            self.C_n.pack_into(self.buffer, HAND_ID)
            self.C_n.pack_into(self.buffer, CARD_TYP)
            self.C_n.pack_into(self.buffer, CARD_ID)
            self.C_n.pack_into(self.buffer, LOAD_TYP)
            self.C_n.pack_into(self.buffer, LOAD_ID)
            self.C_n.pack_into(self.buffer, DIB_TYP)
            self.C_n.pack_into(self.buffer, DIB_ID)
            self.C_n.pack_into(self.buffer, CABL_TYP)
            self.C_n.pack_into(self.buffer, CABL_ID)
            self.C_n.pack_into(self.buffer, CONT_TYP)
            self.C_n.pack_into(self.buffer, CONT_ID)
            self.C_n.pack_into(self.buffer, LASR_TYP)
            self.C_n.pack_into(self.buffer, LASR_ID)
            self.C_n.pack_into(self.buffer, EXTR_TYP)
            self.C_n.pack_into(self.buffer, EXTR_ID)

        self.write_fields(1, 80, write_fields)

    def TSR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_NUM: int,
        OPT_FLAG: bytes,
        TEST_TYP: Literal["P", "F", "M", " "] = " ",
        EXEC_CNT: int = 4294967295,
        FAIL_CNT: int = 4294967295,
        ALRM_CNT: int = 4294967295,
        TEST_NAM: str = "",
        SEQ_NAME: str = "",
        TEST_LBL: str = "",
        TEST_TIM: float = 0.0,
        TEST_MIN: float = 0.0,
        TEST_MAX: float = 0.0,
        TST_SUMS: float = 0.0,
        TST_SQRS: float = 0.0,
    ):
        """Test Synopsis Record"""
        # Implementation here

        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_NUM)
            self.C_1.pack_into(self.buffer, TEST_TYP)
            self.U_4.pack_into(self.buffer, TEST_NUM)
            self.U_4.pack_into(self.buffer, EXEC_CNT)
            self.U_4.pack_into(self.buffer, FAIL_CNT)
            self.U_4.pack_into(self.buffer, ALRM_CNT)
            self.C_n.pack_into(self.buffer, TEST_NAM)
            self.C_n.pack_into(self.buffer, SEQ_NAME)
            self.C_n.pack_into(self.buffer, TEST_LBL)
            self.B_1.pack_into(self.buffer, OPT_FLAG)
            self.R_4.pack_into(self.buffer, TEST_TIM)
            self.R_4.pack_into(self.buffer, TEST_MIN)
            self.R_4.pack_into(self.buffer, TEST_MAX)
            self.R_4.pack_into(self.buffer, TST_SUMS)
            self.R_4.pack_into(self.buffer, TST_SQRS)

        self.write_fields(10, 30, write_fields)

    def WCR(
        self,
        WAFR_SIZ: float = 0.0,
        DIE_HT: float = 0.0,
        DIE_WID: float = 0.0,
        WF_UNITS: int = 0,
        WF_FLAT: Literal["U", "D", "L", "R", " "] = " ",
        CENTER_X: int = -32768,
        CENTER_Y: int = -32768,
        POS_X: Literal["L", "R", " "] = " ",
        POS_Y: Literal["U", "D", " "] = " ",
    ):
        """Wafer Configuration Record"""
        # Implementation here
        pass

    def WIR(
        self,
        HEAD_NUM: int,
        START_T: int,
        SITE_GRP: int = 255,
        WAFER_ID: str = "",
    ):
        """Wafer Information Record"""

        # Implementation here
        def write_fields(self):
            self.U_1.pack_into(self.buffer, HEAD_NUM)
            self.U_1.pack_into(self.buffer, SITE_GRP)
            self.U_4.pack_into(self.buffer, START_T)
            self.C_n.pack_into(self.buffer, WAFER_ID)

        self.write_fields(2, 10, write_fields)

    def WRR(
        self,
        HEAD_NUM: int,
        FINISH_T: int,
        PART_CNT: int,
        SITE_GRP: int = 255,
        RTST_CNT: int = 4294967295,
        ABRT_CNT: int = 4294967295,
        GOOD_CNT: int = 4294967295,
        FUNC_CNT: int = 4294967295,
        WAFER_ID: str = "",
        FABWF_ID: str = "",
        FRAME_ID: str = "",
        MASK_ID: str = "",
        USR_DESC: str = "",
        EXC_DESC: str = "",
    ):
        """Wafer Results Record"""
        # Implementation here
        pass
