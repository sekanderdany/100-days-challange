#!/bin/bash


#echo "all params: $*"
#echo "number of params: $#"

for param in $*
  do
    if [ -d "$param" ]
    then
      echo "executing scripts in the config folder"
      ls -l "$param"
    fi
    echo $param
  done

function score_sum() {
  sum=0

  while true
  do
    read -p "enter a score: " score

    if [ "$score" == "q" ]
    then
      break
    fi

    sum=$(($sum+score))
    echo "total score: $sum"

  done
}

function create_file() {
  file_name=$1
  is_shell_script=$2
  touch $file_name
  echo "file $file_name" created

  if [ "$is_shell_script" = true ]
  then
    echo "providing permission"
    chmod u+x $file_name
  fi
}


create_file test.txt
create_file myfile.yaml
create_file myscript.sh true

function sum() {
  total=$(($1+$2))
  return $total
}

sum 2 10
result=$?

echo "sum of 2 and 10 is $result"

# score_sum
