from typing import Any, Literal, Sequence

from pystdf4.Records.base import RecordBase
from pystdf4.Records.literials import AlphaNumericLiteral, BinPassFailLiteral, RetestConditionLiteral, StationModeLiteral, TestTypeLiteral


class StdfPacker(RecordBase):
    def __init__(self):
        super().__init__()

    def FAR(
        self,
        CPU_TYPE: int,
        STDF_VER: int,
    ) -> None:
        """File Attributes Record (FAR)

        Contains the information necessary to determine how to decode the STDF data
        contained in the file.

        Note:
            Required as the first record of the file.

        Args:
            CPU_TYPE (int): CPU type that wrote this file.
            STDF_VER (int): STDF version number.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, CPU_TYPE)
            obj.U_1.pack_into(obj.buffer, STDF_VER)

        self.write_fields(0, 10, write_fields)

    def ATR(
        self,
        MOD_TIM: int,
        CMD_LINE: str,
    ) -> None:
        """Audit Trail Record (ATR)

        Used to record any operation that alters the contents of the STDF file. The name of the
        program and all its parameters should be recorded in the ASCII field provided in this
        record. Typically, this record will be used to track filter programs that have been
        applied to the data.

        Note:
            Between the File Attributes Record (FAR) and the Master Information Record (MIR).
            The filter program that writes the altered STDF file must write its ATR immediately
            after the FAR (and hence before any other ATRs that may be in the file). In this way,
            multiple ATRs will be in reverse chronological order.

        Args:
            MOD_TIM (int): Date and time of STDF file modification.
            CMD_LINE (str): Command line of program.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, MOD_TIM)
            obj.C_n.pack_into(obj.buffer, CMD_LINE)

        self.write_fields(0, 20, write_fields)

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
        MODE_COD: StationModeLiteral = " ",
        RTST_COD: RetestConditionLiteral = " ",
        PROT_COD: AlphaNumericLiteral = " ",
        BURN_TIM: int = 65535,
        CMOD_COD: AlphaNumericLiteral = " ",
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
        """Master Information Record (MIR)

        The MIR and the MRR (Master Results Record) contain all the global information that
        is to be stored for a tested lot of parts. Each data stream must have exactly one MIR,
        immediately after the FAR (and the ATRs, if they are used). This will allow any data
        reporting or analysis programs access to this information in the shortest possible
        amount of time.

        Note:
            Immediately after the File Attributes Record (FAR) and the Audit Trail Records (ATR),
            if ATRs are used.

        Args:
            SETUP_T (int): Date and time of job setup.
            START_T (int): Date and time first part tested.
            STAT_NUM (int): Tester station number.
            LOT_ID (str): Lot ID (customer specified).
            PART_TYP (str): Part Type (or product ID).
            NODE_NAM (str): Name of node that generated data.
            TSTR_TYP (str): Tester type.
            JOB_NAM (str): Job name (test program name).
            MODE_COD (StationModeLiteral): Test mode code (e.g. prod, dev). Defaults to " ".
            RTST_COD (RetestConditionLiteral): Lot retest code. Defaults to " ".
            PROT_COD (AlphaNumericLiteral): Data protection code. Defaults to " ".
            BURN_TIM (int): Burn-in time (in minutes). Defaults to 65535.
            CMOD_COD (AlphaNumericLiteral): Command mode code. Defaults to " ".
            JOB_REV (str): Job (test program) revision number. Defaults to "".
            SBLOT_ID (str): Sublot ID. Defaults to "".
            OPER_NAM (str): Operator name or ID (at setup time). Defaults to "".
            EXEC_TYP (str): Tester executive software type. Defaults to "".
            EXEC_VER (str): Tester exec software version number. Defaults to "".
            TEST_COD (str): Test phase or step code. Defaults to "".
            TST_TEMP (str): Test temperature. Defaults to "".
            USER_TXT (str): Generic user text. Defaults to "".
            AUX_FILE (str): Name of auxiliary data file. Defaults to "".
            PKG_TYP (str): Package type. Defaults to "".
            FAMLY_ID (str): Product family ID. Defaults to "".
            DATE_COD (str): Date code. Defaults to "".
            FACIL_ID (str): Test facility ID. Defaults to "".
            FLOOR_ID (str): Test floor ID. Defaults to "".
            PROC_ID (str): Fabrication process ID. Defaults to "".
            OPER_FRQ (str): Operation frequency or step. Defaults to "".
            SPEC_NAM (str): Test specification name. Defaults to "".
            SPEC_VER (str): Test specification version number. Defaults to "".
            FLOW_ID (str): Test flow ID. Defaults to "".
            SETUP_ID (str): Test setup ID. Defaults to "".
            DSGN_REV (str): Device design revision. Defaults to "".
            ENG_ID (str): Engineering lot ID. Defaults to "".
            ROM_COD (str): ROM code ID. Defaults to "".
            SERL_NUM (str): Tester serial number. Defaults to "".
            SUPR_NAM (str): Supervisor name or ID. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, SETUP_T)
            obj.U_4.pack_into(obj.buffer, START_T)
            obj.U_1.pack_into(obj.buffer, STAT_NUM)
            obj.C_1.pack_into(obj.buffer, MODE_COD)
            obj.C_1.pack_into(obj.buffer, RTST_COD)
            obj.C_1.pack_into(obj.buffer, PROT_COD)
            obj.U_2.pack_into(obj.buffer, BURN_TIM)
            obj.C_1.pack_into(obj.buffer, CMOD_COD)
            obj.C_n.pack_into(obj.buffer, LOT_ID)
            obj.C_n.pack_into(obj.buffer, PART_TYP)
            obj.C_n.pack_into(obj.buffer, NODE_NAM)
            obj.C_n.pack_into(obj.buffer, TSTR_TYP)
            obj.C_n.pack_into(obj.buffer, JOB_NAM)
            obj.C_n.pack_into(obj.buffer, JOB_REV)
            obj.C_n.pack_into(obj.buffer, SBLOT_ID)
            obj.C_n.pack_into(obj.buffer, OPER_NAM)
            obj.C_n.pack_into(obj.buffer, EXEC_TYP)
            obj.C_n.pack_into(obj.buffer, EXEC_VER)
            obj.C_n.pack_into(obj.buffer, TEST_COD)
            obj.C_n.pack_into(obj.buffer, TST_TEMP)
            obj.C_n.pack_into(obj.buffer, USER_TXT)
            obj.C_n.pack_into(obj.buffer, AUX_FILE)
            obj.C_n.pack_into(obj.buffer, PKG_TYP)
            obj.C_n.pack_into(obj.buffer, FAMLY_ID)
            obj.C_n.pack_into(obj.buffer, DATE_COD)
            obj.C_n.pack_into(obj.buffer, FACIL_ID)
            obj.C_n.pack_into(obj.buffer, FLOOR_ID)
            obj.C_n.pack_into(obj.buffer, PROC_ID)
            obj.C_n.pack_into(obj.buffer, OPER_FRQ)
            obj.C_n.pack_into(obj.buffer, SPEC_NAM)
            obj.C_n.pack_into(obj.buffer, SPEC_VER)
            obj.C_n.pack_into(obj.buffer, FLOW_ID)
            obj.C_n.pack_into(obj.buffer, SETUP_ID)
            obj.C_n.pack_into(obj.buffer, DSGN_REV)
            obj.C_n.pack_into(obj.buffer, ENG_ID)
            obj.C_n.pack_into(obj.buffer, ROM_COD)
            obj.C_n.pack_into(obj.buffer, SERL_NUM)
            obj.C_n.pack_into(obj.buffer, SUPR_NAM)

        self.write_fields(1, 10, write_fields)

    def MRR(
        self,
        FINISH_T: int = 0,
        DISP_COD: AlphaNumericLiteral = " ",
        USR_DESC: str = "",
        EXC_DESC: str = "",
    ) -> None:
        """Master Results Record (MRR)

        The Master Results Record (MRR) is a logical extension of the Master Information
        Record (MIR). The data can be thought of as belonging with the MIR, but it is not
        available when the tester writes the MIR information. Each data stream must have
        exactly one MRR as the last record in the data stream.

        Note:
            Must be the last record in the data stream.

        Args:
            FINISH_T (int): Date and time last part tested. Defaults to 0.
            DISP_COD (AlphaNumericLiteral): Lot disposition code. Defaults to " ".
            USR_DESC (str): Lot description supplied by user. Defaults to "".
            EXC_DESC (str): Lot description supplied by exec. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, FINISH_T)
            obj.C_1.pack_into(obj.buffer, DISP_COD)
            obj.C_n.pack_into(obj.buffer, USR_DESC)
            obj.C_n.pack_into(obj.buffer, EXC_DESC)

        self.write_fields(1, 20, write_fields)

    def PCR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        PART_CNT: int,
        RTST_CNT: int = 4294967295,
        ABRT_CNT: int = 4294967295,
        GOOD_CNT: int = 4294967295,
        FUNC_CNT: int = 4294967295,
    ) -> None:
        """Part Count Record (PCR)

        Contains the part count totals for one or all test sites. Each data stream must have at
        least one PCR to show the part count.

        Note:
            There must be at least one PCR in the file: either one summary PCR for all test sites
            (HEAD_NUM= 255), or one PCR for each head/site combination, or both.
            When data is being recorded in real time, this record will usually appear near the
            end of the data stream.

        Args:
            HEAD_NUM (int): Test head number. If this PCR contains a summary of the part counts for
                all test sites, this field must be set to 255
            SITE_NUM (int): Test site number.
            PART_CNT (int): Number of parts tested.
            RTST_CNT (int): Number of parts retested. Defaults to 4294967295.
            ABRT_CNT (int): Number of aborts during testing. Defaults to 4294967295.
            GOOD_CNT (int): Number of good (passed) parts tested. Defaults to 4294967295.
            FUNC_CNT (int): Number of functional parts tested. Defaults to 4294967295.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.U_4.pack_into(obj.buffer, PART_CNT)
            obj.U_4.pack_into(obj.buffer, RTST_CNT)
            obj.U_4.pack_into(obj.buffer, ABRT_CNT)
            obj.U_4.pack_into(obj.buffer, GOOD_CNT)
            obj.U_4.pack_into(obj.buffer, FUNC_CNT)

        self.write_fields(1, 30, write_fields)

    def HBR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        HBIN_NUM: int,
        HBIN_CNT: int,
        HBIN_PF: BinPassFailLiteral = " ",
        HBIN_NAM: str = "",
    ) -> None:
        """Hardware Bin Record (HBR)

        Stores a count of the parts "physically" placed in a particular bin after testing. (In
        wafer testing, "physical" binning is not an actual transfer of the chip, but rather is
        represented by a drop of ink or an entry in a wafer map file.) This bin count can be for
        a single test site (when parallel testing) or a total for all test sites.

        Note:
            When data is being recorded in real time, this record usually appears near the end of
            the data stream.

        Args:
            HEAD_NUM (int): Test head number. If this HBR contains a summary of the hardware bin
                counts for all test sites, this field must be set to 255.
            SITE_NUM (int): Test site number.
            HBIN_NUM (int): Hardware bin number.
            HBIN_CNT (int): Number of parts in bin.
            HBIN_PF (BinPassFailLiteral): Pass/fail indication. Defaults to " ".
            HBIN_NAM (str): Name of hardware bin. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.U_2.pack_into(obj.buffer, HBIN_NUM)
            obj.U_4.pack_into(obj.buffer, HBIN_CNT)
            obj.C_1.pack_into(obj.buffer, HBIN_PF)
            obj.C_n.pack_into(obj.buffer, HBIN_NAM)

        self.write_fields(1, 40, write_fields)

    def SBR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        SBIN_NUM: int,
        SBIN_CNT: int,
        SBIN_PF: BinPassFailLiteral = " ",
        SBIN_NAM: str = "",
    ) -> None:
        """Software Bin Record (SBR)

        Stores a count of the parts associated with a particular logical bin after testing. This
        bin count can be for a single test site (when parallel testing) or a total for all test sites.

        Note:
            One per software bin for each site. One per software bin for bin totals.
            When data is being recorded in real time, this record usually appears near the
            end of the data stream.

        Args:
            HEAD_NUM (int): Test head number. If this SBR contains a summary of the software bin
                counts for all test sites, this field must be set to 255.
            SITE_NUM (int): Test site number.
            SBIN_NUM (int): Software bin number.
            SBIN_CNT (int): Number of parts in bin.
            SBIN_PF (BinPassFailLiteral): Pass/fail indication. Defaults to " ".
            SBIN_NAM (str): Name of software bin. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.U_2.pack_into(obj.buffer, SBIN_NUM)
            obj.U_4.pack_into(obj.buffer, SBIN_CNT)
            obj.C_1.pack_into(obj.buffer, SBIN_PF)
            obj.C_n.pack_into(obj.buffer, SBIN_NAM)

        self.write_fields(1, 50, write_fields)

    def PMR(
        self,
        PMR_INDX: int,
        CHAN_TYP: int = 0,
        CHAN_NAM: str = "",
        PHY_NAM: str = "",
        LOG_NAM: str = "",
        HEAD_NUM: int = 1,
        SITE_NUM: int = 1,
    ) -> None:
        """Pin Map Record (PMR)

        Provides indexing of tester channel names, and maps them to physical and logical pin
        names. Each PMR defines the information for a single channel/pin combination.

        Note:
            One per channel/pin combination used in the test program.
            Reuse of a PMR index number is not permitted.
            After the initial sequence and before the first PGR, PLR, FTR, or MPR that
            uses this record's PMR_INDX value.

        Args:
            PMR_INDX (int): Unique index associated with pin. The range of legal PMR indexes is 1 - 32,767.
            CHAN_TYP (int): Channel type. Defaults to 0.
            CHAN_NAM (str): Channel name. Defaults to "".
            PHY_NAM (str): Physical name of pin. Defaults to "".
            LOG_NAM (str): Logical name of pin. Defaults to "".
            HEAD_NUM (int): Head number associated with channel. Defaults to 1.
            SITE_NUM (int): Site number associated with channel. Defaults to 1.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_2.pack_into(obj.buffer, PMR_INDX)
            obj.U_2.pack_into(obj.buffer, CHAN_TYP)
            obj.C_n.pack_into(obj.buffer, CHAN_NAM)
            obj.C_n.pack_into(obj.buffer, PHY_NAM)
            obj.C_n.pack_into(obj.buffer, LOG_NAM)
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)

        self.write_fields(1, 60, write_fields)

    def PGR(
        self,
        GRP_INDX: int,
        GRP_NAM: str = "",
        INDX_CNT: int = 0,
        PMR_INDX: Sequence[int] = tuple(),
    ) -> None:
        """Pin Group Record (PGR)

        Associates a name with a group of pins.

        Note:
            After all the PMRs whose PMR index values are listed in the PMR_INDX array of this
            record; and before the first PLR that uses this record’s GRP_INDX value.

        Args:
            GRP_INDX (int): Unique index associated with pin group. The range of legal group index numbers
                is 32,768 - 65,535.
            GRP_NAM (str): Name of pin group. Defaults to "".
            INDX_CNT (int): Count (k) of PMR indexes. Defaults to 0.
            PMR_INDX (Sequence[int]): Array of indexes for pins in the group. Defaults to tuple().
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_2.pack_into(obj.buffer, GRP_INDX)
            obj.C_n.pack_into(obj.buffer, GRP_NAM)
            obj.U_2.pack_into(obj.buffer, INDX_CNT)
            obj.kxU_2.pack_into(obj.buffer, PMR_INDX, INDX_CNT)

        self.write_fields(1, 62, write_fields)

    def PLR(
        self,
        GRP_CNT: int = 0,
        GRP_INDX: Sequence[int] = tuple(),
        GRP_MODE: Sequence[int] = tuple(),
        GRP_RADX: Sequence[int] = tuple(),
        PGM_CHAR: Sequence[str] = tuple(),
        RTN_CHAR: Sequence[str] = tuple(),
        PGM_CHAL: Sequence[str] = tuple(),
        RTN_CHAL: Sequence[str] = tuple(),
    ) -> None:
        """Pin List Record (PLR)

        Defines the current display radix and operating mode for a pin or pin group.

        Note:
            After all the PMRs and PGRs whose PMR index values and pin group index values are
            listed in the GRP_INDX array of this record; and before the first FTR that references pins
            or pin groups whose modes are defined in this record.

        Args:
            GRP_CNT (int): Count (k) of pins or pin groups. Defaults to 0.
            GRP_INDX (Sequence[int]): Array of pin or pin group indexes. Defaults to tuple().
            GRP_MODE (Sequence[int]): Operating mode of pin group. Defaults to tuple().
            GRP_RADX (Sequence[int]): Display radix of pin group. Defaults to tuple().
            PGM_CHAR (Sequence[str]): Program state encoding characters. Defaults to tuple().
            RTN_CHAR (Sequence[str]): Return state encoding characters. Defaults to tuple().
            PGM_CHAL (Sequence[str]): Program state encoding characters. Defaults to tuple().
            RTN_CHAL (Sequence[str]): Return state encoding characters. Defaults to tuple().
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_2.pack_into(obj.buffer, GRP_CNT)
            obj.kxU_2.pack_into(obj.buffer, GRP_INDX, size=GRP_CNT)
            obj.kxU_2.pack_into(obj.buffer, GRP_MODE, size=GRP_CNT)
            obj.kxU_1.pack_into(obj.buffer, GRP_RADX, size=GRP_CNT)
            obj.kxC_n.pack_into(obj.buffer, PGM_CHAR, size=GRP_CNT)
            obj.kxC_n.pack_into(obj.buffer, RTN_CHAR, size=GRP_CNT)
            obj.kxC_n.pack_into(obj.buffer, PGM_CHAL, size=GRP_CNT)
            obj.kxC_n.pack_into(obj.buffer, RTN_CHAL, size=GRP_CNT)

        self.write_fields(1, 63, write_fields)

    def RDR(
        self,
        NUM_BINS: int = 0,
        RTST_BIN: Sequence[int] = tuple(),
    ) -> None:
        """Retest Data Record (RDR)

        Signals that the data in this STDF file is for retested parts. The data in this record,
        combined with information in the MIR, tells data filtering programs what data to
        replace when processing retest data.

        Note:
            If this record is used, it must appear immediately after the Master Information Record (MIR).

        Args:
            NUM_BINS (int): Number (k) of bins being retested. Defaults to 0.
            RTST_BIN (Sequence[int]): Array of retest bin numbers. Defaults to tuple().
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_2.pack_into(obj.buffer, NUM_BINS)
            obj.kxU_2.pack_into(obj.buffer, RTST_BIN, size=NUM_BINS)

        self.write_fields(1, 70, write_fields)

    def SDR(
        self,
        HEAD_NUM: int,
        SITE_GRP: int,
        SITE_CNT: int = 0,
        SITE_NUM: Sequence[int] = tuple(),
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
    ) -> None:
        """Site Description Record (SDR)

        Contains the configuration information for one or more test sites, connected to one test
        head, that compose a site group.

        Note:
            One for each site or group of sites that is differently configured.
            Immediately after the MIR and RDR (if an RDR is used).

        Args:
            HEAD_NUM (int): Test head number..
            SITE_GRP (int): Site group number..
            SITE_CNT (int): Number (k) of test sites in site group. Defaults to 0.
            SITE_NUM (Sequence[int]): Array of test site numbers. Defaults to tuple().
            HAND_TYP (str): Handler or probe type. Defaults to "".
            HAND_ID (str): Handler or prober ID. Defaults to "".
            CARD_TYP (str): Probe card type. Defaults to "".
            CARD_ID (str): Probe card ID. Defaults to "".
            LOAD_TYP (str): Load board type. Defaults to "".
            LOAD_ID (str): Load board ID. Defaults to "".
            DIB_TYP (str): DIB board type. Defaults to "".
            DIB_ID (str): DIB board ID. Defaults to "".
            CABL_TYP (str): Interface cable type. Defaults to "".
            CABL_ID (str): Interface cable ID. Defaults to "".
            CONT_TYP (str): Handler contactor type. Defaults to "".
            CONT_ID (str): Handler contactor ID. Defaults to "".
            LASR_TYP (str): Laser type. Defaults to "".
            LASR_ID (str): Laser ID. Defaults to "".
            EXTR_TYP (str): Extra equipment type field. Defaults to "".
            EXTR_ID (str): Extra equipment ID. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_GRP)
            obj.U_1.pack_into(obj.buffer, SITE_CNT)
            obj.kxU_1.pack_into(obj.buffer, SITE_NUM, size=SITE_CNT)
            obj.C_n.pack_into(obj.buffer, HAND_TYP)
            obj.C_n.pack_into(obj.buffer, HAND_ID)
            obj.C_n.pack_into(obj.buffer, CARD_TYP)
            obj.C_n.pack_into(obj.buffer, CARD_ID)
            obj.C_n.pack_into(obj.buffer, LOAD_TYP)
            obj.C_n.pack_into(obj.buffer, LOAD_ID)
            obj.C_n.pack_into(obj.buffer, DIB_TYP)
            obj.C_n.pack_into(obj.buffer, DIB_ID)
            obj.C_n.pack_into(obj.buffer, CABL_TYP)
            obj.C_n.pack_into(obj.buffer, CABL_ID)
            obj.C_n.pack_into(obj.buffer, CONT_TYP)
            obj.C_n.pack_into(obj.buffer, CONT_ID)
            obj.C_n.pack_into(obj.buffer, LASR_TYP)
            obj.C_n.pack_into(obj.buffer, LASR_ID)
            obj.C_n.pack_into(obj.buffer, EXTR_TYP)
            obj.C_n.pack_into(obj.buffer, EXTR_ID)

        self.write_fields(1, 80, write_fields)

    def WIR(
        self,
        HEAD_NUM: int,
        START_T: int,
        SITE_GRP: int = 255,
        WAFER_ID: str = "",
    ) -> None:
        """Wafer Information Record (WIR)

        Acts mainly as a marker to indicate where testing of a particular wafer begins for each
        wafer tested by the job plan. The WIR and the Wafer Results Record (WRR) bracket all
        the stored information pertaining to one tested wafer.

        Note:
            One per wafer tested.
            Sent before testing each wafer.

        Args:
            HEAD_NUM (int): Test head number.
            START_T (int): Date and time first part tested.
            SITE_GRP (int): Site group number. If this information is not known, or the tester
                does not support the concept of site groups, this field should be set to 255.
            WAFER_ID (str): Wafer ID. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_GRP)
            obj.U_4.pack_into(obj.buffer, START_T)
            obj.C_n.pack_into(obj.buffer, WAFER_ID)

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
    ) -> None:
        """Wafer Results Record (WRR)

        Contains the result information relating to each wafer tested by the job plan. The WRR
        and the Wafer Information Record (WIR) bracket all the stored information pertaining
        to one tested wafer.

        Note:
            Anywhere in the data stream after the corresponding WIR. Sent after testing each wafer.

        Args:
            HEAD_NUM (int): Test head number.
            FINISH_T (int): Date and time last part tested.
            PART_CNT (int): Number of parts tested.
            SITE_GRP (int): Site group number. Defaults to 255.
            RTST_CNT (int): Number of parts retested. Defaults to 4294967295.
            ABRT_CNT (int): Number of aborts during testing. Defaults to 4294967295.
            GOOD_CNT (int): Number of good (passed) parts tested. Defaults to 4294967295.
            FUNC_CNT (int): Number of functional parts tested. Defaults to 4294967295.
            WAFER_ID (str): Wafer ID. Defaults to "".
            FABWF_ID (str): Fab wafer ID. Defaults to "".
            FRAME_ID (str): Wafer frame ID. Defaults to "".
            MASK_ID (str): Wafer mask ID. Defaults to "".
            USR_DESC (str): Wafer description supplied by user. Defaults to "".
            EXC_DESC (str): Wafer description supplied by exec. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_GRP)
            obj.U_4.pack_into(obj.buffer, FINISH_T)
            obj.U_4.pack_into(obj.buffer, PART_CNT)
            obj.U_4.pack_into(obj.buffer, RTST_CNT)
            obj.U_4.pack_into(obj.buffer, ABRT_CNT)
            obj.U_4.pack_into(obj.buffer, GOOD_CNT)
            obj.U_4.pack_into(obj.buffer, FUNC_CNT)
            obj.C_n.pack_into(obj.buffer, WAFER_ID)
            obj.C_n.pack_into(obj.buffer, FABWF_ID)
            obj.C_n.pack_into(obj.buffer, FRAME_ID)
            obj.C_n.pack_into(obj.buffer, MASK_ID)
            obj.C_n.pack_into(obj.buffer, USR_DESC)
            obj.C_n.pack_into(obj.buffer, EXC_DESC)

        self.write_fields(2, 20, write_fields)

    def WCR(
        self,
        WAFR_SIZ: float = 0.0,
        DIE_HT: float = 0.0,
        DIE_WID: float = 0.0,
        WF_UNITS: Literal[0, 1, 2, 3, 4] = 0,
        WF_FLAT: Literal["U", "D", "L", "R", " "] = " ",
        CENTER_X: int = -32768,
        CENTER_Y: int = -32768,
        POS_X: Literal["L", "R", " "] = " ",
        POS_Y: Literal["U", "D", " "] = " ",
    ) -> None:
        """Wafer Configuration Record (WCR)

        Contains the configuration information for the wafers tested by the job plan. The
        WCR provides the dimensions and orientation information for all wafers and dice
        in the lot.

        Note:
            One per STDF file (used only if wafer testing).

        Args:
            WAFR_SIZ (float): Diameter of wafer in WF_UNITS. Defaults to 0.0.
            DIE_HT (float): Height of die in WF_UNITS. Defaults to 0.0.
            DIE_WID (float): Width of die in WF_UNITS. Defaults to 0.0.
            WF_UNITS (Literal[0, 1, 2, 3, 4]): Units for wafer and die dimensions. 0 = Unknown units,
                1 = Units are in inches, 2 =  Units are in centimeters, 3 = Units are in millimeters,
                4 = Units are in mils. Defaults to 0.
            WF_FLAT (Literal["U", "D", "L", "R", " "]): Orientation of wafer flat. "U" = Up, "D" = Down,
                "L" = Left, "R" = Right, " " = Unknown. Defaults to " ".
            CENTER_X (int): X coordinate of center die on wafer. Defaults to -32768.
            CENTER_Y (int): Y coordinate of center die on wafer. Defaults to -32768.
            POS_X (Literal["L", "R", " "]): Positive X direction of wafer. "L" = Left, "R" = Right, " "
                = Unknown. Defaults to " "
            POS_Y (Literal["U", "D", " "]): Positive Y direction of wafer. "U" = Up, "D" = Down, " " =
                Unknown. Defaults to " ".
        """

        def write_fields(obj: "StdfPacker"):
            obj.R_4.pack_into(obj.buffer, WAFR_SIZ)
            obj.R_4.pack_into(obj.buffer, DIE_HT)
            obj.R_4.pack_into(obj.buffer, DIE_WID)
            obj.U_1.pack_into(obj.buffer, WF_UNITS)
            obj.C_1.pack_into(obj.buffer, WF_FLAT)
            obj.I_2.pack_into(obj.buffer, CENTER_X)
            obj.I_2.pack_into(obj.buffer, CENTER_Y)
            obj.C_1.pack_into(obj.buffer, POS_X)
            obj.C_1.pack_into(obj.buffer, POS_Y)

        self.write_fields(2, 30, write_fields)

    def PIR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
    ) -> None:
        """Part Information Record (PIR)

        Acts as a marker to indicate where testing of a particular part begins for each part
        tested by the test program. The PIR and the Part Results Record (PRR) bracket all the
        stored information pertaining to one tested part.

        Note:
            One per part tested.
            Sent before testing each part.

        Args:
            HEAD_NUM (int): Test head number.
            SITE_NUM (int): Test site number.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)

        self.write_fields(5, 10, write_fields)

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
    ) -> None:
        """Part Results Record (PRR)

        Contains the result information relating to each part tested by the test program. The
        PRR and the Part Information Record (PIR) bracket all the stored information
        pertaining to one tested part.

        Note:
            One per part tested.
            Sent after completion of testing each part.

        Args:
            HEAD_NUM (int): Test head number.
            SITE_NUM (int): Test site number.
            PART_FLG (bytes): Part information flag.
            NUM_TEST (int): Number of tests executed.
            HARD_BIN (int): Hardware bin number.
            SOFT_BIN (int): Software bin number. Defaults to 65535.
            X_COORD (int): (Wafer) X coordinate. Defaults to -32768. Have legal values in the
                range -32767 to 32767. A missing value is indicated by the value -32768.
            Y_COORD (int): (Wafer) Y coordinate. Defaults to -32768. Have legal values in the
                range -32767 to 32767. A missing value is indicated by the value -32768.
            TEST_T (int): Elapsed test time in milliseconds. Defaults to 0.
            PART_ID (str): Part identification. Defaults to "".
            PART_TXT (str): Part description text. Defaults to "".
            PART_FIX (bytes): Part repair information. Defaults to b"".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.B_1.pack_into(obj.buffer, PART_FLG)
            obj.U_2.pack_into(obj.buffer, NUM_TEST)
            obj.U_2.pack_into(obj.buffer, HARD_BIN)
            obj.U_2.pack_into(obj.buffer, SOFT_BIN)
            obj.I_2.pack_into(obj.buffer, X_COORD)
            obj.I_2.pack_into(obj.buffer, Y_COORD)
            obj.U_4.pack_into(obj.buffer, TEST_T)
            obj.C_n.pack_into(obj.buffer, PART_ID)
            obj.C_n.pack_into(obj.buffer, PART_TXT)
            obj.B_n.pack_into(obj.buffer, PART_FIX)

        self.write_fields(5, 20, write_fields)

    def TSR(
        self,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_NUM: int,
        OPT_FLAG: bytes,
        TEST_TYP: TestTypeLiteral = " ",
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
    ) -> None:
        """Test Synopsis Record (TSR)

        Contains the test execution and failure counts for one parametric or functional test in
        the test program. Also contains static information, such as test name.

        Note:
            One for each test executed in the test program.
            When test data is being generated in real-time, these records will appear after the last PRR.

        Args:
            HEAD_NUM (int): Test head number. If this TSR contains a summary of the test counts for all
                test sites, this field must be set to 255.
            SITE_NUM (int): Test site number.
            TEST_NUM (int): Test number.
            OPT_FLAG (bytes): Optional data flag.
            TEST_TYP (AlphaNumericLiteral): Test type. Defaults to " ".
            EXEC_CNT (int): Number of test executions. Defaults to 4294967295.
            FAIL_CNT (int): Number of test failures. Defaults to 4294967295.
            ALRM_CNT (int): Number of alarmed tests. Defaults to 4294967295.
            TEST_NAM (str): Test name. Defaults to "".
            SEQ_NAME (str): Sequencer (program segment/flow) name. Defaults to "".
            TEST_LBL (str): Test label or text. Defaults to "".
            TEST_TIM (float): Average test execution time in seconds. Defaults to 0.0.
            TEST_MIN (float): Lowest test result value. Defaults to 0.0.
            TEST_MAX (float): Highest test result value. Defaults to 0.0.
            TST_SUMS (float): Sum of test result values. Defaults to 0.0.
            TST_SQRS (float): Sum of squares of test result values. Defaults to 0.0.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.C_1.pack_into(obj.buffer, TEST_TYP)
            obj.U_4.pack_into(obj.buffer, TEST_NUM)
            obj.U_4.pack_into(obj.buffer, EXEC_CNT)
            obj.U_4.pack_into(obj.buffer, FAIL_CNT)
            obj.U_4.pack_into(obj.buffer, ALRM_CNT)
            obj.C_n.pack_into(obj.buffer, TEST_NAM)
            obj.C_n.pack_into(obj.buffer, SEQ_NAME)
            obj.C_n.pack_into(obj.buffer, TEST_LBL)
            obj.B_1.pack_into(obj.buffer, OPT_FLAG)
            obj.R_4.pack_into(obj.buffer, TEST_TIM)
            obj.R_4.pack_into(obj.buffer, TEST_MIN)
            obj.R_4.pack_into(obj.buffer, TEST_MAX)
            obj.R_4.pack_into(obj.buffer, TST_SUMS)
            obj.R_4.pack_into(obj.buffer, TST_SQRS)

        self.write_fields(10, 30, write_fields)

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
    ) -> None:
        """Parametric Test Record (PTR)

        Contains the results of a single execution of a parametric test in the test program. The
        first occurrence of this record also establishes the default values for all semi-static
        information about the test, such as limits, units, and scaling.

        Note:
            One per parametric test execution.

        Args:
            TEST_NUM (int): Test number.
            HEAD_NUM (int): Test head number.
            SITE_NUM (int): Test site number.
            TEST_FLG (bytes): Test flags (fail, alarm, etc.).
            PARM_FLG (bytes): Parametric test flags (drift, etc.).
            OPT_FLAG (bytes): Optional data flag.
            RESULT (float): Test result. Defaults to 0.0.
            TEST_TXT (str): Test description text or label. Defaults to "".
            ALARM_ID (str): Name of alarm. Defaults to "".
            RES_SCAL (int): Test results scaling exponent. Defaults to 0.
            LLM_SCAL (int): Low limit scaling exponent. Defaults to 0.
            HLM_SCAL (int): High limit scaling exponent. Defaults to 0.
            LO_LIMIT (float): Low test limit value. Defaults to 0.0.
            HI_LIMIT (float): High test limit value. Defaults to 0.0.
            UNITS (str): Test units. Defaults to "".
            C_RESFMT (str): ANSI C result format string. Defaults to "".
            C_LLMFMT (str): ANSI C low limit format string. Defaults to "".
            C_HLMFMT (str): ANSI C high limit format string. Defaults to "".
            LO_SPEC (float): Low specification limit value. Defaults to 0.0.
            HI_SPEC (float): High specification limit value. Defaults to 0.0.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, TEST_NUM)
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.B_1.pack_into(obj.buffer, TEST_FLG)
            obj.B_1.pack_into(obj.buffer, PARM_FLG)
            obj.R_4.pack_into(obj.buffer, RESULT)
            obj.C_n.pack_into(obj.buffer, TEST_TXT)
            obj.C_n.pack_into(obj.buffer, ALARM_ID)
            obj.B_1.pack_into(obj.buffer, OPT_FLAG)
            obj.I_1.pack_into(obj.buffer, RES_SCAL)
            obj.I_1.pack_into(obj.buffer, LLM_SCAL)
            obj.I_1.pack_into(obj.buffer, HLM_SCAL)
            obj.R_4.pack_into(obj.buffer, LO_LIMIT)
            obj.R_4.pack_into(obj.buffer, HI_LIMIT)
            obj.C_n.pack_into(obj.buffer, UNITS)
            obj.C_n.pack_into(obj.buffer, C_RESFMT)
            obj.C_n.pack_into(obj.buffer, C_LLMFMT)
            obj.C_n.pack_into(obj.buffer, C_HLMFMT)
            obj.R_4.pack_into(obj.buffer, LO_SPEC)
            obj.R_4.pack_into(obj.buffer, HI_SPEC)

        self.write_fields(15, 10, write_fields)

    def MPR(
        self,
        TEST_NUM: int,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_FLG: bytes,
        PARM_FLG: bytes,
        OPT_FLAG: bytes,
        RTN_ICNT: int = 0,
        RSLT_CNT: int = 0,
        RTN_STAT: Sequence[int] = tuple(),
        RTN_RSLT: Sequence[float] = tuple(),
        TEST_TXT: str = "",
        ALARM_ID: str = "",
        RES_SCAL: int = 0,
        LLM_SCAL: int = 0,
        HLM_SCAL: int = 0,
        LO_LIMIT: float = 0.0,
        HI_LIMIT: float = 0.0,
        START_IN: float = 0.0,
        INCR_IN: float = 0.0,
        RTN_INDX: Sequence[int] = tuple(),
        UNITS: str = "",
        UNITS_IN: str = "",
        C_RESFMT: str = "",
        C_LLMFMT: str = "",
        C_HLMFMT: str = "",
        LO_SPEC: float = 0.0,
        HI_SPEC: float = 0.0,
    ) -> None:
        """Multiple-Result Parametric Record (MPR)

        Contains the results of a single execution of a parametric test in the test program
        where that test returns multiple values. The first occurrence of this record also
        establishes the default values for all semi-static information about the test, such as
        limits, units, and scaling.

        Note:
            One per multiple-result parametric test execution.

        Args:
            TEST_NUM (int): Test number.
            HEAD_NUM (int): Test head number.
            SITE_NUM (int): Test site number.
            TEST_FLG (bytes): Test flags (fail, alarm, etc.).
            PARM_FLG (bytes): Parametric test flags (drift, etc.).
            OPT_FLAG (bytes): Optional data flag.
            RTN_ICNT (int): Count (j) of PMR indexes. Defaults to 0.
            RSLT_CNT (int): Count (k) of returned results. Defaults to 0.
            RTN_STAT (Sequence[int]): Array of returned states. Defaults to tuple().
            RTN_RSLT (Sequence[float]): Array of returned results. Defaults to tuple().
            TEST_TXT (str): Descriptive text or label. Defaults to "".
            ALARM_ID (str): Name of alarm. Defaults to "".
            RES_SCAL (int): Test result scaling exponent. Defaults to 0.
            LLM_SCAL (int): Test low limit scaling exponent. Defaults to 0.
            HLM_SCAL (int): Test high limit scaling exponent. Defaults to 0.
            LO_LIMIT (float): Test low limit value. Defaults to 0.0.
            HI_LIMIT (float): Test high limit value. Defaults to 0.0.
            START_IN (float): Starting input value (condition). Defaults to 0.0.
            INCR_IN (float): Increment of input condition. Defaults to 0.0.
            RTN_INDX (Sequence[int]): Array of PMR indexes. Defaults to None.
            UNITS (str): Units of returned results. Defaults to "".
            UNITS_IN (str): Input condition units. Defaults to "".
            C_RESFMT (str): ANSI C result format string. Defaults to "".
            C_LLMFMT (str): ANSI C low limit format string. Defaults to "".
            C_HLMFMT (str): ANSI C high limit format string. Defaults to "".
            LO_SPEC (float): Low specification limit value. Defaults to 0.0.
            HI_SPEC (float): High specification limit value. Defaults to 0.0.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, TEST_NUM)
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.B_1.pack_into(obj.buffer, TEST_FLG)
            obj.B_1.pack_into(obj.buffer, PARM_FLG)
            obj.U_2.pack_into(obj.buffer, RTN_ICNT)
            obj.U_2.pack_into(obj.buffer, RSLT_CNT)
            # obj.kx_N1.pack_into(obj.buffer, RTN_STAT) # TODO: fix this
            obj.kxR_4.pack_into(obj.buffer, RTN_RSLT, size=RSLT_CNT)
            obj.C_n.pack_into(obj.buffer, TEST_TXT)
            obj.C_n.pack_into(obj.buffer, ALARM_ID)
            obj.B_1.pack_into(obj.buffer, OPT_FLAG)
            obj.I_1.pack_into(obj.buffer, RES_SCAL)
            obj.I_1.pack_into(obj.buffer, LLM_SCAL)
            obj.I_1.pack_into(obj.buffer, HLM_SCAL)
            obj.R_4.pack_into(obj.buffer, LO_LIMIT)
            obj.R_4.pack_into(obj.buffer, HI_LIMIT)
            obj.R_4.pack_into(obj.buffer, START_IN)
            obj.R_4.pack_into(obj.buffer, INCR_IN)
            obj.kxU_2.pack_into(obj.buffer, RTN_INDX, size=RTN_ICNT)
            obj.C_n.pack_into(obj.buffer, UNITS)
            obj.C_n.pack_into(obj.buffer, UNITS_IN)
            obj.C_n.pack_into(obj.buffer, C_RESFMT)
            obj.C_n.pack_into(obj.buffer, C_LLMFMT)
            obj.C_n.pack_into(obj.buffer, C_HLMFMT)
            obj.R_4.pack_into(obj.buffer, LO_SPEC)
            obj.R_4.pack_into(obj.buffer, HI_SPEC)

        self.write_fields(15, 15, write_fields)

    def FTR(
        self,
        TEST_NUM: int,
        HEAD_NUM: int,
        SITE_NUM: int,
        TEST_FLG: bytes,
        OPT_FLAG: bytes,
        CYCL_CNT: int = 0,
        REL_VADR: int = 0,
        REPT_CNT: int = 0,
        NUM_FAIL: int = 0,  #
        XFAIL_AD: int = 0,
        YFAIL_AD: int = 0,
        VECT_OFF: int = 0,
        RTN_ICNT: int = 0,
        PGM_ICNT: int = 0,
        RTN_INDX: Sequence[int] = tuple(),
        RTN_STAT: Sequence[int] = tuple(),
        PGM_INDX: Sequence[int] = tuple(),
        PGM_STAT: Sequence[int] = tuple(),
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
    ) -> None:
        """Functional Test Record (FTR)

        Contains the results of the single execution of a functional test in the test program. The
        first occurrence of this record also establishes the default values for all semi-static
        information about the test.

        Note:
            One or more for each execution of a functional test.

        Args:
            TEST_NUM (int): Test number.
            HEAD_NUM (int): Test head number.
            SITE_NUM (int): Test site number.
            TEST_FLG (int): Test flags (fail, alarm, etc.).
            OPT_FLAG (int): Optional data flag.
            CYCL_CNT (int): Cycle count of vector. Defaults to 0.
            REL_VADR (int): Relative vector address. Defaults to 0.
            REPT_CNT (int): Repeat count of vector. Defaults to 0.
            NUM_FAIL (int): Number of pins with 1 or more failures. Defaults to 0.
            XFAIL_AD (int): X logical device failure address. Defaults to 0.
            YFAIL_AD (int): Y logical device failure address. Defaults to 0.
            VECT_OFF (int): Offset from vector of interest. Defaults to 0.
            RTN_ICNT (int): Count (j) of return data PMR indexes. Defaults to 0.
            PGM_ICNT (int): Count (k) of programmed state indexes. Defaults to 0.
            RTN_INDX (Sequence[int]): Array of return data PMR indexes. Defaults to tuple().
            RTN_STAT (Sequence[int]): Array of returned states. Defaults to tuple().
            PGM_INDX (Sequence[int]): Array of programmed state indexes. Defaults to tuple().
            PGM_STAT (Sequence[int]): Array of programmed states. Defaults to tuple().
            FAIL_PIN (bytes): Failing pin bitfield. Defaults to b"".
            VECT_NAM (str): Vector module pattern name. Defaults to "".
            TIME_SET (str): Time set name. Defaults to "".
            OP_CODE (str): Vector Op Code. Defaults to "".
            TEST_TXT (str): Descriptive text or label. Defaults to "".
            ALARM_ID (str): Name of alarm. Defaults to "".
            PROG_TXT (str): Additional programmed information. Defaults to "".
            RSLT_TXT (str): Additional result information. Defaults to "".
            PATG_NUM (int): Pattern generator number. Defaults to 255.
            SPIN_MAP (bytes): Bit map of enabled comparators. Defaults to b"".
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_4.pack_into(obj.buffer, TEST_NUM)
            obj.U_1.pack_into(obj.buffer, HEAD_NUM)
            obj.U_1.pack_into(obj.buffer, SITE_NUM)
            obj.B_1.pack_into(obj.buffer, TEST_FLG)
            obj.B_1.pack_into(obj.buffer, OPT_FLAG)
            obj.U_4.pack_into(obj.buffer, CYCL_CNT)
            obj.U_4.pack_into(obj.buffer, REL_VADR)
            obj.U_4.pack_into(obj.buffer, REPT_CNT)
            obj.U_4.pack_into(obj.buffer, NUM_FAIL)
            obj.I_4.pack_into(obj.buffer, XFAIL_AD)
            obj.I_4.pack_into(obj.buffer, YFAIL_AD)
            obj.I_2.pack_into(obj.buffer, VECT_OFF)
            obj.U_2.pack_into(obj.buffer, RTN_ICNT)
            obj.U_2.pack_into(obj.buffer, PGM_ICNT)
            obj.kxU_2.pack_into(obj.buffer, RTN_INDX, size=RTN_ICNT)
            # obj.kx_N1.pack_into(obj.buffer, RTN_STAT, size=RTN_ICNT) # TODO: fix this
            obj.kxU_2.pack_into(obj.buffer, PGM_INDX, size=PGM_ICNT)
            # obj.kx_N1.pack_into(obj.buffer, PGM_STAT, size=PGM_ICNT) # TODO: fix this
            # obj.D_n.pack_into(obj.buffer, FAIL_PIN) # TODO: fix this
            obj.C_n.pack_into(obj.buffer, VECT_NAM)
            obj.C_n.pack_into(obj.buffer, TIME_SET)
            obj.C_n.pack_into(obj.buffer, OP_CODE)
            obj.C_n.pack_into(obj.buffer, TEST_TXT)
            obj.C_n.pack_into(obj.buffer, ALARM_ID)
            obj.C_n.pack_into(obj.buffer, PROG_TXT)
            obj.C_n.pack_into(obj.buffer, RSLT_TXT)
            obj.U_1.pack_into(obj.buffer, PATG_NUM)
            # obj.D_n.pack_into(obj.buffer, SPIN_MAP) # TODO: fix this

        self.write_fields(15, 20, write_fields)

    def BPS(
        self,
        SEQ_NAME: str = "",
    ) -> None:
        """Begin Program Section Record (BPS)

        Marks the beginning of a new program section (or sequencer) in the job plan.

        Note:
            Anywhere after the PIR and before the PRR.

        Args:
            SEQ_NAME (str): Program section (or sequencer) name. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.C_n.pack_into(obj.buffer, SEQ_NAME)

        self.write_fields(20, 10, write_fields)

    def EPS(
        self,
    ) -> None:
        """End Program Section Record (EPS)

        Marks the end of the current program section (or sequencer) in the job plan.

        Note:
            Following the corresponding BPS and before the PRR in the data stream.
        """

        def write_fields(obj: "StdfPacker"):
            return

        self.write_fields(20, 20, write_fields)

    def GDR(
        self,
        FLD_CNT: int = 0,
        GEN_DATA: Sequence[Any] = tuple(),
    ) -> None:
        """Generic Data Record (GDR)

        Contains information that does not conform to any other record type defined by the
        STDF specification. Such records are intended to be written under the control of job
        plans executing on the tester.

        Note:
            A test data file may contain any number of GDRs.

        Args:
            FLD_CNT (int): Count of data fields in record. Defaults to 0.
            GEN_DATA (list[tuple[int, bytes]]): Data type code and data for one field. Defaults to None.
        """

        def write_fields(obj: "StdfPacker"):
            obj.U_2.pack_into(obj.buffer, FLD_CNT)
            # obj.V_n.pack_into(obj.buffer, GEN_DATA) # TODO: fix this

        self.write_fields(50, 10, write_fields)

    def DTR(
        self,
        TEXT_DAT: str = "",
    ) -> None:
        """Datalog Text Record (DTR)

        Contains text information that is to be included in the datalog printout. DTRs may be
        written under the control of a job plan: for example, to highlight unexpected test
        results. They may also be generated by the tester executive software.

        Note:
            A test data file may contain any number of DTRs.

        Args:
            TEXT_DAT (str): ASCII text string. Defaults to "".
        """

        def write_fields(obj: "StdfPacker"):
            obj.C_n.pack_into(obj.buffer, TEXT_DAT)

        self.write_fields(50, 30, write_fields)
