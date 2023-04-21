import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from qa.models import Answer, AnswerFollower, Question, QuestionFollower
from core.models import Vote, ContentViewd
from datetime import datetime
from account.models import User, AccountFollower
from bs4 import BeautifulSoup
from qa.recommendations.question import get_question_all_id_similarity_df, get_top_n_question_similarity_series


def get_answer_text(answer):
    return answer.question.title + ' ' + BeautifulSoup(answer.feed, 'html.parser').get_text()


# 获取系统中所有问题文本之间的相似度 DataFrame
def get_answer_all_id_similarity_df():
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

    return answer_all_similarity_df


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
def get_user_all_related_answers_df():
    user_all_related_answers_data = []
    question_all_id_similarity_df = get_question_all_id_similarity_df()

    for user in User.objects.all():
        # vote
        for vote in Vote.objects.filter(content_type__model='answer', voter=user):
            votes = vote.vote
            if votes == 0:
                continue
            user_all_related_answers_data.append({
                'user_id': user.id,
                'answer_id': vote.content_object.id,
                'action': 'positive_vote' if votes == 1 else 'negative_vote',
                'action_timestamp': vote.updated
            })

        # view
        recently_created_viewed_record = ContentViewd.objects.filter(user=user, content_type__model='answer').order_by('-created').first()
        if recently_created_viewed_record is not None:
            user_all_related_answers_data.append({
                'user_id': user.id,
                'answer_id': recently_created_viewed_record.content_object.id,
                'action': 'view',
                'action_timestamp': recently_created_viewed_record.created,
            })

        # post
        for answer in user.answer_posted.all():
            user_all_related_answers_data.append({
                'user_id': user.id,
                'answer_id': answer.id,
                'action': 'post',
                'action_timestamp': answer.created,
            })

        # follow
        for answer_follower in AnswerFollower.objects.filter(follower=user):
            user_all_related_answers_data.append({
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
                user_all_related_answers_data.append({
                    'user_id': user.id,
                    'answer_id': vote.content_object.id,
                    'action': 'followed_user_positive_vote' if votes == 1 else 'followed_user_negative_vote',
                    'action_timestamp': vote.updated
                })

            # followed_user_follow
            for answer_follower in AnswerFollower.objects.filter(follower=followed_user):
                user_all_related_answers_data.append({
                    'user_id': user.id,
                    'answer_id': answer_follower.answer.id,
                    'action': 'followed_user_follow',
                    'action_timestamp': answer_follower.created,
                })

            # followed_user_view
            recently_created_viewed_record = ContentViewd.objects.filter(user=followed_user, content_type__model='answer').order_by('-created').first()
            if recently_created_viewed_record is not None:
                user_all_related_answers_data.append({
                    'user_id': user.id,
                    'answer_id': recently_created_viewed_record.content_object.id,
                    'action': 'followed_user_view',
                    'action_timestamp': recently_created_viewed_record.created,
                })

            # followed_user_post
            for answer in followed_user.answer_posted.all():
                user_all_related_answers_data.append({
                    'user_id': user.id,
                    'answer_id': answer.id,
                    'action': 'followed_user_post',
                    'action_timestamp': answer.created,
                })

        # user 直接产生交互的 questions 所相关的 questions 下的 answers
        def put_question_related_answer_data(question_id, action, action_timestamp):
            related_questions = get_top_n_question_similarity_series(question_id, question_all_id_similarity_df)
            for related_question_id, similarity in related_questions.items():
                related_question = Question.objects.get(id=related_question_id)
                answers = related_question.answers.all()
                if len(answers) != 0:
                    for answer, answer_score in get_answer_2_answer_score(answers).items():
                        user_all_related_answers_data.append({
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

    user_all_related_answers_df = pd.DataFrame(user_all_related_answers_data)
    user_all_related_answers_df['answer_score'].fillna(1, inplace=True)

    return user_all_related_answers_df


# 获取与输入问题文本相比，前 top_n 个最相似的问题
def get_top_n_answer_similarity_series(answer_id, answer_all_similarity_df, top_n=5):
    # 获取给定问题的相似度数据
    answer_similarity_series = answer_all_similarity_df[answer_id]

    # 按相似度降序排序
    sorted_answer_similarity_series = answer_similarity_series.sort_values(ascending=False)

    # 返回最相似的前 top_n 个问题（不排除自身）
    return sorted_answer_similarity_series[:top_n]


def recommend_answers_for_user(user_id, answer_all_similarity_df, user_all_related_answers_df, top_n):
    user_related_answers_series = user_all_related_answers_df[user_all_related_answers_df['user_id'] == user_id]

    user_viewd_answer_ids = set(user_related_answers_series
                                     [(user_related_answers_series['action'] == 'follow') |
                                      (user_related_answers_series['action'] == 'positive_vote') |
                                      (user_related_answers_series['action'] == 'negative_vote') |
                                      (user_related_answers_series['action'] == 'view') |
                                      (user_related_answers_series['action'] == 'post')]
                                      ['answer_id']
                                     )
    # 推荐问题结果集
    recommend_result = {}

    for idx, row in user_related_answers_series.iterrows():
        answer_id = row['answer_id']
        action = row['action']
        action_timestamp = row['action_timestamp']
        weight = WEIGHTS[action]
        answer_score = row['answer_score']

        time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))

        cur_text_similar_answers = get_top_n_answer_similarity_series(answer_id, answer_all_similarity_df)

        for cur_text_similar_answer_id, similarity in cur_text_similar_answers.items():
            # once the answer are in the user_viewd_answer_ids,
            # this answer won't be recommned to user
            if cur_text_similar_answer_id not in user_viewd_answer_ids:
                answer_instance = Answer.objects.get(id=cur_text_similar_answer_id)
                if answer_instance not in recommend_result:
                    recommend_result[answer_instance] = 0
                # 根据权重调整答案分数
                adjusted_answer_score = answer_score * np.sign(weight)
                recommend_result[answer_instance] += similarity * time_decay * weight * adjusted_answer_score

        # 按推荐得分降序排序
        sorted_recommend_result = sorted(recommend_result.items(), key=lambda x: x[1], reverse=True)

        # 返回推荐得分最高的前 top_n 个问题
        return sorted_recommend_result[:top_n]


def get_top_n_recommend_answers_for_user(user, top_n=50):
    answer_all_similarity_df = get_answer_all_id_similarity_df()
    user_all_related_answers_df = get_user_all_related_answers_df()

    recommended_answers = recommend_answers_for_user(user.id, answer_all_similarity_df, user_all_related_answers_df, top_n=top_n)

    if recommended_answers is not None:
        return [item[0] for item in recommended_answers]
    else:
        return []
