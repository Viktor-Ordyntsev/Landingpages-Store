#!/bin/bash
if [[ $BRANCH_NAME = *[![:ascii:]]* ]]; then
  echo $BRANCH_NAME | idn > /tmp/punycode
else 
  echo $BRANCH_NAME > /tmp/punycode
fi 

echo $BRANCH_NAME > /tmp/non_idn
