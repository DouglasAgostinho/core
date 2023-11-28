#------------------------------------------------------
# Project commom section
#
# Message type codes (m_type) variable
# 0x - Messages with confirmation
# 01 - user input
# 02 - file
# 03 - confirmation / close message
# 2x - Messages without confirmation (requests)
#
# Received messages should starts as below
# 02 char of message type
# 14 char for message length
# 64 char for message hash (SHA-512)
# 
#------------------------------------------------------