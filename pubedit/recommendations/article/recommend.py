from pubedit.models import Article, ArticleFollower
from core.recommendations.content import markdown_to_text

from celery import group, chord
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from qa.models import Question, QuestionFollower
from core.models import Vote, ContentViewd
from account.models import User, AccountFollower
from django.core.cache import cache
import numpy as np
from datetime import datetime
import json
import celery
from celery import shared_task
from celery.result import AsyncResult
from dateutil.parser import parse
from core.utils import partition_df
from cqa.settings import NUM_CORES


def get_article_text(article):
    return article.title + ' ' + ','.join([tag.name for tag in article.tags.all()]) + ' ' + markdown_to_text(article.feed)


"""
更新系统中所有文章文本之间的相似度 DataFrame
"""
def update_article_all_id_similarity_df():
    # TF-IDF和相似度计算相关的代码
    article_all = Article.objects.all()
    # [{'title': 'How to learn Django?', 'tags': 'cs,django,python'}]
    article_all_data = [{'article_id': article.id, 'article_text': get_article_text(article)} for article in article_all]

    article_all_df = pd.DataFrame(article_all_data)

    # 创建一个TF-IDF向量器
    vectorizer = TfidfVectorizer()

    # 将文本数据转换为TF-IDF矩阵
    # tfidf_matrix 中，每一行表示一个文档（article），每一列就是一个单词，矩阵中的数据就是某个单词在某个问题中的 tf-idf 值
    article_all_text_tfidf_matrix = vectorizer.fit_transform(article_all_df['article_text'])

    # 计算 TF-IDF 矩阵中问题之间的相似度
    # 计算每一个文档向量之间的余弦相似度，假设问题有 n 个，那么 similarity_matrix 就是 n * n 的矩阵（二维列表）
    # 第 i 行 j 列上的值就是问题 i 与问题 j，通过二者的 tf-idf 向量计算得出的余弦相似度
    article_all_text_similarity_matrix = cosine_similarity(article_all_text_tfidf_matrix)

    # 将相似度矩阵转换为 DataFrame
    # article_all_df['id'] 返回的是一个 pandas Series 对象，其中存有所有数据行在 'article_id' 字段上的值
    article_all_similarity_df = pd.DataFrame(article_all_text_similarity_matrix, index=article_all_df['article_id'], columns=article_all_df['article_id'])

    # 将 DataFrame 转换成 JSON 格式
    article_all_similarity_json = article_all_similarity_df.to_json()

    # 存储 JSON 数据到缓存
    cache.set('article_all_similarity_json', article_all_similarity_json, timeout=None)

"""
用户行为权重
"""
WEIGHTS = {
    'positive_vote': 40,
    'negative_vote': -40,
    'view': 10,
    'follow': 30,
    'post': 40,

    'followed_user_positive_vote': 3,
    'followed_user_negative_vote': -3,
    'followed_user_view': 1.5,
    'followed_user_follow': 5,
    'followed_user_post': 10,
}

