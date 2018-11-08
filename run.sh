#!/bin/bash

sudo apt-get update
sudo apt-get install software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install ansible -y
ansible-galaxy install bendews.cloudflared
ansible-playbook ubuntu-playbook.yml --user="$USER" --ask-sudo-pass