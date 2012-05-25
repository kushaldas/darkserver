#!/bin/sh

IMM_VER=0.7.2
NOIR_VER=1.2.1
SWANK_VER=1.4.4

if [ -z "$LEIN" ];
then
    LEIN=$(which lein)
fi

LEIN_VER=$($LEIN version | cut -d\  -f2 | cut -d. -f1)


if [ $LEIN_VER -ge 2 ];
then
    echo Using Leiningen 2
    echo \'$LEIN plugin\' is now deprecated, but
    echo you can copy the :plugins section of project.clj
    echo to ~/.lein/profiles.clj :
    echo "{:user {:plugins [[lein-immutant \"$IMM_VER\"]"
    echo "                  [lein-noir \"$NOIR_VER\"]"
    echo "                  [lein-swank \"$SWANK_VER\"]]}}"
else
    $LEIN plugin install lein-immutant $IMM_VER
    $LEIN plugin install lein-noir $NOIR_VER
    $LEIN plugin install lein-swank $SWANK_VER
fi

