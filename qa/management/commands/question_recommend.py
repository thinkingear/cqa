# import numpy as np
# from django.core.management.base import BaseCommand
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# from qa.models import Question, QuestionFollower
# from core.models import Vote, ContentViewd
# from datetime import datetime
# from account.models import User, AccountFollower
#
#
# def get_question_text(question):
#     return question.title + ' ' + ','.join([tag.name for tag in question.tags.all()])
#
#
# # 获取系统中所有问题文本之间的相似度 DataFrame
# def get_question_all_id_similarity_df():
#     # TF-IDF和相似度计算相关的代码
#     question_all = Question.objects.all()
#     # [{'title': 'How to learn Django?', 'tags': 'cs,django,python'}]
#     question_all_data = [{'question_id': question.id,
#                           'question_text': get_question_text(question)}
#                          for question in question_all]
#
#     question_all_df = pd.DataFrame(question_all_data)
#
#     # 创建一个TF-IDF向量器
#     vectorizer = TfidfVectorizer()
#
#     # 将文本数据转换为TF-IDF矩阵
#     # tfidf_matrix 中，每一行表示一个文档（question），每一列就是一个单词，矩阵中的数据就是某个单词在某个问题中的 tf-idf 值
#     question_all_text_tfidf_matrix = vectorizer.fit_transform(question_all_df['question_text'])
#
#     # 计算 TF-IDF 矩阵中问题之间的相似度
#     # 计算每一个文档向量之间的余弦相似度，假设问题有 n 个，那么 similarity_matrix 就是 n * n 的矩阵（二维列表）
#     # 第 i 行 j 列上的值就是问题 i 与问题 j，通过二者的 tf-idf 向量计算得出的余弦相似度
#     question_all_text_similarity_matrix = cosine_similarity(question_all_text_tfidf_matrix)
#
#     # 将相似度矩阵转换为 DataFrame
#     # question_all_df['id'] 返回的是一个 pandas Series 对象，其中存有所有数据行在 'question_id' 字段上的值
#     question_all_similarity_df = pd.DataFrame(question_all_text_similarity_matrix, index=question_all_df['question_id'], columns=question_all_df['question_id'])
#
#     return question_all_similarity_df
#
#
# WEIGHTS = {
#     'positive_vote': 1.0,
#     'negative_vote': -1.0,
#     'view': 0.5,
#     'follow': 1.5,
#     'post': 2.0,
#     'followed_user_positive_vote': 0.5,
#     'followed_user_negative_vote': -0.5,
#     'followed_user_view': 0.25,
#     'followed_user_follow': 0.75,
#     'followed_user_post': 1,
# }
#
#
# # 获取系统中所有用户与之相关的问题
# # 最终的 user_all_related_questions_df 需要包括 'user_id', 'question_id', 'action', 'action_timestamp' 等字段
# def get_user_all_related_questions_df():
#     user_all_related_questions_data = []
#
#     for user in User.objects.all():
#         # vote
#         for vote in Vote.objects.filter(content_type__model='question', voter=user):
#             votes = vote.vote
#             if votes == 0:
#                 continue
#             user_all_related_questions_data.append({
#                 'user_id': user.id,
#                 'question_id': vote.content_object.id,
#                 'action': 'positive_vote' if votes == 1 else 'negative_vote',
#                 'action_timestamp': vote.updated
#             })
#
#         # view
#         for content_viewed in ContentViewd.objects.filter(user=user, content_type__model='question'):
#             user_all_related_questions_data.append({
#                 'user_id': user.id,
#                 'question_id': content_viewed.content_object.id,
#                 'action': 'view',
#                 'action_timestamp': content_viewed.updated,
#             })
#
#         # post
#         for question in user.question_posted.all():
#             user_all_related_questions_data.append({
#                 'user_id': user.id,
#                 'question_id': question.id,
#                 'action': 'post',
#                 'action_timestamp': question.created,
#             })
#
#         # follow
#         for question_follower in QuestionFollower.objects.filter(follower=user):
#             user_all_related_questions_data.append({
#                 'user_id': user.id,
#                 'question_id': question_follower.question.id,
#                 'action': 'follow',
#                 'action_timestamp': question_follower.created,
#             })
#
#         # followed_user
#
#         for account_follower in AccountFollower.objects.filter(follower=user):
#             followed_user = account_follower.followed
#             # followed_user_positive_vote
#             # followed_user_negative_vote
#             for vote in Vote.objects.filter(content_type__model='question', voter=followed_user):
#                 votes = vote.vote
#                 if votes == 0:
#                     continue
#                 user_all_related_questions_data.append({
#                     'user_id': user.id,
#                     'question_id': vote.content_object.id,
#                     'action': 'followed_user_positive_vote' if votes == 1 else 'followed_user_negative_vote',
#                     'action_timestamp': vote.updated
#                 })
#
#             # followed_user_follow
#             for question_follower in QuestionFollower.objects.filter(follower=followed_user):
#                 user_all_related_questions_data.append({
#                     'user_id': user.id,
#                     'question_id': question_follower.question.id,
#                     'action': 'followed_user_follow',
#                     'action_timestamp': question_follower.created,
#                 })
#
#             # followed_user_view
#             for content_viewed in ContentViewd.objects.filter(user=followed_user, content_type__model='question'):
#                 user_all_related_questions_data.append({
#                     'user_id': user.id,
#                     'question_id': content_viewed.content_object.id,
#                     'action': 'followed_user_view',
#                     'action_timestamp': content_viewed.updated,
#                 })
#
#             # followed_user_post
#             for question in followed_user.question_posted.all():
#                 user_all_related_questions_data.append({
#                     'user_id': user.id,
#                     'question_id': question.id,
#                     'action': 'followed_user_post',
#                     'action_timestamp': question.created,
#                 })
#
#     user_all_related_questions_df = pd.DataFrame(user_all_related_questions_data)
#
#     return user_all_related_questions_df
#
#
# # 获取与输入问题文本相比，前 top_n 个最相似的问题
# def get_top_n_question_similarity_series(question_id, question_all_similarity_df, top_n=5):
#     # 获取给定问题的相似度数据
#     question_similarity_series = question_all_similarity_df[question_id]
#
#     # 按相似度降序排序
#     sorted_question_similarity_series = question_similarity_series.sort_values(ascending=False)
#
#     # 返回最相似的前 top_n 个问题（排除自身）
#     return sorted_question_similarity_series[1:top_n + 1]
#
#
# def recommend_questions_for_user(user_id, question_all_similarity_df, user_all_related_questions_df, top_n=5):
#     user_related_questions_series = user_all_related_questions_df[user_all_related_questions_df['user_id'] == user_id]
#
#     user_viewd_question_ids = set(user_related_questions_series
#                                      [(user_related_questions_series['action'] == 'follow') |
#                                       (user_related_questions_series['action'] == 'positive_vote') |
#                                       (user_related_questions_series['action'] == 'view') |
#                                       (user_related_questions_series['action'] == 'post')]
#                                       ['question_id']
#                                      )
#     # 推荐问题结果集
#     recommend_result = {}
#
#     for idx, row in user_related_questions_series.iterrows():
#         question_id = row['question_id']
#         action = row['action']
#         action_timestamp = row['action_timestamp']
#         weight = WEIGHTS[action]
#
#         time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))
#
#         cur_text_similar_questions = get_top_n_question_similarity_series(question_id, question_all_similarity_df)
#
#         for cur_text_similar_question_id, similarity in cur_text_similar_questions.items():
#             # once the question are in the user_viewd_question_ids,
#             # this question won't be recommned to user
#             if cur_text_similar_question_id not in user_viewd_question_ids:
#                 question_instance = Question.objects.get(id=cur_text_similar_question_id)
#                 if question_instance not in recommend_result:
#                     recommend_result[question_instance] = 0
#                 recommend_result[question_instance] += similarity * time_decay * weight
#
#         # 按推荐得分降序排序
#         sorted_recommend_result = sorted(recommend_result.items(), key=lambda x: x[1], reverse=True)
#
#         # 返回推荐得分最高的前 top_n 个问题
#         return sorted_recommend_result[:top_n]
#
#
# class Command(BaseCommand):
#     help = "Generate recommended questions for user."
#
#     def handle(self, *args, **options):
#         question_all_similarity_df = get_question_all_id_similarity_df()
#         user_all_related_questions_df = get_user_all_related_questions_df()
#
#         user = User.objects.get(id=1)
#         recommended_questions = recommend_questions_for_user(user.id, question_all_similarity_df, user_all_related_questions_df)
#
#         print(f"Recommended questions for user {user.username}:")
#         for question, similarity_score in recommended_questions:
#             print(f"{question} (similarity score: {similarity_score:.2f})")
#
