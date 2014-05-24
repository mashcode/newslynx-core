#!/bin/sh
*/5 * * * * * nlc galerts
4,34 * * * * * nlc articles
8,38 * * * * * * nlc twitter_user_stats
12,42 * * * * * * nlc twitter_users
16,46 * * * * * nlc twitter_lists
20,50 * * * * * nlc homepages
24,54 * * * * * nlc facebook_page_stats
28,58 * * * * * nlc facebook_pages
@reboot /usr/local/bin/forever start /nlc twitter_stream