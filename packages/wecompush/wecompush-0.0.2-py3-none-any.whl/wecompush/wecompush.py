import logging
import os
import re
import time
import base64
import hashlib
from typing import Dict, Any, Optional, List

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from .exceptions import (
    WecomConfigError,
    WecombotError
)

# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Bot():
    """
    企业微信群机器人推送客户端

    通过webhook_url直接推送消息到企业微信群
    """
    def __init__(self, webhook_url: str, timeout: int = 10, retry_count: int = 3, retry_interval: float = 1.0):
        """
        初始化客户端

        Args:
            webhook_url: 群机器人webhook地址，用于群机器人推送
            timeout: 请求超时时间，默认10秒
            retry_count: 失败重试次数，默认3次
            retry_interval: 重试间隔时间（秒），默认1秒
        """
        self.webhook_url = webhook_url
        self.key = re.search(r'key=([a-f0-9\-]+)', self.webhook_url).group(1)
        self.base_url = re.search(r'^(.*?)/send', self.webhook_url).group(1)
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        # self.headers = {'Content-Type': 'application/json'}

    def send_bot_message(self, msg_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送群机器人消息

        Args:
            msg_type: 消息类型，支持text、markdown、image、news等
            content: 消息内容，根据msg_type提供相应格式的内容

        Returns:
            发送结果

        Raises:
            WecomConfigError: 缺少webhook_url或参数错误
            WecombotError: 发送消息失败
        """
        payload = {
            "msgtype": msg_type,
            msg_type: content
        }

        retry = 0
        while retry <= self.retry_count:
            try:
                with httpx.Client() as client:
                    response = client.post(url=self.webhook_url, json=payload, timeout=self.timeout)
                    if response.status_code == 200:
                        result = response.json()

                if result.get('errcode') != 0:
                    raise WecombotError(
                        "发送群机器人消息失败",
                        errcode=result.get('errcode'),
                        errmsg=result.get('errmsg')
                    )

                logger.info(f"群机器人消息发送成功，消息类型: {msg_type}")
                return result
            except (httpx.RequestError, WecombotError) as e:
                retry += 1
                if retry > self.retry_count:
                    raise WecombotError(f"发送群机器人消息失败，重试次数已达上限: {str(e)}")

                logger.warning(f"发送群机器人消息失败，{retry}秒后重试: {str(e)}")
                time.sleep(self.retry_interval)

    def send_text(self, content: str, mentioned_list: Optional[List[str]] = None,
                  mentioned_mobile_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        发送文本消息

        Args:
            content: 消息内容，最长不超过2048个字节
            mentioned_list: userid的列表，提醒群中的指定成员@某一人
            mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员@某一人

        Returns:
            发送结果
        """
        text_content = {"content": content}

        if mentioned_list:
            text_content["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            text_content["mentioned_mobile_list"] = mentioned_mobile_list

        return self.send_bot_message("text", text_content)

    def send_markdown(self, content: str) -> Dict[str, Any]:
        """
        发送Markdown消息

        Args:
            content: Markdown格式的消息内容，最长不超过4096个字节

        Returns:
            发送结果
        """
        return self.send_bot_message("markdown", {"content": content})

    def send_markdown_v2(self, content: str) -> Dict[str, Any]:
        """
        发送Markdown V2消息
        Markdown V2支持更丰富的样式和表情等功能

        Args:
            content: Markdown V2格式的消息内容，最长不超过4096个字节

        Returns:
            发送结果
        """
        return self.send_bot_message("markdown_v2", {"content": content})

    def send_image(self, base64: str, md5: str) -> Dict[str, Any]:
        """
        发送图片消息

        Args:
            base64: 图片的base64编码
            md5: 图片的md5值

        Returns:
            发送结果
        """
        return self.send_bot_message("image", {"base64": base64, "md5": md5})

    def send_file(self, media_id: str) -> Dict[str, Any]:
        """
        发送文件消息

        Args:
            media_id: 文件的media_id

        Returns:
            发送结果
        """
        return self.send_bot_message("file", {"media_id": media_id})

    def send_voice(self, media_id: str) -> Dict[str, Any]:
        """
        发送语音消息

        Args:
            media_id: 文件的media_id

        Returns:
            发送结果
        """
        return self.send_bot_message("voice", {"media_id": media_id})

    def send_news(self, articles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        发送图文消息

        Args:
            articles: 图文消息列表，每个元素包含title、description、url、picurl
                      最多支持8条图文消息

        Returns:
            发送结果

        Raises:
            WecomConfigError: 参数错误
        """
        if not articles:
            raise WecomConfigError("articles不能为空")

        if len(articles) > 8:
            raise WecomConfigError("articles最多支持8条图文消息")

        for article in articles:
            if not all(key in article for key in ["title", "description", "url", "picurl"]):
                raise WecomConfigError("每个article必须包含title、description、url、picurl字段")

        return self.send_bot_message("news", {"articles": articles})

    def upload_media(self, filepath: str, filetype: str = 'file') -> str:
        """
        文件上传

        Args:
            filepath: 推送文件路径
            filetype: 文件file、语音voice

        Returns:
            发送结果
        """

        self.upload_media_url = f'{self.base_url}/upload_media?key={self.key}&type={filetype}'
        headers = {'Content-Type': 'multipart/form-data'}
        with open(filepath, 'rb') as file:
            data = {'file': file}
            with httpx.Client() as client:
                response = client.post(url=self.upload_media_url, files=data, headers=headers, timeout=None)
                if response.status_code == 200:
                    result = response.json()
                    media_id = result['media_id']
                    return media_id

    def send_file_by_path(self, filepath: str) -> Dict[str, Any]:
        """
        通过文件路径发送文件消息

        Args:
            filepath: 文件路径

        Returns:
            发送结果
        """
        media_id = self.upload_media(filepath=filepath, filetype='file')
        return self.send_file(media_id)

    def send_voice_by_path(self, filepath: str) -> Dict[str, Any]:
        """
        通过文件路径发送语音消息

        Args:
            filepath: 文件路径

        Returns:
            发送结果
        """
        media_id = self.upload_media(filepath=filepath, filetype='voice')
        return self.send_voice(media_id)

    @staticmethod
    def image_to_base64_and_md5(filepath: str) -> Dict[str, str]:
        """
        将图片文件转换为base64编码和md5值

        Args:
            filepath: 图片文件路径

        Returns:
            包含base64和md5的字典

        Raises:
            WecomConfigError: 文件不存在或读取失败
        """
        if not os.path.exists(filepath):
            raise WecomConfigError(f"图片文件不存在: {filepath}")

        try:
            with open(filepath, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                md5_data = hashlib.md5(image_data).hexdigest()

            return {
                "base64": base64_data,
                "md5": md5_data
            }
        except Exception as e:
            raise WecomConfigError(f"读取图片文件失败: {str(e)}")

    def send_image_by_path(self, filepath: str) -> Dict[str, Any]:
        """
        通过文件路径发送图片消息

        Args:
            image_path: 图片文件路径

        Returns:
            发送结果
        """
        # 转换图片为base64和md5
        image_info = self.image_to_base64_and_md5(filepath)

        # 发送图片消息
        return self.send_image(image_info["base64"], image_info["md5"])

    def send_template_card(self, card_type: str, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送模板卡片消息

        Args:
            card_type: 卡片类型，支持text_notice、news_notice、button_interaction等
            card_data: 卡片数据，根据卡片类型提供相应格式的数据

        Returns:
            发送结果
        """
        return self.send_bot_message("template_card", {card_type: card_data})