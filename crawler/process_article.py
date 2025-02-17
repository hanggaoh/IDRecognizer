import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup


import requests
import requests
from bs4 import BeautifulSoup


class Actress:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"Actress(name='{self.name}', url='{self.url}')"


class Article:
    def __init__(self, item_id, title, image_url, article_url):
        self.item_id = item_id
        self.title = title
        self.image_url = image_url
        self.article_url = article_url
        self.actresses = []
        self.image_downloaded = False

    def add_actress(self, actress):
        self.actresses.append(actress)

    def download_image(self):
        if self.image_url:
            try:
                response = requests.get(self.image_url, stream=True)
                response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
                filename = f"{self.item_id}.jpg"
                with open(filename, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                self.image_downloaded = True
                print(f"Image downloaded and saved as {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image for {self.item_id}: {e}")
        else:
            print("No image URL available to download.")

def process_article(article):
    # Extract relevant data
    title_element = article.find("h2", class_="archive-header-title")
    title = title_element.get_text(strip=True) if title_element else None
    article_url = title_element.find("a", href=True)["href"] if title_element else None
    # Find image URL in 'picture' tag with 'source'
    picture_tag = article.find('picture')
    if picture_tag:
        image_url = picture_tag.find('source', {'data-srcset': True})['data-srcset']
    else:
        img_tag = article.find('img', {'data-src': True}) or article.find('img', {'src': True})
        image_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else img_tag['src'] if img_tag else None


    # Attempt to find the ID text
    id_element = article.find("ul", class_="post-meta clearfix").find("i", class_="fa fa-circle-o") if article.find("ul", class_="post-meta clearfix") else None
    item_id = id_element.parent.get_text(strip=True) if id_element and id_element.parent else None

    # Create an Article object
    article_obj = Article(item_id, title, image_url, article_url)

    # Parse actress names and URLs
    actress_list = article.find("li", class_="actress-name")
    if actress_list:
        for link in actress_list.find_all("a", href=True):
            actress_name = link.get_text(strip=True)
            actress_url = link["href"]
            actress = Actress(actress_name, actress_url)
            article_obj.add_actress(actress)

    # Download the image for this article
    article_obj.download_image()

    return article_obj

class TestProcessArticle(unittest.TestCase):

    @patch("requests.get")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_process_article(self, mock_open, mock_requests_get):
        # Sample HTML snippet similar to the one you've provided
        html = """
        <article class="archive-list">
            <div class="eye-catch max-300">
                <a class="image-link-border" href="https://example.com">
                    <img class="animation lazyloaded" src="https://pics.dmm.co.jp/digital/amateur/mako022/mako022jp.jpg" data-src="https://pics.dmm.co.jp/digital/amateur/mako022/mako022jp.jpg" alt="ゆかり">
                </a>
            </div>
            <header class="archive-header">
                <h2 class="archive-header-title">
                    <a href="https://example.com" title="ゆかり">ゆかり</a>
                </h2>
                <ul class="post-meta clearfix">
                    <li class="actress-name">
                        <i class="fa fa-venus"></i><a href="https://example.com" rel="tag">大槻ゆりか</a>
                        <a href="https://example.com" rel="tag">乙羽あむ</a>
                    </li>
                    <li><i class="fa fa-clone"></i><a href="https://example.com">真昼の恋人</a></li>
                    <li><i class="fa fa-circle-o"></i>MAKO-022</li>
                    <li><i class="fa fa-clock-o"></i><time class="date published updated" datetime="2024-10-05">2024-10-05</time></li>
                    <li><a href="https://av-wiki.net/fanza-video/moodyz/moodyz-fresh/">MOODYZ Fresh</a></li>
                </ul>
            </header>
        </article>
        """

        # Create a BeautifulSoup object from the HTML
        article = BeautifulSoup(html, "html.parser").find("article")

        # Mocking the requests.get response
        mock_response = MagicMock()
        mock_response.iter_content = MagicMock(return_value=[b"test image content"])
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        # Call the process_article function
        article_obj = process_article(article)

        # Check if the image was downloaded and saved correctly
        mock_open.assert_called_once_with("MAKO-022.jpg", "wb")
        mock_requests_get.assert_called_once_with(
            "https://pics.dmm.co.jp/digital/amateur/mako022/mako022jp.jpg", stream=True
        )

        # Validate the properties of the created Article object
        self.assertEqual(article_obj.item_id, "MAKO-022")
        self.assertEqual(article_obj.title, "ゆかり")
        self.assertEqual(
            article_obj.image_url,
            "https://pics.dmm.co.jp/digital/amateur/mako022/mako022jp.jpg",
        )
        self.assertEqual(article_obj.article_url, "https://example.com")

        # Check if the actresses were added correctly
        self.assertEqual(len(article_obj.actresses), 2)
        self.assertEqual(article_obj.actresses[0].name, "大槻ゆりか")
        self.assertEqual(article_obj.actresses[0].url, "https://example.com")
        self.assertEqual(article_obj.actresses[1].name, "乙羽あむ")
        self.assertEqual(article_obj.actresses[1].url, "https://example.com")

        # Ensure the image was marked as downloaded
        self.assertTrue(article_obj.image_downloaded)

    @patch('requests.get')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_process_article_with_image_source(self, mock_open, mock_requests_get):
        # Sample HTML snippet
        html = '''
        <article class="archive-list">
            <div class="eye-catch max-147">
                <a class="image-link-border" href="https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Fdetail%2F%3D%2Fcid%3Dh_1605stsk00140%2F&amp;af_id=dmm8234-027&amp;ch_id=link" target="_blank" rel="nofollow noopener">
                    <picture>
                        <source media="(max-width: 480px)" data-srcset="https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140pl.jpg" srcset="https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140pl.jpg">
                        <source media="(min-width: 481px)" data-srcset="https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140ps.jpg" srcset="https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140ps.jpg">
                        <img class="animation lazyloaded" src="https://av-wiki.net/wp-content/themes/emanon-pro/lib/images/no-img/small-no-img.png" data-src="https://av-wiki.net/wp-content/themes/emanon-pro/lib/images/no-img/small-no-img.png" alt="アウトドアヨガ教室 青空痴〇">
                    </picture>
                </a>
            </div>
            <header class="archive-header">
                <h2 class="archive-header-title">
                    <a href="https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Fdetail%2F%3D%2Fcid%3Dh_1605stsk00140%2F&amp;af_id=dmm8234-027&amp;ch_id=link" title="アウトドアヨガ教室 青空痴〇" target="_blank" rel="nofollow noopener">アウトドアヨガ教室 青空痴〇</a>
                </h2>
                <ul class="post-meta clearfix">
                    <li class="actress-name">
                        <i class="fa fa-venus"></i><a href="https://av-wiki.net/av-actress/otoha-amu/" rel="tag">乙羽あむ</a> #
                        <a href="https://av-wiki.net/av-actress/%e5%a4%a7%e6%a7%bb%e3%82%86%e3%82%8a%e3%81%8b/" rel="tag">大槻ゆりか</a> #
                        <a href="https://av-wiki.net/av-actress/amemi-mea/" rel="tag">天美めあ</a> #
                        <a href="https://av-wiki.net/av-actress/%e6%9c%9b%e6%9c%88%e3%81%a4%e3%81%bc%e3%81%bf/" rel="tag">望月つぼみ</a>
                    </li>
                    <li><i class="fa fa-clone"></i><a href="https://av-wiki.net/fanza-video/shirouto-39/">素人39</a></li>
                    <li><i class="fa fa-circle-o"></i>STSK-140</li>
                    <li><i class="fa fa-clock-o"></i><time class="date published updated" datetime="2024-09-05">2024-09-05</time></li>
                </ul>
            </header>
        </article>
        '''

        # Create a BeautifulSoup object from the HTML
        article = BeautifulSoup(html, 'html.parser').find('article')

        # Mocking the requests.get response
        mock_response = MagicMock()
        mock_response.iter_content = MagicMock(return_value=[b'test image content'])
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        # Call the process_article function
        article_obj = process_article(article)

        # Check if the image was downloaded and saved correctly
        mock_open.assert_called_once_with('STSK-140.jpg', 'wb')
        mock_requests_get.assert_called_once_with('https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140pl.jpg', stream=True)

        # Validate the properties of the created Article object
        self.assertEqual(article_obj.item_id, 'STSK-140')
        self.assertEqual(article_obj.title, 'アウトドアヨガ教室 青空痴〇')
        self.assertEqual(article_obj.image_url, 'https://pics.dmm.co.jp/digital/video/h_1605stsk00140/h_1605stsk00140pl.jpg')
        self.assertEqual(article_obj.article_url, 'https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Fdetail%2F%3D%2Fcid%3Dh_1605stsk00140%2F&af_id=dmm8234-027&ch_id=link')

        # Check if the actresses were added correctly
        self.assertEqual(len(article_obj.actresses), 4)
        self.assertEqual(article_obj.actresses[0].name, '乙羽あむ')
        self.assertEqual(article_obj.actresses[0].url, 'https://av-wiki.net/av-actress/otoha-amu/')



if __name__ == "__main__":
    unittest.main()
