Value LANE (\d+)
Value Required BIAS ([\.\d]+)
Value Required TX ([\.\d\-]+)
Value Required RX ([\.\d\-]+)

Start
 ^\s+Laser Bias Current = ${BIAS}
 ^\s+Actual TX Power = ${TX} dBm
 ^\s+RX Power = ${RX} dBm -> Record
 # multi-lane optic - based on um iosxr but no scinet example available
 ^\s+${LANE}\s+${BIAS} mA\s+${TX} dBm\s+${RX} dBm\s+N\/A -> Record