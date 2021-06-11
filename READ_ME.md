Please do all the following before attempting to run the game.

Setup Notes:
1. Go to the link below and download all of the game's assets:

https://drive.google.com/drive/folders/1Rt2-ZWoYuCMdCxyPQ4p7dl78H0udm0Fy?usp=sharing 

2. place 'fonts', 'images', and 'music' into the same directory as the .py files here

3. If it is your first time playing. Be sure there is no existing file named "records.txt" in the directory
   as this will crash the game. records is a very basic save file that is read when loading up the game. 
   When the game loads the first time, Tris creates a records.txt that will be used from
   then on and will keep track of your progress through the game.
   
4. That's it! go ahead and run TrisApplet.py to load up the game! Please be sure you have pygame installed.

Disclaimer (June 2021):
It has not been tested so far, but you will likely need to use pygame 2 found here:
https://github.com/pygame/pygame/releases/tag/2.0.0
as it is backwards compatible with all pygame applications and does not encounter dependencies between the old 
pygame 1 and Python 3.9.
In moving Tris to this repository, we found that pygame's mixer library relating to sound-file reading may only 
function correctly on applications using at latest Python 2.7. A further disclaimer will be added if we find
that converting to pygame 2 causes the noted sound issues to be fixed when using the most up-to-date versions
of Python.