"""
获取系统中所有用户与之相关的问题
最终的 user_all_related_articles_df 需要包括 'user_id', 'article_id', 'action', 'action_timestamp' 等字段
"""
def get_user_related_articles_df(user_id):
    user = User.objects.get(id=user_id)
    user_all_related_articles_data = []

    # vote
    for vote in Vote.objects.filter(content_type__model='article', voter=user):
        votes = vote.vote
        if votes == 0:
            continue
        user_all_related_articles_data.append({
            'user_id': user.id,
            'article_id': vote.content_object.id,
            'action': 'positive_vote' if votes == 1 else 'negative_vote',
            'action_timestamp': vote.updated
        })

    # view
    recently_created_viewed_record = ContentViewd.objects.filter(user=user, content_type__model='article').order_by('-created').first()
    if recently_created_viewed_record is not None:
        user_all_related_articles_data.append({
            'user_id': user.id,
            'article_id': recently_created_viewed_record.content_object.id,
            'action': 'view',
            'action_timestamp': recently_created_viewed_record.created,
        })

    # post
    for article in user.article_posted.all():
        user_all_related_articles_data.append({
            'user_id': user.id,
            'article_id': article.id,
            'action': 'post',
            'action_timestamp': article.created,
        })

    # follow
    for article_follower in ArticleFollower.objects.filter(follower=user):
        user_all_related_articles_data.append({
            'user_id': user.id,
            'article_id': article_follower.article.id,
            'action': 'follow',
            'action_timestamp': article_follower.created,
        })

    # followed_user

    for account_follower in AccountFollower.objects.filter(follower=user):
        followed_user = account_follower.followed
        # followed_user_positive_vote
        # followed_user_negative_vote
        for vote in Vote.objects.filter(content_type__model='article', voter=followed_user):
            votes = vote.vote
            if votes == 0:
                continue
            user_all_related_articles_data.append({
                'user_id': user.id,
                'article_id': vote.content_object.id,
                'action': 'followed_user_positive_vote' if votes == 1 else 'followed_user_negative_vote',
                'action_timestamp': vote.updated
            })

        # followed_user_follow
        for article_follower in ArticleFollower.objects.filter(follower=followed_user):
            user_all_related_articles_data.append({
                'user_id': user.id,
                'article_id': article_follower.article.id,
                'action': 'followed_user_follow',
                'action_timestamp': article_follower.created,
            })

        # followed_user_view
        recently_created_viewed_record = ContentViewd.objects.filter(user=followed_user, content_type__model='article').order_by('-created').first()
        if recently_created_viewed_record is not None:
            user_all_related_articles_data.append({
                'user_id': user.id,
                'article_id': recently_created_viewed_record.content_object.id,
                'action': 'followed_user_view',
                'action_timestamp': recently_created_viewed_record.created,
            })

        # followed_user_post
        for article in followed_user.article_posted.all():
            user_all_related_articles_data.append({
                'user_id': user.id,
                'article_id': article.id,
                'action': 'followed_user_post',
                'action_timestamp': article.created,
            })

    user_all_related_articles_df = pd.DataFrame(user_all_related_articles_data)

    return user_all_related_articles_df


# 获取与输入问题文本相比，前 top_n 个最相似的问题
def get_top_n_article_similarity_series(article_id, top_n=5):
    article_all_similarity_df = get_article_all_similarity()


    # 获取给定问题的相似度数据
    article_similarity_series = article_all_similarity_df[article_id]

    # 按相似度降序排序
    sorted_article_similarity_series = article_similarity_series.sort_values(ascending=False)

    # 返回最相似的前 top_n 个问题（不排除自身）
    return sorted_article_similarity_series[:top_n]


@shared_task
def map_task(dict_partition, user_viewd_article_ids_list):
    df_partition = pd.DataFrame(dict_partition)
    user_viewd_article_ids = set(user_viewd_article_ids_list)

    partition_recommend_result = {}
    for _, row in df_partition.iterrows():
        article_id = row['article_id']
        action = row['action']
        action_timestamp = parse(row['action_timestamp'])
        weight = WEIGHTS[action]

        time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))

        cur_text_similar_articles = get_top_n_article_similarity_series(article_id)

        for cur_text_similar_article_id, similarity in cur_text_similar_articles.items():
            if cur_text_similar_article_id not in user_viewd_article_ids:
                if cur_text_similar_article_id not in partition_recommend_result:
                    partition_recommend_result[cur_text_similar_article_id] = 0
                partition_recommend_result[cur_text_similar_article_id] += similarity * time_decay * weight

    return partition_recommend_result


@shared_task
def reduce_task(map_results, user_id, top_n):
    combined_results = {}
    for result in map_results:
        for article_id, score in result.items():
            if article_id not in combined_results:
                combined_results[article_id] = 0
            combined_results[article_id] += score

    sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)

    # 将 ID 转换为 Article 实例并返回推荐得分最高的前 top_n 个问题
    recommended_article_ids = [article_id for article_id, score in sorted_results[:top_n]]

    # 将结果缓存
    cache.set(f'user_{user_id}_articles_recommendation_json', json.dumps(recommended_article_ids), timeout=None)


