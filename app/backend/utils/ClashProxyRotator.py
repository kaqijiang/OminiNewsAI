import requests
from loguru import logger
class ClashProxyRotator:
    def __init__(self, selector_name):
        self.api_url = "http://127.0.0.1:7893"
        self.selector_name = selector_name
        # 内部初始化节点列表
        self.node_names = [
            # {"name": "台湾ᴛᴡ专线解锁NF1", "available": True},
            # {"name": "台湾ᴛᴡ专线解锁NF2", "available": True},
            # {"name": "台湾ᴛᴡ专线解锁NF3", "available": True},
            # {"name": "台湾ᴛᴡ解ChatGPT¹‧⁵A", "available": True},
            # {"name": "台湾ᴛᴡ解ChatGPT¹‧⁵B", "available": True},
            # {"name": "台湾ᴛᴡ解ChatGPT¹‧⁵C", "available": True},
            # {"name": "台湾ᴛᴡ解ChatGPT¹‧⁵D", "available": True},
            # {"name": "新加坡sɢ专线×¹‧⁵VIP", "available": True},
            # {"name": "新加坡sɢ隧道加密×¹‧⁵A", "available": True},
            # {"name": "新加坡sɢ隧道加密×¹‧⁵B", "available": True},
            # {"name": "新加坡sɢ隧道加密×¹‧⁵C", "available": True},
            # {"name": "新加坡sɢ隧道加密×¹‧⁵D", "available": True},
            # {"name": "日本ᴊᴘ专线×¹‧⁵VIP", "available": True},
            {"name": "日本ᴊᴘ解锁Netflix×¹‧⁶A", "available": True},
            # {"name": "日本ᴊᴘ解锁Netflix×¹‧⁶B", "available": True},
            {"name": "日本ᴊᴘ隧道加密×¹‧⁵C", "available": True},
            # {"name": "A香港ʜᴋ专线IPLC限速×¹‧⁸", "available": True},
            # {"name": "B香港ʜᴋ专线IPLC限速×¹‧⁸", "available": True},
            # {"name": "C香港ʜᴋ专线IPLC限速×¹‧⁸", "available": True},
            # {"name": "D香港ʜᴋ专线IPLC限速×¹‧⁸", "available": True},
            # {"name": "E香港ʜᴋ解锁Netflix×¹‧⁷", "available": True},
            # {"name": "F香港ʜᴋ解锁Netflix×¹‧⁷", "available": True},
            # {"name": "G香港ʜᴋ解锁Netflix×¹‧⁷", "available": True},
            # {"name": "H香港ʜᴋ解锁Netflix×¹‧⁷", "available": True},
            # {"name": "I 香港ʜᴋ隧道加密× ¹‧⁵", "available": True},
            # {"name": "J香港ʜᴋ隧道加密×¹‧⁵", "available": True},
            # {"name": "K香港ʜᴋ隧道加密×¹‧⁵", "available": True},
            # {"name": "L香港ʜᴋ隧道加密×¹‧⁵", "available": True},
            {"name": "日本ᴊᴘ隧道加密×¹‧⁵D", "available": True}
        ]

        self.current_node_index = 0

    def switch_to_next_proxy(self):
        success = False
        attempts = 0
        while not success and attempts < len(self.node_names):
            node_info = self.node_names[self.current_node_index]
            node_name = node_info["name"]
            if not node_info["available"]:
                # 如果当前节点不可用，跳到下一个
                self.current_node_index = (self.current_node_index + 1) % len(self.node_names)
                attempts += 1
                continue

            url = f"{self.api_url}/proxies/{self.selector_name}"
            data = {"name": node_name}
            try:
                response = requests.put(url, json=data)
                response.raise_for_status()

                if response.status_code == 204:
                    logger.info(f"节点 {node_name} 已成功切换。")
                    success = True
                else:
                    logger.info(f"节点 {node_name} 切换响应: {response.json()}")
                    success = True
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Exception: {e}")
                # 标记为不可用并尝试下一个代理
                self.node_names[self.current_node_index]["available"] = False

            self.current_node_index = (self.current_node_index + 1) % len(self.node_names)
            attempts += 1

        return {"success": success, "error": None if success else "所有代理尝试失败"}

    def is_any_proxy_available(self):
        """
        检查是否至少有一个代理是可用的
        """
        return any(node["available"] for node in self.node_names)
    def mark_current_proxy_unavailable(self):
        """
        标记当前代理为不可用
        """
        if self.node_names:
            # 标记当前代理为不可用
            current_proxy = self.node_names[self.current_node_index]
            current_proxy["available"] = False

            logger.info(f"代理 {current_proxy['name']} 已被标记为不可用。")

            # 自动切换到下一个可用代理
            self.switch_to_next_proxy()
        else:
            logger.warning("代理列表为空，无法标记。")