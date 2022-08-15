#!/bin/bash
if ! grep -e '\bSSHPASS' ~/.bashrc; then
    echo "export SSHPASS='\$pl3nd1D'" >> ~/.bashrc
fi

# echo "export SSHPASS=\'$pl3nd1D\'" | tee -a ~/.bashrcv