"""
执行 MapReduce
"""
def _update_articles_recommendation_for_user(user_id, top_n):
    user_related_articles_df = get_user_related_articles_df(user_id)

    user_viewd_article_ids = set(user_related_articles_df
                                  [(user_related_articles_df['action'] == 'follow') |
                                   (user_related_articles_df['action'] == 'positive_vote') |
                                   (user_related_articles_df['action'] == 'negative_vote') |
                                   (user_related_articles_df['action'] == 'view') |
                                   (user_related_articles_df['action'] == 'post')]
                                  ['article_id']
                                  )

    # 将 user_related_questions_df 划分为与 CPU 核心数相等的份数
    df_partitions = partition_df(user_related_articles_df, NUM_CORES)
    # celery 需要将 dataframe 转化成 json 格式
    dict_partitions = [partition.to_dict(orient='records') for partition in df_partitions]
    # 同样，celery 也不允许 set 类型，需要转化成 list 类型
    user_viewed_article_ids_list = list(user_viewd_article_ids)

    map_tasks = [map_task.s(dict_partition, user_viewed_article_ids_list) for dict_partition in dict_partitions]
    chord(group(*map_tasks))(reduce_task.s(user_id, top_n))


"""
从 redis 缓存中获取 user 的推荐文章
"""
def get_recommend_articles_for_user(user):
    # 获取缓存数据
    recommended_article_ids_json = cache.get(f'user_{user.id}_articles_recommendation_json')
    # 将 JSON 数据转换回列表
    recommended_article_ids = json.loads(recommended_article_ids_json)

    return Article.objects.filter(id__in=recommended_article_ids)



"""
从 redis 缓存中获取 article_all_similarity
"""
def get_article_all_similarity():
    # 从缓存中获取 JSON 数据
    article_all_similarity_json = cache.get('article_all_similarity_json')
    # 将 JSON 数据转换回 DataFrame
    article_all_similarity_df = pd.read_json(article_all_similarity_json)

    return article_all_similarity_df


"""
创建一个新的 recommended articles for user task '周期'任务：update_articles_recommendation_for_user
"""
def start_article_recommendation_for_user_task(user, top_n=50):
    # 获取现有任务的ID
    user_2_article_task_ids_json = cache.get('user_articles_recommendation_task_ids_json')
    if user_2_article_task_ids_json is None:
        user_2_article_task_ids = {}
    else:
        user_2_article_task_ids = json.loads(user_2_article_task_ids_json)

    article_task_id = user_2_article_task_ids[user.id] if user.id in user_2_article_task_ids else None

    # 如果存在现有任务ID，取消该任务
    if article_task_id:
        # 获取任务的结果对象
        article_task_result = AsyncResult(article_task_id)

        if article_task_result.state in ('PENDING', 'RETRY'):
            celery.current_app.control.revoke(article_task_id, terminate=True)
        elif article_task_result.state == 'STARTED':
            # 等待任务完成，3 秒之后还没完成直接报错
            article_task_result.get(timeout=3)


    # 异步的 MapReduce 地更新 user 的所有被推荐的问题
    _update_articles_recommendation_for_user(user.id, top_n)

    # 调度新任务
    new_article_task = update_articles_recommendation_for_user.apply_async(args=(user.id, top_n), countdown=user.update_interval)

    # 存储新任务的ID到 Redis 散列中
    user_2_article_task_ids[user.id] = new_article_task.id
    cache.set('user_articles_recommendation_task_ids_json', json.dumps(user_2_article_task_ids), timeout=None)


@shared_task
def update_articles_recommendation_for_user(user_id, top_n=50):
    # 计算并缓存 questions_recommendation_for_user
    user = User.objects.get(id=user_id)

    # 异步的 MapReduce 地更新 user 的所有被推荐的问题
    _update_articles_recommendation_for_user(user.id, top_n)

    # 重新调度任务
    update_articles_recommendation_for_user.apply_async(args=(user_id, top_n), countdown=user.update_interval)

