#import "../config.typ": template, tufted, site-intro, site-latest-count, latest-posts
#import "_data/posts.typ": posts

#show: template.with(intro: site-intro)

#latest-posts(posts)
