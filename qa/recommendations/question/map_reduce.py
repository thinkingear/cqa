from datetime import datetime
import numpy as np
from qa.recommendations.question.recommend import get_top_n_question_similarity_series


# Map 函数
def map_function(row, question_all_similarity_df, user_viewd_question_ids):

    print(f"|-----------Entering map_function-----------|")
    question_id, action, action_timestamp, weight = row
    time_decay = 1 / (1 + np.log1p((datetime.now(action_timestamp.tzinfo) - action_timestamp).days))

    cur_text_similar_questions = get_top_n_question_similarity_series(question_id, question_all_similarity_df)

    recommend_result = {}
    for cur_text_similar_question_id, similarity in cur_text_similar_questions.items():
        if cur_text_similar_question_id not in user_viewd_question_ids:
            if cur_text_similar_question_id not in recommend_result:
                recommend_result[cur_text_similar_question_id] = 0
            recommend_result[cur_text_similar_question_id] += similarity * time_decay * weight

    return recommend_result


# Reduce 函数
# a and b are recommend_result partitions
def reduce_function(a, b):
    print(f"|-----------Entering map_function-----------|")

    for question_id, score in b.items():
        if question_id not in a:
            a[question_id] = 0
        a[question_id] += score
    return a

