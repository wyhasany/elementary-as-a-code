Firstly to configure new Elementary Juno installation run:

```
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt-get install ansible
$ ansible-galaxy install bendews.cloudflared
```

Then install all default apps and configurations by:

```
ansible-playbook ubuntu-playbook.yml
```

Playbook already tested, works flawlessly:
autostart.yml
chrome.yml
dropbox.yml
flatpak.yml
fusuma.yml
wingpanel-ayatana.yml
wireshark-installation.yml
yubikey.yml
keepassxc.yml

Playbook with issues:
caprine.yml (the snap probably do not work correctly inside juno)
dns-over-https.yml (works unstable changes needed in role)
