from datetime import datetime, timedelta, timezone

class Article:
    def __init__(self, **kwargs):
        # 기사 링크
        self.article_id = kwargs.get("article_id", -1)
        # 기사 제목 
        self.title = kwargs.get("title", "제목없음")
        # 기사 내용
        self.content = kwargs.get("content", "본문없음")
        # 기사 매체
        self.media = kwargs.get("media", "알 수 없음")
        # 기사 추가 시점
        KST = timezone(timedelta(hours=9))
        kst_now = datetime.now(KST)
        self.created_time = kst_now.strftime("%y-%m-%d:%H")
        # 기사 발행 시점, 알 수 없으면 추가 시점으로
        self.datetime = kwargs.get("datetime", "알 수 없음")
        self.url = kwargs.get("url", "url 알 수 없음")

        self.index = kwargs.get("index", -1)
        self.page = kwargs.get("page", -1)
        self.keyword = kwargs.get("keyword", "키워드없음")
        self.score = kwargs.get("score", -1)
        
    def to_dict(self):
        return {
            "article_id": self.article_id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "media": self.media,
            "created_time": self.created_time,
            "datetime" : self.datetime,
            "index" : self.index,
            "page" : self.page,
            "score" : self.score,
            "keyword" : self.keyword,
        }
    
    def to_tuple(self):
        """ FAIRNESS 데이터베이스 저장용 """
        return (
            self.url,
            self.content,
            self.title,
            self.datetime,
            self.media,
        )