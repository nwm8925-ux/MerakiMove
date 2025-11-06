# MerakiMove
A Cisco Meraki organization clone tool 

Introducing Meraki Move: A Meraki organization move tool meant for easy migration between orgs. 

Prerequisites:

Python3 installed on a Windows Computer with PATH enabled. 

A little bit of Python experience. 

Two Meraki organizations created that meet the following requirements:

At least one device claimed to each organization
At least one network created with said device assigned to it
A working API key

NOTE: On modern Meraki dashboard, it requires one device and one network configured to generate an API key. You will need to manually add a temporary device and create a temporary network to generate the API key. 

Running Meraki Move:

1: In Powershell, run the following in order:

py -m ensurepip --upgrade

pip install requests

pip install meraki

2: Generate and save (if you haven't already) a Meraki API key for each account. 

3: Open GetMerakiOrgID.py in the IDLE editor. Enter your API key, save the file, then press f5 to run this, marking down the org ID printed out in the IDLE window. You will need to do this twice, once for the source org, once for the destination org. 

4: Enter the API keys and org IDs into the top of the MerakiMove.py script using the IDLE editor, making sure to keep the “” around each string of data. 

5: Save the script, and press f5 to run. You will see the migration begin. 

6: When prompted to manually unclaim the devices, unclaim them from the source organization. Once this is done, press enter to continue 

7: The script will prompt you to confirm that you really want to migrate. Type “YES”. 

8: Wait, make some coffee, and enjoy! Migration may take a bit depending on how many devices and networks you have created in your source org. 


KNOWN LIMITATIONS:
MerakiCloud Authentication Users

Captive portal image customization






