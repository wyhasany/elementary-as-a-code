#!/bin/bash

#Pulpit
ls -Art /home/hasan/.config/variety/Downloaded/Bing | xargs -I{} cp /home/hasan/.config/variety/Downloaded/Bing/{} /home/hasan/.local/share/backgrounds/lock.jpg
#Lock screen
ls -Art /home/hasan/.config/variety/Downloaded/Bing | xargs -I{} cp /home/hasan/.config/variety/Downloaded/Bing/{} /var/lib/lightdm-data/hasan/wallpaper/lock.jpg

