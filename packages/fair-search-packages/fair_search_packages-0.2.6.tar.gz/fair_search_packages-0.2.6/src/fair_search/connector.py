import pymysql
from fair_setup import connect_mysql_database
from typing import List

class DatabaseConnector:
    def __init__(self, config_path, database_name):
        self.connection = connect_mysql_database(config_path=config_path, database_name=database_name)

    def close(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")

    # SQL문 실행
    def executeSQL(self, sql_query: str, values:object):
        if not self.connection:
            print("데이터베이스 연결이 없습니다")
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query, values)
        except pymysql.MySQLError as e:
            print(f"❌ SQL 실행 실패 {e}")
        self.connection.commit()
        cursor.close()

    def getAllArticles(self, limit:int = -1) -> List[dict]:
        """Article 테이블 내 모든 데이터 조회 함수"""
        if not self.connection:
            print("데이터베이스 연결이 없습니다")
        try:
            cursor = self.connection.cursor()
            if limit == -1:
                cursor.execute("select * from article")
            else:
                cursor.execute(f"select * from article limit {limit}")
            return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"❌ SQL 실행 실패 {e}")
        self.connection.commit()
        cursor.close()

    def getNotSummaryArticles(self) -> List[dict]:
        if not self.connection:
            print("데이터베이스 연결이 없습니다")
        try:
            cursor = self.connection.cursor()
            cursor.execute("select * from article where summary is null")
            return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"❌ SQL 실행 실패 {e}")
        self.connection.commit()
        cursor.close()        


    def getArticlesByRang(self, start_id, end_id, n=None):
        """ start_id <= x <= end_id 범위 내에서 N개 랜덤 선택 """
        if not self.connection:
            print("데이터베이스 연결이 없습니다")
            return []
        try:
            cursor = self.connection.cursor()
            if n:
                query = f"""
                    SELECT * FROM article
                    WHERE article_id >= {start_id} AND article_id <= {end_id}
                    ORDER BY RAND()
                    LIMIT {n}
                """
            else:
                query = f"SELECT * FROM article WHERE article_id >= {start_id} AND article_id <= {end_id}"
            cursor.execute(query)
            return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"❌ SQL 실행 실패 {e}")
            return []
        finally:
            self.connection.commit()
            cursor.close()

    def getArticleById(self, data_id: int):
        """ 특정 아이디를 통해 특정 단일행 출력 """
        if not self.connection:
            print("데이터베이스 연결이 없습니다")
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"select * from article where article_id = {data_id}")
            return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"❌ SQL 실행 실패 {e}")
        self.connection.commit()
        cursor.close()

    def exchangeDatetime(self, article_id: int, str_datetime: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE article SET created_time = %s WHERE article_id = %s",
                (str_datetime, article_id)   # 파라미터 바인딩 → 자동 따옴표 & 포맷
            )
            print(f'{article_id} update successfully')
        self.connection.commit()

    def updateSummary(self, article_id:int, summary: str) -> None:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE article SET summary = %s WHERE article_id = %s",
                    (summary, article_id)
                )
            self.connection.commit()
        except Exception as e:
            print(f"UPDATE ERROR : {e}, article_id : {article_id}")
