# `FastBlog` version roadmap

**Note:** This file is the overview of the upcoming versions
and features within them of the project,
the full changes will be in changelog and GitHub release notes.

----
## Versions
### `v0.1.0` to `v0.9.x`
These are the in-development versions of the blog, nothing is completed yet.

----
### `v1.0.0`
In this version, the basic API of the blog is written, no advance feature is implemented.
Available features:
- Blog Posts
  - Create/Read/Update/Delete blog posts.


----
### `v2.0.0`
Users will come to the blog. Now a user can create an account and do post CRUD on his/her account.
- User accounts
  - Account creation.
  - Authorize with JWT tokens
  - accessing the limited resources through authorization.
    This means, users can:
      - create a post
      - see their post
      - update their post
      - delete their post

       there is no mechanism for publishing the posts.

#### `2.1.0`
Draft posts will be available.

with this release, users can write some of the post,
and save it in drafts, then edit and publish it later.

#### `2.2.0`
Publishing the posts will be available.

With this release, users can publish their posts and
respectively other users can use the global link of posts
and get the post.
----
### `v3.0.0`
A tag system will be added to the posts.

With this feature posts can be:
- tagged with at least one and at most five tags.
- posts can be organised, filtered and searched through tags.

**Note:** with this feature, a post recommendation can be implemented in the future versions.

----
### `v4.0.0`
Post recommendation system will be implemented.

Now the most recent posts with similarities in tags will be shown to the user.

----
### `v5.0.0`
Comments will arrive in this version of `FastBlog`.

Now users can comment on each other's posts.

----
_This file will be updated_
