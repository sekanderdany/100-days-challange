#! /bin/bash

echo "setup and configure server"

file_name=config.yaml

config_dir=$1

if [ -d "$config_dir" ]
then
    echo "reading config directory contents"
    config_files=$(ls "$config_dir")
else
    echo "config dir not found. creating one"
    mkdir "$config_dir"
    touch "$config_dir/config.sh"
fi

user_group=$2

if [ "$user_group" == "ubuntu" ]
then
  echo "configure the server"
elif [ "$user_group" == "admin" ]
then
  echo "administer the serever"
else
  echo "No permission to configure server. wrong user group"
fi


echo="using file $file_name to configuire something"

echo "here are all the configuration files: $config_files"
