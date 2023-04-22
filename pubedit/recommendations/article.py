import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pubedit.models import Article, ArticleFollower
from core.models import Vote, ContentViewd
from datetime import datetime
from account.models import User, AccountFollower


def get_article_text(article):
    return article.title + ' ' + ','.join([tag.name for tag in article.tags.all()]) + ' ' + article.feed, 'html.parser'


# 获取系统中所有问题文本之间的相似度 DataFrame
def get_article_all_id_similarity_df():
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

    return article_all_similarity_df


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


# 获取系统中所有用户与之相关的问题
# 最终的 user_all_related_articles_df 需要包括 'user_id', 'article_id', 'action', 'action_timestamp' 等字段
def get_user_all_related_articles_df():
    user_all_related_articles_data = []

    for user in User.objects.all():
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
def get_top_n_article_similarity_series(article_id, article_all_similarity_df, top_n=5):
    # 获取给定问题的相似度数据
    article_similarity_series = article_all_similarity_df[article_id]

    # 按相似度降序排序
    sorted_article_similarity_series = article_similarity_series.sort_values(ascending=False)

    # 返回最相似的前 top_n 个问题（不排除自身）
    return sorted_article_similarity_series[:top_n]


def recommend_articles_for_user(user_id, article_all_similarity_df, user_all_related_articles_df, top_n):
    user_related_articles_series = user_all_related_articles_df[user_all_related_articles_df['user_id'] == user_id]

    user_viewd_article_ids = set(user_related_articles_series
                                     [(user_related_articles_series['action'] == 'follow') |
                                      (user_related_articles_series['action'] == 'positive_vote') |
                                      (user_related_articles_series['action'] == 'negative_vote') |
                                      (user_related_articles_series['action'] == 'view') |
                                      (user_related_articles_series['action'] == 'post')]
                                      ['article_id']
                                     )
    # 推荐问题结果集
    recommend_result = {}

    for idx, row in user_related_articles_series.iterrows():
        article_id = row['article_id']
        action = row['action']
        action_timestamp = row['action_timestamp']
        weight = WEIGHTS[action]

        time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))

        cur_text_similar_articles = get_top_n_article_similarity_series(article_id, article_all_similarity_df)

        for cur_text_similar_article_id, similarity in cur_text_similar_articles.items():
            # once the article are in the user_viewd_article_ids,
            # this article won't be recommned to user
            if cur_text_similar_article_id not in user_viewd_article_ids:
                article_instance = Article.objects.get(id=cur_text_similar_article_id)
                if article_instance not in recommend_result:
                    recommend_result[article_instance] = 0
                recommend_result[article_instance] += similarity * time_decay * weight

        # 按推荐得分降序排序
        sorted_recommend_result = sorted(recommend_result.items(), key=lambda x: x[1], reverse=True)

        # 返回推荐得分最高的前 top_n 个问题
        return sorted_recommend_result[:top_n]


def get_top_n_recommend_articles_for_user(user, top_n=50):
    article_all_similarity_df = get_article_all_id_similarity_df()
    user_all_related_articles_df = get_user_all_related_articles_df()

    print(f"article_all_similarity_df = \n{article_all_similarity_df}\n")
    print(f"user_all_related_articles_df = \n{user_all_related_articles_df}\n")


    recommended_articles = recommend_articles_for_user(user.id, article_all_similarity_df, user_all_related_articles_df, top_n=top_n)

    if recommended_articles is not None:
        return [item[0] for item in recommended_articles]
    else:
        return []
