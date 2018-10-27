#!/bis/sh

#Alt+Enter
gsettings list-recursively | grep -iE "'.?alt.?enter'" | awk '//{print $1 " " $2 }' | xargs -I{} gsettings set {} '"[<Super>enter]"'
#Ctrl+Space
gsettings list-recursively | grep -iE "'.?(ctrl|control).?space'" | awk '//{print $1 " " $2 }' | xargs -I{} gsettings set {} '"[]"'
#Ctrl+Shift+Space
gsettings list-recursively | grep -iE "'.?(ctrl|control).?space'" | awk '//{print $1 " " $2 }' | xargs -I{} gsettings set {} '"[]"'
