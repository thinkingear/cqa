from qa.models import Answer, AnswerFollower
from qa.recommendations.question.recommend import get_question_all_similarity, get_top_n_question_similarity_series
from core.recommendations.content import markdown_to_text
from celery import group, chord
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from qa.models import Question, QuestionFollower
from core.models import Vote, ContentViewd
from account.models import User, AccountFollower
from django.core.cache import cache
import os
import numpy as np
from datetime import datetime
import json
import celery
from celery import shared_task
from celery.result import AsyncResult
from dateutil.parser import parse
from core.utils import partition_df
from cqa.settings import NUM_CORES


def get_answer_text(answer):
    return answer.question.title + ' ' + markdown_to_text(answer.feed)


# 获取系统中所有问题文本之间的相似度 DataFrame
def update_answer_all_id_similarity_df():
    # TF-IDF和相似度计算相关的代码
    answer_all = Answer.objects.all()
    # [{'title': 'How to learn Django?', 'tags': 'cs,django,python'}]
    answer_all_data = [{'answer_id': answer.id, 'answer_text': get_answer_text(answer)} for answer in answer_all]

    answer_all_df = pd.DataFrame(answer_all_data)

    # 创建一个TF-IDF向量器
    vectorizer = TfidfVectorizer()

    # 将文本数据转换为TF-IDF矩阵
    # tfidf_matrix 中，每一行表示一个文档（answer），每一列就是一个单词，矩阵中的数据就是某个单词在某个问题中的 tf-idf 值
    answer_all_text_tfidf_matrix = vectorizer.fit_transform(answer_all_df['answer_text'])

    # 计算 TF-IDF 矩阵中问题之间的相似度
    # 计算每一个文档向量之间的余弦相似度，假设问题有 n 个，那么 similarity_matrix 就是 n * n 的矩阵（二维列表）
    # 第 i 行 j 列上的值就是问题 i 与问题 j，通过二者的 tf-idf 向量计算得出的余弦相似度
    answer_all_text_similarity_matrix = cosine_similarity(answer_all_text_tfidf_matrix)

    # 将相似度矩阵转换为 DataFrame
    # answer_all_df['id'] 返回的是一个 pandas Series 对象，其中存有所有数据行在 'answer_id' 字段上的值
    answer_all_similarity_df = pd.DataFrame(answer_all_text_similarity_matrix, index=answer_all_df['answer_id'], columns=answer_all_df['answer_id'])

    # 将 DataFrame 转换成 JSON 格式
    answer_all_similarity_json = answer_all_similarity_df.to_json()

    # 存储 JSON 数据到缓存
    cache.set('answer_all_similarity_json', answer_all_similarity_json, timeout=None)


WEIGHTS = {
    # user 直接产生交互的 answers
    'positive_vote': 40,
    'negative_vote': -40,
    'view': 10,
    'follow': 30,
    'post': 40,
    # user 关注的用户直接产生交互的 answers
    'followed_user_positive_vote': 10,
    'followed_user_negative_vote': -10,
    'followed_user_view': 1,
    'followed_user_follow': 5,
    'followed_user_post': 10,
    # user 直接产生交互的 questions 所相关的 questions 下的 answers
    # 这些 answers 还要按照 views, followers 的数量进行进一步的排序评分
    'posted_questions_related_questions_answer': 10,
    'followed_questions_related_questions_answer': 5,
    'viewed_questions_related_questions_answer': 1,
    'positively_voted_questions_related_questions_answer': 10,
    'negatively_voted_questions_related_questions_answer': -10,

    # user 直接产生交互的 answers 的 questions 所相关的 questions 下的 answers
    # 这些 answers 还要按照 views, followers 的数量进行进一步的排序评分
    'posted_answers_questions_related_questions_answer': 10,
    'followed_answers_questions_related_questions_answer': 5,
    'viewed_answers_questions_related_questions_answer': 1,
    'positively_voted_answers_questions_related_questions_answer': 10,
    'negatively_answers_questions_related_questions_answer': -10,
}


def min_max_normalization(min_value, max_value, total_value):
    if min_value == max_value:
        return 0
    else:
        return 2 * (total_value - min_value) / (max_value - min_value) - 1


def get_answer_2_answer_score(answers):
    if answers.count() == 0:
        return {}

    max_votes = max(answer.vote_sum for answer in answers)
    min_votes = min(answer.vote_sum for answer in answers)

    max_followers = max(answer.followers.count() for answer in answers)
    min_followers = min(answer.followers.count() for answer in answers)

    max_views = max(answer.views for answer in answers)
    min_views = min(answer.views for answer in answers)

    alpha = 0.5
    beta = 0.3
    gamma = 0.2

    answer_2_answer_score = {}

    for answer in answers:
        answer_2_answer_score[answer] = alpha * min_max_normalization(min_votes, max_votes, answer.vote_sum) + \
                                        beta * min_max_normalization(min_followers, max_followers, answer.followers.count()) + \
                                        gamma * min_max_normalization(min_views, max_views, answer.views)

    return answer_2_answer_score


