https://www.youtube.com/watch?v=J9-XrRSHrbI
https://www.reddit.com/r/elementaryos/comments/9ked1g/is_there_a_normal_way_to_get_multitouch_touchpad/
https://askubuntu.com/questions/1034624/touchpad-gestures-in-ubuntu-18-04-lts

libinput-gestures:

Installation steps of libinput-gestures:
sudo gpasswd -a $USER input
reboot
sudo apt-get install xdotool wmctrl libinput-tools
git clone https://github.com/bulletmark/libinput-gestures.git
cd libinput-gestures
sudo make install
libinput-gestures-setup autostart
libinput-gestures-setup start

cp libinput-gestures.conf ~/.config/libinput-gestures.conf

+ GUI
sudo apt install python3 python3-setuptools xdotool python3-gi libinput-tools python-gobject
git clone https://gitlab.com/cunidev/gestures.git
cd gestures/
sudo python3 setup.py install

___
Update:
libinput-gestures:
# cd to source dir, as above
git pull
sudo make install
libinput-gestures-setup restart

gestures:
# cd to source dir, as above
git pull
sudo python3 setup.py install

---
To sum up:
three fingers drag works with troubles
pinch seems not to work
four fingers drag works awesome

=================================================================================
Touchegg:

Installation:
git clone https://github.com/JoseExposito/touchegg.git
sudo apt-get build-dep touchegg
sudo apt-get install gtk2-engines-pixbuf
cd touchegg
qmake
make
sudo make install

Touchegg gui:
sudo apt-get install build-essential libqt4-dev libx11-6 libx11-dev
git clone https://github.com/Raffarti/Touchegg-gce
cd Touchegg-gce
mkdir build && cd build
qmake ..
make
sudo make install

---
To sum up:
needs instalation about 100MB of dependencies
wrote down in C++
NOT WORKING AFTER ONE HOOUR OF TRIES

===================================================================================

Unfortunatrely Wayland graphics server (the competitor of X server) doesn't work
under elementaryOS

===================================================================================

Fusuma:

sudo gpasswd -a $USER input 
gsettings set org.gnome.desktop.peripherals.touchpad send-events enabled
restart
sudo apt-get install libinput-tools xdotool
sudo gem install fusuma

configuration:
mkdir -p ~/.config/fusuma 
cp fusuma.yml ~/.config/fusuma/config.yml

----
Update:
sudo gem update fusuma

_
to sum up:
27 MBs of disk space
works smoothly even pinch seems to work correctly

____________________________________________________________________________
Mac style plank:
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:ricotz/docky
sudo apt-get update
sudo apt-get upgrade
killall -9 plank

