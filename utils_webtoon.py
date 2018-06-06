import os
from io import BytesIO
from urllib import parse

import requests
from bs4 import BeautifulSoup


class Episode:
    def __init__(self, webtoon_id, no, url_thumbnail,
                 title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date
    #  에피소드 클래스에 매개변수 webtton_id,no, thumbnai, title, rating, created_date를 받고
        # 위 인스턴스가 배개변수를 받음
    @property @ #속성 가져옴
    def url(self):
        # self는 위의 인스턴스를 받게됨
        """
        self.webtoon_id, self.no 요소를 사용하여
        실제 에피소드 페이지 URL을 리턴
        :return:
        """
        # url은 메인 웹툰 주소
        # 파라미터값은 타이틀과 넘버를 줌
        #에피소드 Url은 파라미터로 받은??? 살제 웹툰 주소를 리턴 해준
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }
        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_image_url_list(self):
        #플린트
        print('get_image_url_list start')

        # 파일 경로는  'data/episode_detail-{webtoon_id}-{episode_no}.html'는 웹툰_id와 no를 넣어줌??
        file_path = 'data/episode_detail-{webtoon_id}-{episode_no}.html'.format(
            webtoon_id=self.webtoon_id,
            episode_no=self.no,
        )
        print('file_path:', file_path)

        # 위에 파일 유무 확인
        if os.path.exists(file_path):
            print('os.path.exists: True')
            # 있다면 읽어서 html에 줌
            html = open(file_path, 'rt').read()
        else:
            # 없으면 self.uel에  requests 사용해서 건네줌
            print('os.path.exists: False')
            print(' http get request, url:', self.url)
            response = requests.get(self.url)
            #  받은걸 html에게
            html = response.text
            #  file_path에 기록 저장
            open(file_path, 'wt').write(html)

        # html문자열로 BeautifulSoup객체 생성
        soup = BeautifulSoup(html, 'lxml')

        # img목록을 찾는다. 위치는 "div.wt_viewer > img"
        img_list = soup.select('div.wt_viewer > img')

        # 이미지 URL(src의 값)을 저장할 리스트
        # url_list = []
        # for img in img_list:
        #     url_list.append(img.get('src'))

        # img목록을 순회하며 각 item(BeautifulSoup Tag object)에서
        #  'src'속성값을 사용해 리스트 생성

        ## img_list를 반복하면서 img변수에 넣어주고
        ## Img 요소중에 src 속성만 list에 추가시킴
        # 얘는 리시트?? 맞나,,, 그랬던거 같음 list찾는건 int??
        return [img.get('src') for img in img_list]

    #
    def download_all_images(self):
        # Sel.fet__image_url_list_list가 불러온값을 url에 넣어줌
        for url in self.get_image_url_list():
            # 위에 Url에 slef download에 ..... 음,,,, 넣어줌??
            self.download(url)

    def download(self, url_img):
        """
        :param url_img: 실제 이미지의 URL
        :return:
        """
        # 서버에서 거부하지 않도록 HTTP헤더 중 'Referer'항목을 채워서 요청미
        # referer 란
        # http 긁어올때 내가 어디에 있는지 전송해주는거
        url_referer = f'http://comic.naver.com/webtoon/list.nhn?titleId={self.webtoon_id}'
        #딕셔너리
        headers = {
            'Referer': url_referer,
        }

        response = requests.get(url_img, headers=headers)

        # 이미지 URL에서 이미지명을 가져옴
        ## -1은 list의 마지막
        file_name = url_img.rsplit('/', 1)[-1]

        ## 파일 저장경로
        dir_path = f'data/{self.webtoon_id}/{self.no}'
        #없으면 만들어서 정리
        os.makedirs(dir_path, exist_ok=True)

        # 이미지가 저장될 파일 경로, 'wb'모드로 열어 이진데이터를 기록한다
        ## 위에꺼 이해는됨,,,
        ## 이진데이터란?
        ## 본 단위가 2개의 상태만 가지는 데이터이다. 일반적으로 이진법과 불 대수에서는 2개의 상태를 0과 +1로 나타낸다.
        ## 이렇게 나오는데... 그냥 이진법 인거 같은데 +1은 왜 나타내는지 이해가 안됨 _ 일단 알아둠
        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)

