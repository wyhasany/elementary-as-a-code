[![Build Status](https://travis-ci.com/wyhasany/elementary-as-a-code.svg?branch=master)](https://travis-ci.com/wyhasany/elementary-as-a-code)

This script configures fresh installation of Elementary OS Juno as well
as any linux distribution based on Ubuntu Bionic. All pre-installed
applications you can find under playbooks directory. As well you can
customize which application would you like to pre-install on your
system.

Firstly to configure new Elementary Juno installation run:

```
sudo apt-get update &&\
sudo apt-get install software-properties-common git -y &&\
sudo apt-add-repository --yes --update ppa:ansible/ansible &&\
sudo apt-get install ansible -y &&\
ansible-galaxy install bendews.cloudflared &&\
git clone https://github.com/wyhasany/elementary-as-a-code.git &&\
cd elementary-as-a-code
```

Then install all default apps and configurations by:

```
ansible-playbook ubuntu-playbook.yml --user="$USER" --ask-sudo-pass
```

If you would like to miss packages for elementary os use command:
```
ansible-playbook ubuntu-playbook.yml --user="$USER" --ask-sudo-pass --skip-tags elementary-os
```

As well you can just run:

```
./run.sh
```

Playbook already tested, works flawlessly:

```
autostart.yml
chrome.yml
dns-over-https.yml
docker.yml
dropbox.yml
elementary-os-apps.yml
elementary-tweaks.yml
flatpak.yml
fusuma.yml
grub-customizer.yml
idea-shortcuts.yml
java.yml
jetbrains-toolbox.yml (needs one more test)
keepassxc.yml
multimedia-codecs.yml
nord-vpn.yml
plank.yml
qnapi.yml
remmina.yml
sdkman.yml
terminal-tools.yml
utilities.yml
vim.yml
virtualbox.yml
vivaldi.yml
wallpapers.yml
wingpanel-ayatana.yml
wireshark-installation.yml
yakuake.yml
yubikey.yml
zsh.yml
```

If you would like to install KeepassXC with your provided configuration
copy your current keepassxc configuration to keepassxc folder:
```
cp ~/.config/keepassxc/keepassxc.ini playbooks/keepassxc/
```

Playbook with issues:
```
caprine.yml (the snap probably do not work correctly inside juno)
```

