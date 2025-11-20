Value Required PORT ([\d\/]+)


Start
  ^\| ${PORT}\s+\| -> Record

#+------------------------------------------------------------- TRANSCEIVER STATUS ---------------------------------------------------------------------------------+
#|      |Admin| Oper  |                                         |     Ether Medium &        |        |              |  Baud  |Bit-Rate |         |             |    |
#| Port |State| State |       Vendor Name & Part Number         |     Connector Type        | Type   |     Mode     |(GBaud) | (Gbps)  | TM-Type |Constellation|Diag|
#+------+-----+-------+-----------------------------------------+---------------------------+--------+--------------+--------+---------+---------+-------------+----+
#| 1/1  | Ena |Up     |Ciena WL6e Transceiver                   |WL6e-1600G-OTN:LC          |WL6e    |Tunable       |200.0   |1600     |Ethernet |Shaped       |Yes |
#| 1/2  | Ena |Up     |Ciena WL6e Transceiver                   |WL6e-1600G-OTN:LC          |WL6e    |Tunable       |200.0   |1600     |Ethernet |Shaped       |Yes |
#| 1/3  | Ena |Up     |Ciena 160-9600-900 Rev005                |400G-FR4:LC                |QSFP-DD |400GE         |        |         |         |             |Yes |