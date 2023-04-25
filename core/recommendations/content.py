import re
import markdown


def markdown_to_text(markdown_string):
    """ 将 Markdown 文本转换为纯文本。 """
    # 使用 Python 的 `markdown` 库将 Markdown 转换为 HTML
    html = markdown.markdown(markdown_string)

    # 使用正则表达式删除 HTML 标签
    html_tag_pattern = re.compile('<.*?>')
    plain_text = re.sub(html_tag_pattern, '', html)

    return plain_text
