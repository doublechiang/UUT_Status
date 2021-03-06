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
    { 'ts' : 'log:log@192.168.0.212', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.213', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.214', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.215', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.216', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.0.217', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.66.66', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.20', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.21', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.22', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.23', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.24', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.25', 'prjs' : [ 'T6UB'] },
    { 'ts' : 'log:log@192.168.59.26', 'prjs' : [ 'T6UB'] }
]

hop_station = 'cchiang@192.168.66.108'
# hop_station = None
