#!/usr/bin/env bash
if [ $# -eq 0 ];
    then
        echo "$0 <hostname or ip to deploy to>"
        exit
fi

echo "**** Starting deloyment ****"

echo "Updating hermod.py with deployment hostname or IP address"
sed -i .bak -E "s/^IPADDRESS=.*/IPADDRESS='$1'/g" hermod.py

echo "Creating tar file..."
tar cf fsoapi.tar hermod.py README favicon.ico run_fsoapi.sh

echo "Removing remote directory (hermod.d)"
ssh -q -l ixoperator $1 rm -rf hermod.d

echo "Creating remote directory (hermod.d)"
ssh -q -l ixoperator $1 mkdir hermod.d

echo "Copying tar file to remote directory"
scp -q fsoapi.tar ixoperator@$1:hermod.d

echo "Extracting tar file"
ssh -q -l ixoperator $1 "cd ~/hermod.d;tar -xf fsoapi.tar"

echo "Removing tar file"
ssh -q -l ixoperator $1 rm -f hermod.d/fsoapi.tar

echo "Running hermod startup script at $1"
ssh -q -l ixoperator $1 "cd hermod.d;./run_fsoapi.sh"

echo "Removing local tar file"
rm -f fsoapi.tar

echo "Restore original hermod.py"
cp hermod.py.bak hermod.py
rm -f hermod.py.bak

echo "**** Deployment done ****"