# 获取系统中所有用户与之相关的问题
# 最终的 user_all_related_answers_df 需要包括 'user_id', 'answer_id', 'action', 'action_timestamp' 等字段
def get_user_related_answers_df(user_id):
    user = User.objects.get(id=user_id)

    user_related_answers_data = []

    # vote
    for vote in Vote.objects.filter(content_type__model='answer', voter=user):
        votes = vote.vote
        if votes == 0:
            continue
        user_related_answers_data.append({
            'user_id': user.id,
            'answer_id': vote.content_object.id,
            'action': 'positive_vote' if votes == 1 else 'negative_vote',
            'action_timestamp': vote.updated
        })

    # view
    recently_created_viewed_record = ContentViewd.objects.filter(user=user, content_type__model='answer').order_by('-created').first()
    if recently_created_viewed_record is not None:
        user_related_answers_data.append({
            'user_id': user.id,
            'answer_id': recently_created_viewed_record.content_object.id,
            'action': 'view',
            'action_timestamp': recently_created_viewed_record.created,
        })

    # post
    for answer in user.answer_posted.all():
        user_related_answers_data.append({
            'user_id': user.id,
            'answer_id': answer.id,
            'action': 'post',
            'action_timestamp': answer.created,
        })

    # follow
    for answer_follower in AnswerFollower.objects.filter(follower=user):
        user_related_answers_data.append({
            'user_id': user.id,
            'answer_id': answer_follower.answer.id,
            'action': 'follow',
            'action_timestamp': answer_follower.created,
        })

    # followed_user
    for account_follower in AccountFollower.objects.filter(follower=user):
        followed_user = account_follower.followed
        # followed_user_positive_vote
        # followed_user_negative_vote
        for vote in Vote.objects.filter(content_type__model='answer', voter=followed_user):
            votes = vote.vote
            if votes == 0:
                continue
            user_related_answers_data.append({
                'user_id': user.id,
                'answer_id': vote.content_object.id,
                'action': 'followed_user_positive_vote' if votes == 1 else 'followed_user_negative_vote',
                'action_timestamp': vote.updated
            })

        # followed_user_follow
        for answer_follower in AnswerFollower.objects.filter(follower=followed_user):
            user_related_answers_data.append({
                'user_id': user.id,
                'answer_id': answer_follower.answer.id,
                'action': 'followed_user_follow',
                'action_timestamp': answer_follower.created,
            })

        # followed_user_view
        recently_created_viewed_record = ContentViewd.objects.filter(user=followed_user, content_type__model='answer').order_by('-created').first()
        if recently_created_viewed_record is not None:
            user_related_answers_data.append({
                'user_id': user.id,
                'answer_id': recently_created_viewed_record.content_object.id,
                'action': 'followed_user_view',
                'action_timestamp': recently_created_viewed_record.created,
            })

        # followed_user_post
        for answer in followed_user.answer_posted.all():
            user_related_answers_data.append({
                'user_id': user.id,
                'answer_id': answer.id,
                'action': 'followed_user_post',
                'action_timestamp': answer.created,
            })

    # user 直接产生交互的 questions 所相关的 questions 下的 answers
    def put_question_related_answer_data(question_id, action, action_timestamp):
        related_questions = get_top_n_question_similarity_series(question_id)
        for related_question_id, similarity in related_questions.items():
            related_question = Question.objects.get(id=related_question_id)
            answers = related_question.answers.all()
            for answer, answer_score in get_answer_2_answer_score(answers).items():
                user_related_answers_data.append({
                    'user_id': user.id,
                    'answer_id': answer.id,
                    'answer_score': answer_score,
                    'action': action,
                    'action_timestamp': action_timestamp,
                })

    # positively_voted_questions_related_questions_answer
    # negatively_voted_questions_related_questions_answer
    for vote in Vote.objects.filter(content_type__model='question', voter=user):
        if vote.vote == 0:
            continue

        put_question_related_answer_data(
            question_id=vote.content_object.id,
            action='positively_voted_questions_related_questions_answer' if vote.vote == 1 else 'negatively_voted_questions_related_questions_answer',
            action_timestamp=vote.updated,
        )

    # posted_questions_related_questions_answer
    for posted_question in user.question_posted.all():
        put_question_related_answer_data(
            question_id=posted_question.id,
            action='posted_questions_related_questions_answer',
            action_timestamp=posted_question.updated,
        )

    # followed_questions_related_questions_answer
    for question_follower in QuestionFollower.objects.filter(follower=user):
        put_question_related_answer_data(
            question_id=question_follower.question.id,
            action='followed_questions_related_questions_answer',
            action_timestamp=question_follower.created,
        )

    # viewed_questions_related_questions_answer
    recently_created_viewed_record = ContentViewd.objects.filter(user=user, content_type__model='question').order_by('-created').first()
    if recently_created_viewed_record is not None:
        put_question_related_answer_data(
            question_id=recently_created_viewed_record.content_object.id,
            action='viewed_questions_related_questions_answer',
            action_timestamp=recently_created_viewed_record.created,
        )

    # user 直接产生交互的 answers 的 questions 所相关的 questions 下的 answers
    # positively_voted_answers_questions_related_questions_answer
    # negatively_answers_questions_related_questions_answer
    for vote in Vote.objects.filter(content_type__model='answer', voter=user):
        votes = vote.vote
        if votes == 0:
            continue

        put_question_related_answer_data(
            question_id=vote.content_object.question.id,
            action='positively_voted_answers_questions_related_questions_answer' if votes == 1 else 'negatively_answers_questions_related_questions_answer',
            action_timestamp=vote.updated,
        )

    # viewed_answers_questions_related_questions_answer
    recently_created_viewed_record = ContentViewd.objects.filter(user=user, content_type__model='answer').order_by('-created').first()
    if recently_created_viewed_record is not None:
        put_question_related_answer_data(
            question_id=recently_created_viewed_record.content_object.question.id,
            action='viewed_answers_questions_related_questions_answer',
            action_timestamp=recently_created_viewed_record.created,
        )

    # posted_answers_questions_related_questions_answer
    for answer in user.answer_posted.all():
        put_question_related_answer_data(
            question_id=answer.question.id,
            action='posted_answers_questions_related_questions_answer',
            action_timestamp=answer.created,
        )

    # followed_answers_questions_related_questions_answer
    for answer_follower in AnswerFollower.objects.filter(follower=user):
        put_question_related_answer_data(
            question_id=answer_follower.answer.question.id,
            action='followed_answers_questions_related_questions_answer',
            action_timestamp=answer_follower.created,
        )

    user_related_answers_df = pd.DataFrame(user_related_answers_data)
    user_related_answers_df['answer_score'].fillna(1, inplace=True)

    return user_related_answers_df


