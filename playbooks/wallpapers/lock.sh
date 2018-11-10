#!/bin/bash

#Pulpit
ls -Art1 /home/yourusername/.config/variety/Downloaded/Bing | tail -n 1 | xargs -I{} cp /home/yourusername/.config/variety/Downloaded/Bing/{} /usr/share/backgrounds/Ashim\ DSilva.jpg
#Lock screen
ls -Art1 /home/yourusername/.config/variety/Downloaded/Bing | tail -n 1 | xargs -I{} cp /home/yourusername/.config/variety/Downloaded/Bing/{} /var/lib/lightdm-data/yourusername/wallpaper/Ashim\ DSilva.jpg

