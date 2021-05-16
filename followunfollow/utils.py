from .models import Follow, BlockList


def unfollow_block(user, id):
    user_follow_list = Follow.objects.get(user = user)
    user_follow_list.follower.remove(id)
    user_follow_list.following.remove(id)
    other_follow_list = Follow.objects.get(user_id = id)
    other_follow_list.following.remove(user)
    other_follow_list.follower.remove(user)


def unblock(user, id):
    user_block = BlockList.objects.get(user = user)
    user_block.blocked.remove(id)
    other_block = BlockList.objects.get(user_id = id)
    other_block.restricted.remove(user)


def unfollow(user, id):
    user_follow_list = Follow.objects.get(user = user)
    user_follow_list.following.remove(id)
    other_follow_list = Follow.objects.get(user_id = id)
    other_follow_list.follower.remove(user)