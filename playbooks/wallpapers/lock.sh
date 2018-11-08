#!/bin/bash

#Pulpit
ls -Art /home/yourusername/.config/variety/Downloaded/Bing | xargs -I{} cp /home/yourusername/.config/variety/Downloaded/Bing/{} /home/yourusername/.local/share/backgrounds/lock.jpg
#Lock screen
ls -Art /home/yourusername/.config/variety/Downloaded/Bing | xargs -I{} cp /home/yourusername/.config/variety/Downloaded/Bing/{} /var/lib/lightdm-data/yourusername/wallpaper/lock.jpg

