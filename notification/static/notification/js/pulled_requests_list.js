function togglePulledRequestJudgeButton(article_feed_id, cmd) {
    service.get("notification/pull/request/article/judge/", {
        params: {
            cmd: cmd,
            article_feed_id: article_feed_id,
        }
    }).then((response) => {
        location.reload();
    }).catch((error) => {
        console.log(error);
    });
}