# 获取与输入问题文本相比，前 top_n 个最相似的问题
def get_top_n_answer_similarity_series(answer_id, top_n=5):
    answer_all_similarity_df = get_answer_all_similarity()

    # 获取给定问题的相似度数据
    answer_similarity_series = answer_all_similarity_df[answer_id]

    # 按相似度降序排序
    sorted_answer_similarity_series = answer_similarity_series.sort_values(ascending=False)

    # 返回最相似的前 top_n 个问题（不排除自身）
    return sorted_answer_similarity_series[:top_n]


@shared_task
def map_task(dict_partition, user_viewed_answer_ids_list):
    # print(f"\n|----------------------- MAP TASK: CALL --------------------------|")
    # print(f"\n user_viewed_answer_ids_list = \n{user_viewed_answer_ids_list}")

    df_partition = pd.DataFrame(dict_partition)
    user_viewed_answer_ids = set(user_viewed_answer_ids_list)

    partition_recommend_result = {}
    for _, row in df_partition.iterrows():
        answer_id = row['answer_id']
        action = row['action']
        action_timestamp = parse(row['action_timestamp'])
        answer_score = row['answer_score']
        weight = WEIGHTS[action]

        time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))

        cur_text_similar_answers = get_top_n_answer_similarity_series(answer_id)

        for cur_text_similar_answer_id, similarity in cur_text_similar_answers.items():
            if cur_text_similar_answer_id not in user_viewed_answer_ids:
                if cur_text_similar_answer_id not in partition_recommend_result:
                    partition_recommend_result[cur_text_similar_answer_id] = 0
                # 根据权重调整答案分数
                adjusted_answer_score = answer_score * np.sign(weight)
                partition_recommend_result[cur_text_similar_answer_id] += similarity * time_decay * weight * adjusted_answer_score

    # print(f"\n|----------------------- MAP TASK: RETURN --------------------------|")
    # print(f"\n partition_recommend_result = \n{partition_recommend_result}")

    return partition_recommend_result


@shared_task
def reduce_task(map_results, user_id, top_n):
    # print(f"\n|----------------------- REDUCE TASK: CALL --------------------------|")
    # print(f"\n user_id = \n{user_id}")
    # print(f"\n top_n = \n{top_n}")
    # print(f"\n map_results = \n{map_results}")

    combined_results = {}
    for result in map_results:
        for answer_id, score in result.items():
            if answer_id not in combined_results:
                combined_results[answer_id] = 0
            combined_results[answer_id] += score

    sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)

    # print(f"\n|----------------------- REDUCE TASK: RETURN --------------------------|")
    # print(f"\n sorted_results = \n{sorted_results}")

    # 将 ID 转换为 Answer 实例并返回推荐得分最高的前 top_n 个答案
    recommended_answer_ids = [answer_id for answer_id, score in sorted_results[:top_n]]

    # 将结果缓存
    cache.set(f'user_{user_id}_answers_recommendation_json', json.dumps(recommended_answer_ids), timeout=None)



