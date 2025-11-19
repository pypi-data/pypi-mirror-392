# -- coding: utf-8 --
import ddddocr
import requests
from loguru import logger
from io import BytesIO


class VerifyCodeIdentification:
    def __init__(self):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

    def crawl_image(self, url):
        if not url:
            logger.error("URL不能为空")
            return None

        if 'http' not in url:
            logger.error("URL异常")
            return None

        try:
            image_res = requests.get(url, headers=self.headers, timeout=60)
            image_res.raise_for_status()
            # 使用 BytesIO 更高效地处理大文件
            image_data = BytesIO()
            for chunk in image_res.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    image_data.write(chunk)

            image_bytes = image_data.getvalue()
            if not image_bytes:
                logger.error("下载的图片数据为空")
                return None

            return image_bytes

        except requests.exceptions.Timeout:
            logger.error(f"图片下载超时: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"图片下载 HTTP错误: {e}, URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"图片下载 请求异常: {e}, URL: {url}")
            return None
        except Exception as e:
            logger.error(f"图片处理异常: {e}, URL: {url}")
            return None

    def run(self, img_bytes=None, img_path=None, img_url=None):
        # 英文数字验证码识别
        if img_bytes:
            img_bytes = img_bytes
        elif img_url:
            img_bytes = self.crawl_image(img_url)
        else:
            with open(img_path, 'rb') as f:
                img_bytes = f.read()
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(img_bytes)
        return res

# print(VerifyCodeIdentification().run(img_url='https://zfcg.czt.fujian.gov.cn/gpcms/rest/web/v2/index/getVerify?1763434244374'))
