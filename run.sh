#!/bin/sh
workon newslynx-core
while :
do
  echo "articles"
  nlc articles
  echo "fb page stats"
  nlc facebook_page_stats
  echo "fb pages"
  nlc facebook_pages
  echo "google alerts"
  nlc galerts
  echo "homepages"
  nlc homepages
  echo "twitter lists"
  nlc twitter_lists
  echo "twitter_search"
  nlc twitter_search
  echo "twitter_user_stats"
  nlc twitter_user_stats
  echo "twitter users"
  nlc twitter_users
  echo "sleeping"
  sleep 10m 
done
