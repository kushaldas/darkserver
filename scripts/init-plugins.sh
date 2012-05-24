#!/bin/sh

IMM_VER=0.7.2
NOIR_VER=1.2.1

if [ -z "$LEIN" ];
then
    LEIN=$(which lein)
fi

LEIN_VER=$($LEIN version | cut -d\  -f2 | cut -d. -f1)


if [ $LEIN_VER -ge 2 ];
then
    echo Using Leiningen 2
    echo add the following to ~/.lein/profiles.clj :
    echo "{:user {:plugins [[lein-immutant \"$IMM_VER\"]"
    echo "                  [lein-noir \"$NOIR_VER\"]]}}"
else
    echo Using Leiningen 1
    lein plugin install lein-immutant $IMM_VER
    lein plugin install lein-noir $NOIR_VER
fi
