import urlpath


def give_domain(domain, /, post_or_posts):
    if isinstance(post_or_posts, list):
        posts = post_or_posts
        for post in posts:
            if isinstance(post, dict):
                post["url"] = str(urlpath.URL(domain) / post["url"])
            else:
                post.url = str(urlpath.URL(domain) / post.url)
        return posts
    post = post_or_posts
    if isinstance(post, dict):
        post["url"] = str(urlpath.URL(domain) / post["url"])
        return post
    post.url = str(urlpath.URL(domain) / post.url)
    return post