#여기서 중요함 무한츠쿠요미 시발점
class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self._title = None
        self._author = None
        self._description = None
        self._episode_list = list()
        self._html = ''
        self.page = 1  # 제일 최신 페이지 ex)죽음에 관하여 1페이지에 있는 10화 ?
    # 기억도 안날뿐더러 봐도 이해가 안됨,,,
    def _get_info(self, attr_name):
        # if의 부정문인데 self.set_info를 호출
        if not getattr(self, attr_name):
            self.set_info()
            # getattr attr_name 객체값을 리턴
        return getattr(self, attr_name)

    # 이부분이 show_info에 있는걸 줌??
    # 밑에서 위로 다시 올라
    @property
    def title(self):
        return self._get_info('_title')

    @property
    def author(self):
        return self._get_info('_author')

    @property
    def description(self):
        return self._get_info('_description')

    @property
    def html(self):

        # 인스턴스의 html속성값이 False(빈 문자열)일 경우
        # HTML파일을 저장하거나 불러올 경로
        file_path = 'data/episode_list-{webtoon_id}-{page}.html'.format(
            webtoon_id=self.webtoon_id,
            page=self.page)
        ## HTTP 줄 url
        url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
        ## 파라미터 줄 self.webtoon_id와 page
        params = {
            'titleId': self.webtoon_id,
            'page': self.page,
        }
        # HTML파일 유무 확인
        if os.path.exists(file_path):
            # 있으면 해당 파일 읽어서 html예 줌
            html = open(file_path, 'rt').read()
        else:
            # 만약 없다면 requests를 사용하는데 url_episode, 파라미터를 get함
            # 그 값은 reponse
            response = requests.get(url_episode_list, params)
            # print(response.url) 확인..
            # html = reponse로 받은 text속성
            html = response.text
            # 위에 텍스트파일 받은걸 쓰고 저장하기
            open(file_path, 'wt').write(html)
            # slef._html이 html 갑
        self._html = html
        # 이걸 다시 리턴
        # 이게 중요함!!
        #위에 프로퍼티로 받은
        return self._html

    def show_info(self):

        return '{title} \n' \
               '작가 : {author} \n' \
               '설명 : {description} \n' \
               '총 연재횟수 : {episode_list} 회'.format(title=self.title,
                                                  author=self.author,
                                                  description=self.description,
                                                  episode_list=len(self.episode_list))

    def set_info(self):
        """
        자신의 html속성을 파싱한 결과를 사용해
        자신의 title, author, description속성값을 할당
        :return: None
        """
        # BeautifulSoup클래스형 객체 생성 및 soup변수에 할당
        soup = BeautifulSoup(self.html, 'lxml')
        # 간단함 태그 접근해서 원하는 속성??을 받아
        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)
        # div.detail > p (설명)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        # 자신의 html데이터를 사용해서 (웹에서 받아오거나, 파일에서 읽어온 결과)
        # 자신의 속성들을 지정
        self._title = title
        self._author = author
        self._description = description

    def crawl_episode_list(self):
        """
        자기자신의 webtoon_id에 해당하는 HTML문서에서 Episode목록을 생성
        :return:
        """
        while True:줌
        # 반복문 저얼대 break가 없는이상 계속 돔
            # BeautifulSoup클래스형 객체 생성 및 soup변수에 할당
            soup = BeautifulSoup(self.html, 'lxml')

            # 에피소드 목록을 담고 있는 table
            table = soup.select_one('table.viewList')
            # table내의 모든 tr요소 목록
            tr_list = table.select('tr')
            # list를 리턴하기 위해 선언
            # for문을 다 실행하면 episode_lists 에는 Episode 인스턴스가 들어가있음

            # 첫 번째 tr은 thead의 tr이므로 제외, tr_list의 [1:]부터 순회옴
            for index, tr in enumerate(tr_list[1:]):
                # 에피소드에 해당하는 tr은 클래스가 없으므로,
                # 현재 순회중인 tr요소가 클래스 속성값을 가진다면 continue
                if tr.get('class'):
                    continue

                # 현재 tr의 첫 번째 td요소의 하위 img태그의 'src'속성값
                url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
                # 현재 tr의 첫 번째 td요소의 자식   a태그의 'href'속성값
                from urllib import parse
                url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
                # query_string = 웹클라이언트에서 서버로 전달받는 방식 이해하면 복잡하니까 외우자
                # 파라미터 url은
                query_string = parse.urlsplit(url_detail).query
                query_dict = parse.parse_qs(query_string)
                # print(query_dict)
                no = query_dict['no'][0]

                # 현재 tr의 두 번째 td요소의 자식 a요소의 내용
                title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
                # 현재 tr의 세 번째 td요소의 하위 strong태그의 내용
                rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
                # 현재 tr의 네 번째 td요소의 내용
                created_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

                # 매 에피소드 정보를 Episode 인보스턴스로 생성
                # new_episode = Episode 인스턴스
                new_episode = Episode(
                    webtoon_id=self.webtoon_id,
                    no=no,
                    url_thumbnail=url_thumbnail,
                    title=title,
                    rating=rating,
                    created_date=created_date,
                )
                # episode_lists Episode 인스턴스들 추가
                ## self._episode_list.append가 (new_episode 부분을 호출하는데
                self._episode_list.append(new_episode)
                # no가 1인 경우 break
                # 위에꼐 no가 1이변 break는 웹툰의 첫화를 뜻함
                # 무한 츠쿠요미를 통해서 페이지의 끝 화를 찾으면 여기서 stop이 걸림
            if no == '1':
                break
            # 그 경우가 아니면 page를 1씩 추가하여 다으메이지 웹툰 리스트 크롤링
            # 위에꺼처럼 맨끝페이지의 1을 찾지 못하면 페이지를 (파라미터가 올라감) 1 추가해
            else:
                self.page += 1

    @property
    def episode_list(self):
        # self.episode_list가 빈 리스트가 아니라면
        #  -> self.episode_list를 반환
        # self.episode_list가 비어있다면
        #  채우는 함수를 실행해서 self.episode_list리스트에 값을 채운 뒤
        #  self.episode_list를 반환

        # 다했으면
        # episode_list속성이름을 _episode_list로 변경
        # 이 함수의 이름을 episode_list로 변경 후 property설정
        if not self._episode_list:
            self.crawl_episode_list()
        return self._episode_list

        # if self.episode_list:
        #     return self.episode_list
        # else:
        #     self.crawl_episode_list()
        #     return self.episode_list


if __name__ == '__main__': #  - if는 블록
                            # - name은 모듈의 이름을 담은 내장변수, 모듈이 직접 실행된느 경우에만
                            # name은 main으
    webtoon1 = Webtoon(651673)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)
    e1 = webtoon1.episode_list[0]
    e1.download_all_images()
