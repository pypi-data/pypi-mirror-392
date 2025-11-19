import pytest
from pyqcisim.QCIS_parser import QCISParser
from pyqcisim.QCIS_inst import QCISInst, QCISOpCode


class TestQCISParser:
    def test_single_inst(self):
        parser = QCISParser()

        success, instructions, qubit_names = parser.parse("CZ Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.CZ, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("MEASURE Q1")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.MEASURE, qubits_list=["Q1"])]
            and qubit_names == ["Q1"]
        )
        success, instructions, qubit_names = parser.parse("MEASURE Q10 Q11 Q12")
        assert success == True and instructions == [
            QCISInst(QCISOpCode.MEASURE, qubits_list=["Q10", "Q11", "Q12"])
        ]

        success, instructions, qubit_names = parser.parse("M Q1")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.M, qubits_list=["Q1"])]
            and qubit_names == ["Q1"]
        )
        success, instructions, qubit_names = parser.parse("M Q10 Q11 Q12")
        assert success == True and instructions == [
            QCISInst(QCISOpCode.M, qubits_list=["Q10", "Q11", "Q12"])
        ]

        success, instructions, qubit_names = parser.parse("RZ Q3 1.3")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.RZ, qubit="Q3", azimuth=1.3)]
            and qubit_names == ["Q3"]
        )

        success, instructions, qubit_names = parser.parse("XYARB Q4 0 3.14")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.XYARB, qubit="Q4", azimuth=0, altitude=3.14)]
            and qubit_names == ["Q4"]
        )

        success, instructions, qubit_names = parser.parse("XY Q4 0")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.XY, qubit="Q4", azimuth=0)]
            and qubit_names == ["Q4"]
        )

        success, instructions, qubit_names = parser.parse("XY2P Q4 0.1")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.XY2P, qubit="Q4", azimuth=0.1)]
            and qubit_names == ["Q4"]
        )

        success, instructions, qubit_names = parser.parse("XY2M Q4 0.1")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.XY2M, qubit="Q4", azimuth=0.1)]
            and qubit_names == ["Q4"]
        )

        success, instructions, qubit_names = parser.parse("X Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.X, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("X2P Q6")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.X2P, qubit="Q6")]
            and qubit_names == ["Q6"]
        )

        success, instructions, qubit_names = parser.parse("X2M Q7")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.X2M, qubit="Q7")]
            and qubit_names == ["Q7"]
        )

        success, instructions, qubit_names = parser.parse("Y Q8")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Y, qubit="Q8")]
            and qubit_names == ["Q8"]
        )

        success, instructions, qubit_names = parser.parse("Y2P Q9")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Y2P, qubit="Q9")]
            and qubit_names == ["Q9"]
        )

        success, instructions, qubit_names = parser.parse("Y2M Q10")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Y2M, qubit="Q10")]
            and qubit_names == ["Q10"]
        )

        success, instructions, qubit_names = parser.parse("Z Q11")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Z, qubit="Q11")]
            and qubit_names == ["Q11"]
        )

        success, instructions, qubit_names = parser.parse("Z2P Q12")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Z2P, qubit="Q12")]
            and qubit_names == ["Q12"]
        )

        success, instructions, qubit_names = parser.parse("Z2M Q13")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Z2M, qubit="Q13")]
            and qubit_names == ["Q13"]
        )

        success, instructions, qubit_names = parser.parse("Z4P Q14")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Z4P, qubit="Q14")]
            and qubit_names == ["Q14"]
        )

        success, instructions, qubit_names = parser.parse("Z4M Q15")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.Z4M, qubit="Q15")]
            and qubit_names == ["Q15"]
        )

        success, instructions, qubit_names = parser.parse("S Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.S, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("SD Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.SD, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("T Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.T, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("TD Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.TD, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("H Q5")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.H, qubit="Q5")]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("RX Q5 -0.55")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.RX, qubit="Q5", altitude=-0.55)]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("RY Q5 -0.55")
        assert (
            success == True
            and instructions == [QCISInst(QCISOpCode.RY, qubit="Q5", altitude=-0.55)]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("RXY Q5 1.1 -0.55")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.RXY, qubit="Q5", azimuth=1.1, altitude=-0.55)]
            and qubit_names == ["Q5"]
        )

        success, instructions, qubit_names = parser.parse("CNOT Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.CNOT, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("SWP Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.SWP, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("SSWP Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.SSWP, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("ISWP Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.ISWP, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("SISWP Q1 Q2")
        assert (
            success == True
            and instructions
            == [QCISInst(QCISOpCode.SISWP, control_qubit="Q1", target_qubit="Q2")]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("CP Q1 Q2 -0.5")
        assert (
            success == True
            and instructions
            == [
                QCISInst(
                    QCISOpCode.CP, control_qubit="Q1", target_qubit="Q2", azimuth=-0.5
                )
            ]
            and qubit_names == ["Q1", "Q2"]
        )

        success, instructions, qubit_names = parser.parse("FSIM Q1 Q2 0.5")
        assert (
            success == True
            and instructions
            == [
                QCISInst(
                    QCISOpCode.FSIM, control_qubit="Q1", target_qubit="Q2", azimuth=0.5
                )
            ]
            and qubit_names == ["Q1", "Q2"]
        )

    def test_cz_coupler_format(self):
        """Test new CZ instruction format with coupler (e.g., CZ G2827)"""
        parser = QCISParser()

        # Test single CZ with coupler format
        success, instructions, qubit_names = parser.parse("CZ G2827")
        assert success == True
        assert len(instructions) == 1
        inst = instructions[0]
        assert inst.op_code == QCISOpCode.CZ
        assert inst.control_qubit == "Q28"
        assert inst.target_qubit == "Q27"
        assert inst.coupler == "G2827"
        assert qubit_names == ["Q27", "Q28"]
        assert inst.dump() == "CZ G2827"

        # Test another coupler
        success, instructions, qubit_names = parser.parse("CZ G2625")
        assert success == True
        assert len(instructions) == 1
        inst = instructions[0]
        assert inst.op_code == QCISOpCode.CZ
        assert inst.control_qubit == "Q26"
        assert inst.target_qubit == "Q25"
        assert inst.coupler == "G2625"
        assert qubit_names == ["Q25", "Q26"]
        assert inst.dump() == "CZ G2625"

        # Test with different qubit indices
        success, instructions, qubit_names = parser.parse("CZ G0001")
        assert success == True
        inst = instructions[0]
        assert inst.control_qubit == "Q00"
        assert inst.target_qubit == "Q01"
        assert inst.coupler == "G0001"
        assert inst.dump() == "CZ G0001"

    def test_cz_mixed_formats(self):
        """Test that old and new CZ formats can coexist"""
        parser = QCISParser()

        # Program with both old and new CZ formats
        prog = "Y2M Q28\nCZ G2827\nY2P Q28\nY2M Q25\nCZ Q25 Q26\nY2P Q25\nM Q25 Q26 Q27 Q28"
        success, instructions, qubit_names = parser.parse(prog)

        assert success == True
        assert len(instructions) == 7

        # Check first CZ (new format with coupler)
        cz1 = instructions[1]
        assert cz1.op_code == QCISOpCode.CZ
        assert cz1.control_qubit == "Q28"
        assert cz1.target_qubit == "Q27"
        assert cz1.coupler == "G2827"
        assert cz1.dump() == "CZ G2827"

        # Check second CZ (old format without coupler)
        cz2 = instructions[4]
        assert cz2.op_code == QCISOpCode.CZ
        assert cz2.control_qubit == "Q25"
        assert cz2.target_qubit == "Q26"
        assert not hasattr(cz2, "coupler") or cz2.coupler is None
        assert cz2.dump() == "CZ Q25 Q26"

        assert qubit_names == ["Q25", "Q26", "Q27", "Q28"]

    def test_cz_coupler_in_complex_program(self):
        """Test CZ coupler format in a realistic quantum program"""
        parser = QCISParser()

        prog = """Y2M Q25
RZ Q25 3.1415927
Y2M Q27
RZ Q27 3.1415927
Y2M Q28
RZ Q28 3.1415927
B G2625 G2827 Q25 Q26 Q27 Q28 R05
Y2M Q28
CZ G2827
Y2P Q28
Y2M Q26
CZ G2625
Y2P Q26
B G2625 G2827 Q25 Q26 Q27 Q28 R05
M Q25
M Q26"""

        success, instructions, qubit_names = parser.parse(prog)
        assert success == True
        assert len(instructions) == 16

        # Find and verify CZ instructions
        cz_instructions = [
            inst for inst in instructions if inst.op_code == QCISOpCode.CZ
        ]
        assert len(cz_instructions) == 2

        # First CZ: G2827 -> Q28, Q27
        assert cz_instructions[0].control_qubit == "Q28"
        assert cz_instructions[0].target_qubit == "Q27"
        assert cz_instructions[0].coupler == "G2827"
        assert cz_instructions[0].dump() == "CZ G2827"

        # Second CZ: G2625 -> Q26, Q25
        assert cz_instructions[1].control_qubit == "Q26"
        assert cz_instructions[1].target_qubit == "Q25"
        assert cz_instructions[1].coupler == "G2625"
        assert cz_instructions[1].dump() == "CZ G2625"

    def test_multi_inst(self):
        parser = QCISParser()
        prog = "X Q10\nS Q20\nCZ Q10 Q20\nXY Q30 -1\nCNOT Q10 Q20\nM Q20 Q30"
        success, instructions, qubit_names = parser.parse(prog)
        assert (
            success == True
            and instructions
            == [
                QCISInst(QCISOpCode.X, qubit="Q10"),
                QCISInst(QCISOpCode.S, qubit="Q20"),
                QCISInst(QCISOpCode.CZ, control_qubit="Q10", target_qubit="Q20"),
                QCISInst(QCISOpCode.XY, qubit="Q30", azimuth=-1),
                QCISInst(QCISOpCode.CNOT, control_qubit="Q10", target_qubit="Q20"),
                QCISInst(QCISOpCode.M, qubits_list=["Q20", "Q30"]),
            ]
            and qubit_names == ["Q10", "Q20", "Q30"]
        )

    def test_complex_seperator(self):
        parser = QCISParser()
        prog = "X2P  Q20 \n MEASURE \t\t Q100\tQ200\n\nCZ Q10 Q20"
        success, instructions, qubit_names = parser.parse(prog)
        assert (
            success == True
            and instructions
            == [
                QCISInst(QCISOpCode.X2P, qubit="Q20"),
                QCISInst(QCISOpCode.MEASURE, qubits_list=["Q100", "Q200"]),
                QCISInst(QCISOpCode.CZ, control_qubit="Q10", target_qubit="Q20"),
            ]
            and qubit_names == ["Q10", "Q100", "Q20", "Q200"]
        )

    def test_syntax_error(self):
        parser = QCISParser()
        # QCIS program with an error at the end
        prog = "X Q10\nY Q20\nCZ Q10 Q20\nXYARB Q30 1.2"
        success, instructions, qubit_names = parser.parse(prog)
        assert (
            success == False
            and instructions
            == [
                QCISInst(QCISOpCode.X, qubit="Q10"),
                QCISInst(QCISOpCode.Y, qubit="Q20"),
                QCISInst(QCISOpCode.CZ, control_qubit="Q10", target_qubit="Q20"),
            ]
            and qubit_names == ["Q10", "Q20"]
        )
        assert parser.error_list == ["Syntax error at the end of program."]

        # QCIS program with an error in the middle
        prog = "X Q10\nY Q20\nCZ Q10 Q15 Q20\nMEASURE Q99\n"
        success, instructions, qubit_names = parser.parse(prog)
        assert (
            success == False
            and instructions
            == [
                QCISInst(QCISOpCode.X, qubit="Q10"),
                QCISInst(QCISOpCode.Y, qubit="Q20"),
                QCISInst(QCISOpCode.MEASURE, qubits_list=["Q99"]),
            ]
            and qubit_names == ["Q10", "Q20", "Q99"]
        )
        assert parser.error_list == [
            "Syntax error: Found unmatched QREG at (3, 12).\nSkip line 3: CZ Q10 Q15 Q20"
        ]

        prog = "X Q10\nY Q20\nCZ Q10 Q20\nXYARB Q30 1.2 -1\nCZ 1.R9 Q100\n"
        success, instructions, qubit_names = parser.parse(prog)
        print(instructions)
        assert not success
        assert parser.error_list == [
            "Syntax error: Found unmatched FLOAT at (5, 4).\nSkip line 5: CZ 1.R9 Q100"
        ]

        # QCIS program with an error at the beginning
        prog = "Q10\nY Q20\nCZ Q10 Q20\nMEASURE Q99\n"
        success, instructions, qubit_names = parser.parse(prog)
        assert (
            success == False
            and instructions
            == [
                QCISInst(QCISOpCode.Y, qubit="Q20"),
                QCISInst(QCISOpCode.CZ, control_qubit="Q10", target_qubit="Q20"),
                QCISInst(QCISOpCode.MEASURE, qubits_list=["Q99"]),
            ]
            and qubit_names == ["Q10", "Q20", "Q99"]
        )
        assert parser.error_list == [
            "Syntax error: Found unmatched QREG at (1, 1).\nSkip line 1: Q10"
        ]
