""" All module are singleton
    To use: # import settings
"""

webssh = { 'host' : 'http://192.168.66.108:8888' }

rdp_tunnel = {
    'host' : '192.168.66.108',
    'user' : 'sshtunnel',
    'pass' : 'sshtunnel'
}

# all test station and project definition.
tss =  [
    { 'ts' : 'log:log@192.168.0.83', 'prjs' : [ 'T6UB', 'RMK_I'] },
    { 'ts' : 'log:log@192.168.0.210', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.211', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.212', 'prjs' : [ 'T6UB', 'T6UC'] },
    { 'ts' : 'log:log@192.168.0.213', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.214', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.215', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.216', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.217', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.218', 'prjs' : [ 'T6UB', 'T6UC','T6UA_2U_MILAN'] }
]

#hop_station = 'cchiang@192.168.66.108'
hop_station = None
