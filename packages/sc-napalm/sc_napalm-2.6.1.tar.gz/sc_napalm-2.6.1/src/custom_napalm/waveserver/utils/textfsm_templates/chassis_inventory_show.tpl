Value Required UNIT (\S+)
Value Required MODEL (.+?)
Value Required PN (\S+)
Value Required SN (\S+|see label)

Start
  ^\| ${UNIT}\s+\|.+?\| ${MODEL}\s+\| ${PN}\s+\| ${SN}\s+\| -> Record

# +--------------------------------------- CHASSIS INVENTORY TABLE ------------------------------------------------------------------+
# |         |   Oper    |                                  |                  |                  |        |              |    Mfg    |
# |  Unit   |   State   | Model                            | Part Number      | Serial #         | Rev    | CLEI         |    Date   |
# +---------+-----------+----------------------------------+------------------+------------------+--------+--------------+-----------+
# | Chassis | Up        | Waveserver 5 Chassis             | 186-3001-900     | M997FB4A         | 003    |              | 12/18/23  |
# | CM-1    | Up        | Waveserver 5 Control Processor M | 186-3010-900     | M990009B         | 007    |              | 01/16/24  |
# |         |           | odule                            |                  |                  |        |              |           |
# | 1/3     | Up        | 400G-FR4, SMF, 2KM QSFP-DD       | 160-9600-900     | LUMNTWOBTT000082 | 005    | WMOTC02FAA   | 10/28/24  |