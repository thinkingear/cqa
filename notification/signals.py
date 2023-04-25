# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.contenttypes.models import ContentType
#
# from qa.models import Question, Answer, QuestionFollower, AnswerFollower
# from pubedit.models import Article, ArticleFeed, ArticleFollower
# from course.models import Course, Video, CourseFollower, VideoFollower
#
#
# for content in [Answer, ArticleFeed, Video]:
#     def create_content_follow_notification(sender, instance, created, **kwargs):
#         if created:  # 如果对象已存在（即更新操作）
#             if content == Answer:
#                 content_type = ContentType.objects.get_for_model(model=Question)
#                 content_id = instance.question.id
#             elif content == ArticleFeed:
#                 content_type = ContentType.objects.get_for_model(model=Article)
#                 content_id = instance.article.id
#             elif content == Video:
#                 content_type = ContentType.objects.get_for_model(model=Course)
#                 content_id = instance.section.course.id
#             ContentFollowNotification.objects.create(
#                 content_type=content_type,
#                 content_id=content_id
#             )
#
#
# for content in [Question, Answer, Article, Course]:
#     @receiver(post_save, sender=content)
#     def create_account_follow_post_notification(sender, instance, created, **kwargs):
#         if created:  # 如果是新对象（即创建操作）
#             content_type = ContentType.objects.get_for_model(model=content)
#             AccountFollowNotification.objects.create(
#                 content_type=content_type,
#                 content_id=instance.id,
#                 action='post',
#             )
#
#
# # @receiver(post_save, sender=Vote)
# # def create_account_follow_upvote_notification(sender, instance, created, **kwargs):
# #     if created and instance.vote == 1:  # 如果是新对象（即创建操作）
# #         AccountFollowNotification.objects.create(
# #             followed=instance.voter,
# #             content_type=instance.content_type,
# #             content_id=instance.content_id,
# #             action='upvote',
# #         )
#
#
# for content_follow in [QuestionFollower, AnswerFollower, ArticleFollower, CourseFollower, VideoFollower]:
#     @receiver(post_save, sender=content_follow)
#     def create_account_follow_content_follow_notification(sender, instance, created, **kwargs):
#         if created:
#             if content_follow == QuestionFollower:
#                 content_type = ContentType.objects.get_for_model(model=Question)
#                 content_id = instance.question.id
#             elif content_follow == AnswerFollower:
#                 content_type = ContentType.objects.get_for_model(model=Answer)
#                 content_id = instance.answer.id
#             elif content_follow == ArticleFollower:
#                 content_type = ContentType.objects.get_for_model(model=Article)
#                 content_id = instance.article.id
#             elif content_follow == CourseFollower:
#                 content_type = ContentType.objects.get_for_model(model=Course)
#                 content_id = instance.course.id
#             elif content_follow == QuestionFollower:
#                 content_type = ContentType.objects.get_for_model(model=Video)
#                 content_id = instance.video.id
#
#             AccountFollowNotification.objects.create(
#                 action='follow',
#                 followed=instance.follower,
#                 content_type=content_type,
#                 content_id=content_id,
#             )
