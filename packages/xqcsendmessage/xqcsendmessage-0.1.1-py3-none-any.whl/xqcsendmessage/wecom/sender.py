# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:09:58.674Z
# 文件描述：企业微信消息发送器
# 文件路径：xqcsendmessage/wecom/sender.py

import httpx
from typing import Any, Dict, Optional

from ..core.abc import Sender, AsyncSender
from ..core.exceptions import HttpError, AuthError, SendMessageError
from ..core.logger import default_logger


class WeComWebhookSender(Sender):
    """
    企业微信 Webhook 同步消息发送器。
    """

    def __init__(self, webhook: str):
        """
        初始化企业微信 Webhook 同步发送器。

        :param webhook: 企业微信机器人的 Webhook 地址。
        """
        self.webhook = webhook
        self.logger = default_logger

    def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        发送企业微信 Webhook 消息。

        :param message: 消息内容，符合企业微信机器人支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        message.update(kwargs) # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.webhook, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信 Webhook 消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信 Webhook 消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信 Webhook 消息时发生未知错误: {e}")
            raise


class AsyncWeComWebhookSender(AsyncSender):
    """
    企业微信 Webhook 异步消息发送器。
    """

    def __init__(self, webhook: str):
        """
        初始化企业微信 Webhook 异步发送器。

        :param webhook: 企业微信机器人的 Webhook 地址。
        """
        self.webhook = webhook
        self.logger = default_logger

    async def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送企业微信 Webhook 消息。

        :param message: 消息内容，符合企业微信机器人支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        message.update(kwargs) # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信 Webhook 消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信 Webhook 消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信 Webhook 消息时发生未知错误: {e}")
            raise


class WeComAppSender(Sender):
    """
    企业微信应用同步消息发送器。
    """

    def __init__(self, corpid: str, corpsecret: str, agentid: int):
        """
        初始化企业微信应用同步发送器。

        :param corpid: 企业 ID。
        :param corpsecret: 应用的 Secret。
        :param agentid: 应用的 AgentId。
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.logger = default_logger
        self._access_token: Optional[str] = None

    def _get_access_token(self) -> str:
        """
        获取 Access Token。

        :return: Access Token。
        """
        if self._access_token:
            return self._access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        try:
            with httpx.Client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    return self._access_token
                else:
                    raise AuthError(
                        f"获取 Access Token 失败: {data.get('errmsg')}")
        except httpx.HTTPStatusError as e:
            raise AuthError(f"获取 Access Token 请求失败: {e.response.text}")

    def _upload_media(self, image_path: str) -> str:
        """
        上传图片到企业微信临时素材。

        :param image_path: 图片文件的路径。
        :return: media_id。
        """
        access_token = self._get_access_token()
        upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": (image_path, f, "image/jpeg")}
                with httpx.Client() as client:
                    response = client.post(upload_url, files=files)
                    response.raise_for_status()
                    data = response.json()
                    if data.get("media_id"):
                        self.logger.info(f"🎉 图片上传成功: {data['media_id']}")
                        return data["media_id"]
                    else:
                        raise HttpError(f"上传图片失败: {data.get('errmsg')}")
        except FileNotFoundError:
            raise SendMessageError(f"❌ 图片文件未找到: {image_path}")
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 上传图片失败: {e.response.text}")
            raise HttpError(f"上传图片失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 上传图片时发生未知错误: {e}")
            raise

    def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        发送企业微信应用消息。

        :param message: 消息内容，符合企业微信应用消息支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        image_path = kwargs.pop("image_path", None)
        
        if image_path:
            media_id = self._upload_media(image_path)
            final_payload = {
                "msgtype": "image",
                "image": {"media_id": media_id},
                "touser": message.get("touser"),
                "toparty": message.get("toparty"),
                "totag": message.get("totag"),
            }
            final_payload = {k: v for k, v in final_payload.items() if v is not None}
        else:
            final_payload = message
            final_payload.update(kwargs)

        access_token = self._get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

        final_payload["agentid"] = self.agentid

        headers = {"Content-Type": "application/json"}
        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=final_payload)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信应用消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信应用消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信应用消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信应用消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信应用消息时发生未知错误: {e}")
            raise


class AsyncWeComAppSender(AsyncSender):
    """
    企业微信应用异步消息发送器。
    """

    def __init__(self, corpid: str, corpsecret: str, agentid: int):
        """
        初始化企业微信应用异步发送器。

        :param corpid: 企业 ID。
        :param corpsecret: 应用的 Secret。
        :param agentid: 应用的 AgentId。
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.logger = default_logger
        self._access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        """
        异步获取 Access Token。

        :return: Access Token。
        """
        if self._access_token:
            return self._access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    return self._access_token
                else:
                    raise AuthError(
                        f"获取 Access Token 失败: {data.get('errmsg')}")
        except httpx.HTTPStatusError as e:
            raise AuthError(f"获取 Access Token 请求失败: {e.response.text}")

    async def _upload_media_async(self, image_path: str) -> str:
        """
        异步上传图片到企业微信临时素材。

        :param image_path: 图片文件的路径。
        :return: media_id。
        """
        access_token = await self._get_access_token()
        upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
        
        try:
            # 注意：这里使用了同步文件读取，对于大文件可能会阻塞事件循环。
            with open(image_path, "rb") as f:
                files = {"media": (image_path, f, "image/jpeg")}
                async with httpx.AsyncClient() as client:
                    response = await client.post(upload_url, files=files)
                    response.raise_for_status()
                    data = response.json()
                    if data.get("media_id"):
                        self.logger.info(f"🎉 图片上传成功: {data['media_id']}")
                        return data["media_id"]
                    else:
                        raise HttpError(f"上传图片失败: {data.get('errmsg')}")
        except FileNotFoundError:
            raise SendMessageError(f"❌ 图片文件未找到: {image_path}")
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 上传图片失败: {e.response.text}")
            raise HttpError(f"上传图片失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 上传图片时发生未知错误: {e}")
            raise

    async def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送企业微信应用消息。

        :param message: 消息内容，符合企业微信应用消息支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        image_path = kwargs.pop("image_path", None)
        
        if image_path:
            media_id = await self._upload_media_async(image_path)
            final_payload = {
                "msgtype": "image",
                "image": {"media_id": media_id},
                "touser": message.get("touser"),
                "toparty": message.get("toparty"),
                "totag": message.get("totag"),
            }
            final_payload = {k: v for k, v in final_payload.items() if v is not None}
        else:
            final_payload = message
            final_payload.update(kwargs)

        access_token = await self._get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

        final_payload["agentid"] = self.agentid

        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=final_payload)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信应用消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信应用消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信应用消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信应用消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信应用消息时发生未知错误: {e}")
            raise
