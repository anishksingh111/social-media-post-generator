def post_to_markdown(platform, post):
    return f"""# {platform} Post

## {post.post_title}

**Opening hook:** {post.opening_hook}

## Main caption
{post.main_caption}

## Hashtags
{' '.join(post.hashtags)}

**Call to action:** {post.call_to_action}

## Alternative hooks
""" + "\n".join(f"- {h}" for h in post.alternative_hooks) + f"""

## Short version
{post.short_version}

## Content strategy
{post.content_strategy}
"""