"""
执行 MapReduce
"""
def _update_answers_recommendation_for_user(user_id, top_n):

    user_related_answers_df = get_user_related_answers_df(user_id)

    user_viewd_answer_ids = set(user_related_answers_df
                                  [(user_related_answers_df['action'] == 'follow') |
                                   (user_related_answers_df['action'] == 'positive_vote') |
                                   (user_related_answers_df['action'] == 'negative_vote') |
                                   (user_related_answers_df['action'] == 'view') |
                                   (user_related_answers_df['action'] == 'post')]
                                  ['answer_id']
                                  )
    #
    # print(f"\n|----------------------- _update_answers_recommendation_for_user: CALL --------------------------|")
    # print(f"\n user_id = {user_id}, user_viewd_answer_ids = \n{user_viewd_answer_ids}")

    # 将 user_related_answers_df 划分为与 CPU 核心数相等的份数
    df_partitions = partition_df(user_related_answers_df, NUM_CORES)

    # celery 需要将 dataframe 转化成 json 格式
    dict_partitions = [partition.to_dict(orient='records') for partition in df_partitions if len(partition) != 0]
    # 同样，celery 也不允许 set 类型，需要转化成 list 类型
    user_viewed_answer_ids_list = list(user_viewd_answer_ids)

    map_tasks = [map_task.s(dict_partition, user_viewed_answer_ids_list) for dict_partition in dict_partitions]
    chord(group(*map_tasks))(reduce_task.s(user_id, top_n))


"""
从 redis 缓存中获取 user 的推荐 Answer
"""
def get_recommend_answers_for_user(user):
    # 获取缓存数据
    recommended_answer_ids_json = cache.get(f'user_{user.id}_answers_recommendation_json')
    # 将 JSON 数据转换回列表
    recommended_answer_ids = json.loads(recommended_answer_ids_json)

    return Answer.objects.filter(id__in=recommended_answer_ids)


"""
从 redis 缓存中获取 answer_all_similarity
"""
def get_answer_all_similarity():
    # 从缓存中获取 JSON 数据
    answer_all_similarity_json = cache.get('answer_all_similarity_json')
    # 将 JSON 数据转换回 DataFrame
    answer_all_similarity_df = pd.read_json(answer_all_similarity_json)

    return answer_all_similarity_df


"""
创建一个新的 recommended answers for user task '周期'任务：update_answers_recommendation_for_user
"""
def start_answer_recommendation_for_user_task(user, top_n=50):
    # 获取现有任务的ID
    user_2_answer_task_ids_json = cache.get('user_answers_recommendation_task_ids_json')
    if user_2_answer_task_ids_json is None:
        user_2_answer_task_ids = {}
    else:
        user_2_answer_task_ids = json.loads(user_2_answer_task_ids_json)
    answer_task_id = user_2_answer_task_ids[user.id] if user.id in user_2_answer_task_ids else None

    # 如果存在现有任务ID，取消该任务
    if answer_task_id:
        # 获取任务的结果对象
        answer_task_result = AsyncResult(answer_task_id)

        if answer_task_result.state in ('PENDING', 'RETRY'):
            celery.current_app.control.revoke(answer_task_id, terminate=True)
        elif answer_task_result.state == 'STARTED':
            # 等待任务完成，3 秒之后还没完成直接报错
            answer_task_result.get(timeout=3)

    # 异步的 MapReduce 地更新 user 的所有被推荐的答案
    _update_answers_recommendation_for_user(user.id, top_n)

    # 调度新任务
    new_answer_task = update_answers_recommendation_for_user.apply_async(args=(user.id, top_n), countdown=user.update_interval)

    # 存储新任务的ID到 Redis 散列中
    user_2_answer_task_ids[user.id] = new_answer_task.id
    cache.set('user_answers_recommendation_task_ids_json', json.dumps(user_2_answer_task_ids), timeout=None)


@shared_task
def update_answers_recommendation_for_user(user_id, top_n=50):
    # 计算并缓存 answers_recommendation_for_user
    user = User.objects.get(id=user_id)

    # 异步的 MapReduce 地更新 user 的所有被推荐的答案
    _update_answers_recommendation_for_user(user.id, top_n)

    # 重新调度任务
    update_answers_recommendation_for_user.apply_async(args=(user_id, top_n), countdown=user.update_interval)


