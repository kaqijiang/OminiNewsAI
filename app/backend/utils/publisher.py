import json
import time
import random
from datetime import datetime
import requests
from loguru import logger
from api.models import PlatformConfig


class Publisher:
    def __init__(self, platform_config: PlatformConfig):
        # 初始化时直接设置 config
        self.config = {
            "wechat": {
                "appid": platform_config.wechat_appid,
                "secret": platform_config.wechat_secret
            },
            "xing_qiu": {
                "access_token": platform_config.xing_qiu_access_token,
                "session_id": platform_config.xing_qiu_session_id,
                "group_id": platform_config.xing_qiu_group_id
            },
            "jue_jin": {
                "session_id": platform_config.jue_jin_session_id
            },
            "zhi_hu": {
                "z_c0": platform_config.zhi_hu_cookie
            }
        }



    def get_random_thumb_media_id(self):
        thumb_media_ids = [
            "YRyXvTWmgM7H8zOu3sIwa8aPl-AAFClXe0vpPitSyWRIrlB9WYDc_2mj-tBM7ogV",
            "YRyXvTWmgM7H8zOu3sIwayFbHGjkOwTXbx8aHJf7XPzUP2YGVZVp0tjKaTvS-gMh",
            "YRyXvTWmgM7H8zOu3sIwa2JI8oUfKhY2T8QeQ-5De9RaVuc4mYeaRbICYRuZ7FWk"
        ]
        return random.choice(thumb_media_ids)

    def get_jue_jin_random_thumb_media_id(self):
        thumb_media_ids = [
            "https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b134971f4f5f41dfb1a9a1b9fe2c8279~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3120&h=2336&s=6754948&e=png&b=aec7d6",
            "https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8591aa0bead94e998f54046fb08aa798~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3120&h=2336&s=8139506&e=png&b=236e94",
            "https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0bcbaaa8c8594280b403f6374a6cefed~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3120&h=2336&s=6965952&e=png&b=b8cad4"
        ]
        return random.choice(thumb_media_ids)

    def get_wechat_access_token(self, appid, secret):
        response = requests.get(
            f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}')
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        return None

    def format_wechat_content(self, selected_news, platform):

        main_title = f"{platform}{datetime.now().strftime('%m-%d')}"
        author = "阿杰呦"
        digest = ""
        full_content = (
            '<section style="font-size: 16px;"><section style="text-align: left; display: flex; flex-flow: row; margin-top: 10px; margin-bottom: 10px;">'
            '<section style="display: inline-block; width: auto; align-self: flex-end; border-left: 4px solid #ffca00; padding-left: 10px; box-sizing:border-box;">'
            '<p style="color: #2a2a2a; font-size: 18px; text-align: justify;" align="justify"><strong>新闻摘要</strong></p></section></section>'
        )
        stop_adding_to_digest = False

        for title, _ in selected_news:
            full_content += f"<p>{title}</p>"
            if not stop_adding_to_digest:
                if len(digest) + len(title) <= 118:
                    digest += title + "\n"
                else:
                    stop_adding_to_digest = True

        full_content += (
            '<section style="text-align: left; margin-top: 10px;"><p style="font-size: 17px; text-align: center;" align="center">'
            '<strong style="color: #ffca00;">扫码加入AI交流群</strong></p><p style="text-align: center;" align="center">'
            '<span style="color: #2a2a2a;"><strong>获得更多技术支持和交流</strong></span></p><p style="text-align: center;" align="center">'
            '<span style="color: #ffca00;"><strong>（请注明自己的职业）</strong></span></p></section><section style="text-align: center; margin-top: 10px; margin-bottom: 20px; line-height: 0;">'
            '<img class="rich_pages wxw-img" src="https://mmbiz.qpic.cn/sz_mmbiz_png/1JwdIWf27gmzM5uYBLUrfv4fJsezfHwlVwwZnicDVg738RNjibg5kBJmUib32FDY9H91icN2MZjRMTERUSy8iaRdDhQ/0.png" alt="图片" style="width: 243.719px !important; height: auto !important; vertical-align: initial; box-sizing:border-box;"></section></section>'
        )

        full_content += '<section style="font-size: 16px;">'
        for title, content in selected_news:
            full_content += (
                f'<section style="text-align: left; display: flex; flex-flow: row; margin-top: 10px; margin-bottom: 10px;">'
                f'<section style="display: inline-block; width: auto; align-self: flex-end; border-left: 4px solid #ffca00; padding-left: 10px; box-sizing:border-box;">'
                f'<p style="color: #2a2a2a; font-size: 18px; text-align: justify;" align="justify"><strong>{title}</strong></p></section></section>'
                f'<p>{content}</p><p></p>'
            )
        full_content += (
            '<hr>'
            '<section style="margin-top: 20px;"><p style="text-align: center;" align="center">'
            '关注「<span style="color: #a65bcb;">阿杰与AI</span>」公众号</p>'
            '<p style="text-align: center;" align="center"><span style="color: #ffca00;">与AI时代更靠近一点</span></p>'
            '<p style="text-align: center;" align="center"><span style="color: #2a2a2a; font-size: 14px;">提供服务：ChatGPT Plus 成品账号，团购低至 120/个、Plus正规代充、OpenAI直连API</span></p>'
            '<p style="text-align: center;" align="center"><span style="color: #2a2a2a; font-size: 14px;">资讯汇总 ominiai.cn </span></p>'
            '</section></section></section>'
        )

        thumb_media_id = self.get_random_thumb_media_id()
        return main_title, digest, author, full_content, thumb_media_id

    def post_to_wechat(self, selected_news, platform):

        json_data = self.get_wechat_access_token(self.config["wechat"]["appid"], self.config["wechat"]["secret"])
        access_token = json_data.get("access_token", None)
        if not access_token:
            logger.error(f"获取微信访问令牌失败\n{json_data.get('errmsg', None)}")
            return False, json_data.get('errmsg', None)

        title, digest, author, full_content, thumb_media_id = self.format_wechat_content(selected_news, platform)
        articles_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'
        data = {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": full_content,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0
                }
            ]
        }

        data_json = json.dumps(data, ensure_ascii=False)
        response = requests.post(articles_url, data=data_json.encode('utf-8'))
        if response.status_code == 200:
            logger.success(f"微信-草稿箱{response.text}")
            return True, ''
        else:
            logger.error(f"微信草稿箱发布失败: {response.text}")
            return False, response.text

    def format_xing_qiu_content(self, selected_news, platform):

        main_title = f"{platform}{datetime.now().strftime('%m-%d')}"
        author = "阿杰呦"
        digest = ""
        full_content = "<p><strong>新闻摘要</strong></p><p><br></p>"
        for title, _ in selected_news:
            full_content += f"<p>{title}</p>"
            digest += title + "\n"

        full_content += (
            '<p><br></p>'
            '<p class="ql-align-center"><strong style="color: rgb(255, 202, 0);">扫码加入AI交流群</strong></p>'
            '<p class="ql-align-center"><strong style="color: rgb(42, 42, 42);">获得更多技术支持和交流</strong></p>'
            '<p class="ql-align-center"><strong style="color: rgb(255, 202, 0);">（请注明自己的职业）</strong></p>'
            '<p><br></p>'
            '<p><img src="https://article-images.zsxq.com/FnTqb5S22mGmsqoyKb9HcNYSXEAa" style="display: block; margin: auto;" data-imageid="214484188541521" width="304"></p>'
            '<p><br></p>'
        )

        for title, content in selected_news:
            full_content += f"<p><strong>{title}</strong></p><p><br></p><p>{content}</p><p><br></p>"

        full_content += (
            '<hr class="article-hr" style="height: 0px">'
            '<p><br></p>'
            '<p class="ql-align-center">关注「<span style="color: rgb(166, 91, 203);">阿杰与AI</span>」公众号</p>'
            '<p class="ql-align-center"><span style="color: rgb(255, 202, 0);">与AI时代更靠近一点</span></p>'
            '<p class="ql-align-center"><span style="color: rgb(42, 42, 42); font-size: 14px;">提供服务：ChatGPT Plus 成品账号，团购低至 120/个、Plus正规代充、OpenAI直连API</span></p>'
            '<p style="text-align: center;" align="center"><span style="color: #2a2a2a; font-size: 14px;">资讯汇总 ominiai.cn </span></p>'
        )

        return main_title, author, digest, full_content

    def post_to_xing_qiu(self, selected_news, platform):
        url = "https://api.zsxq.com/v2/articles"
        top_url = f"https://api.zsxq.com/v2/groups/{self.config['xing_qiu']['group_id']}/topics"
        headers = {"Content-Type": "application/json"}
        cookies = {
            'zsxq_access_token': self.config["xing_qiu"]["access_token"],
            'abtest_env': 'product',
            'zsxqsessionid': self.config["xing_qiu"]["session_id"]
        }

        main_title, author, digest, full_content = self.format_xing_qiu_content(selected_news, platform)
        article_request = {
            "req_data": {
                "group_id": self.config["xing_qiu"]["group_id"],
                "article_id": "",
                "title": main_title,
                "content": full_content,
                "image_ids": [],
                "scheduled_article": False
            }
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(article_request))
        if response.status_code == 200:
            json_data = response.json()
            succeeded = json_data.get("succeeded", False)
            logger.info("知识星球-创建草稿完成")
            if succeeded:
                time.sleep(1)
                jsond_data = {
                    "req_data": {
                        "type": "talk",
                        "text": f"{main_title}\n\n{digest}",
                        "article_id": json_data["resp_data"].get("article_id", "")
                    }
                }
                response = requests.post(top_url, headers=headers, cookies=cookies, data=json.dumps(jsond_data))
                if response.status_code == 200:
                    logger.success("知识星球-内容更新成功✅ https://wx.zsxq.com/dweb2/index/group/88885828488882")
                    return True, ""
                else:
                    logger.error(f"知识星球内容更新失败: {response.text}")
                    return False, response.text
            else:
                logger.error(f"知识星球文章发布失败: {json_data}")
                return False, json_data
        else:
            logger.error(f"请检查知识星球接口: {response.text}")
            return False,response.text

    def format_jue_jin_content(self, selected_news, platform):

        main_title = f"{platform}{datetime.now().strftime('%m-%d')}"
        jue_jin_img = self.get_jue_jin_random_thumb_media_id()
        full_content = f"\n![{main_title}]({jue_jin_img})\n"
        full_content += "**<p align=left>新闻摘要</p>** "
        digest = ""
        stop_adding_to_digest = False
        for title, _ in selected_news:
            full_content += f"<p>{title}</p>"
            if not stop_adding_to_digest:
                if len(digest) + len(title) <= 98:
                    digest += title + "\n"
                else:
                    stop_adding_to_digest = True

        full_content += (
            '<p align="center"><strong style="color: rgb(255, 202, 0);">扫码加入AI交流群</strong></p>'
            '<p align="center"><strong style="color: rgb(42, 42, 42);">获得更多技术支持和交流</strong></p>'
            '<p align="center"><strong style="color: rgb(255, 202, 0);">（请注明自己的职业）</strong></p>'
            '<p align="center"><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9068ad79e042495089101f1ea830b5ff~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1080&h=1078&s=658631&e=png&b=fbfbfb" alt="123" width="30%" /></p> '

        )

        for title, content in selected_news:
            full_content += f"**<p align=left>{title}</p>** <p align=left>{content}</p>"

        full_content += (
            '<p align="center">关注「阿杰与AI」公众号</p> '
            '<p align="center">与AI时代更靠近一点</p> '
            '<p style="text-align: center;" align="center"><span style="color: #2a2a2a; font-size: 14px;">资讯汇总 ominiai.cn </span></p>'
        )

        return main_title, digest, jue_jin_img, full_content

    def post_to_jue_jin(self, selected_news, platform):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
        cookies = {
            'sessionid': self.config["jue_jin"]["session_id"]
        }
        session.cookies.update(cookies)

        main_title, digest, jue_jin_img, full_content = self.format_jue_jin_content(selected_news, platform)

        url = "https://api.juejin.cn/content_api/v1/article_draft/create?aid=2608&uuid="
        headers = {"Content-Type": "application/json"}

        article_request = {
            "category_id": "0",
            "tag_ids": [],
            "link_url": "",
            "cover_image": "",
            "title": main_title,
            "brief_content": digest,
            "edit_type": 10,
            "html_content": "deprecated",
            "mark_content": "",
            "theme_ids": []
        }

        response = session.post(url, headers=headers, data=json.dumps(article_request))
        if response.status_code == 200:
            json_data = response.json()

            if json_data.get("err_msg") == 'success':
                data = json_data.get("data")
                if data:
                    article_draft_id = data.get("id")
                    logger.info(f"掘金-创建草稿完成，草稿ID:{article_draft_id}")
                    time.sleep(1)
                else:
                    logger.error(f"掘金-创建草稿完成，草稿ID:{json_data}")
                    return

                draft_url = "https://api.juejin.cn/content_api/v1/article_draft/update?aid=2608&uuid="
                draft_request = {
                    "id": article_draft_id,
                    "category_id": "6809637773935378440",
                    "tag_ids": [
                        "6809641073527226376",
                        "7197380216015028281",
                        "7197380506562871333"
                    ],
                    "link_url": "",
                    "cover_image": jue_jin_img,
                    "title": main_title,
                    "brief_content": digest,
                    "edit_type": 10,
                    "html_content": "deprecated",
                    "mark_content": full_content,
                    "theme_ids": [
                        "7210228048107896891"
                    ]
                }
                response = session.post(draft_url, headers=headers, data=json.dumps(draft_request))
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data.get("err_msg") == 'success':
                        logger.info(f"掘金-更新草稿完成")
                        time.sleep(1)
                    else:
                        logger.error(f"掘金-更新草稿失败，草稿ID:{json_data}")
                        return
                    column_id = "7369789429547466763"

                    push_url = "https://api.juejin.cn/content_api/v1/article/publish?aid=2608&uuid="
                    push_request = {
                        "draft_id": article_draft_id,
                        "sync_to_org": False,
                        "column_ids": [column_id],
                        "theme_ids": ["7210228048107896891"],
                        "encrypted_word_count": 1078465,
                        "origin_word_count": 3967
                    }
                    response = session.post(push_url, headers=headers, data=json.dumps(push_request))
                    if response.status_code == 200:
                        json_data = response.json()
                        if json_data.get("err_msg") == 'success':
                            logger.success(f"掘金-发布文章完成✅ https://juejin.cn/user/1468603264933742?utm_source=gold_browser_extension")
                            return True, ''
                        else:
                            return False, response
                    else:
                        return False, response
                else:
                    return False, response
            else:
                return False, json_data
        else:
            return False, response.text


    def format_zhi_hu_content(self, selected_news, platform):

        main_title = f"{platform}{datetime.now().strftime('%m-%d')}"
        jue_jin_img = self.get_jue_jin_random_thumb_media_id()
        full_content = f'<img src="{main_title}" data-caption="{main_title}" data-size="normal" data-rawwidth="3120" data-rawheight="2336" data-watermark="watermark" data-original-src="https://picx.zhimg.com/v2-d90a4817ae309c7f03630e06c3d23482_720w.jpg?source=d16d100b" data-watermark-src="https://pic1.zhimg.com/v2-772c48297a24ecd8679ed29c2d19f2b4_720w.jpg?source=d16d100b" data-private-watermark-src=""/>'

        full_content += '<p><b>新闻摘要</b></p><p><br></p>'
        digest = ""
        stop_adding_to_digest = False
        for title, _ in selected_news:
            full_content += f"<p>{title}</p>"
            if not stop_adding_to_digest:
                if len(digest) + len(title) <= 98:
                    digest += title + "\n"
                else:
                    stop_adding_to_digest = True

        full_content += (
            '<p><b>扫码加入AI交流群</b></p>'
            '<p><b>获得更多技术支持和交流</b></p>'
            '<p><b>（请注明自己的职业）</b></p><p><br></p>'
            '<img src="https://picx.zhimg.com/v2-bcd804d6c84e0623eeaf0c015bb856c6_720w.png?source=d16d100b" data-caption="123" data-size="normal" data-rawwidth="1080" data-rawheight="1078" data-watermark="watermark" data-original-src="https://pica.zhimg.com/v2-bcd804d6c84e0623eeaf0c015bb856c6_720w.jpg?source=d16d100b" data-watermark-src="https://pic1.zhimg.com/v2-9516bfebad32e6133f85f7efac2d94da_720w.jpg?source=d16d100b" data-private-watermark-src=""/>'
            '<p><br></p>'
        )

        for title, content in selected_news:
            full_content += f'<p><b>{title}</b></p><p>{content}</p>'

        full_content += (
            '<p">关注「阿杰与AI」公众号、与AI时代更靠近一点</p> '
            '<p style="text-align: center;" align="center"><span style="color: #2a2a2a; font-size: 14px;">资讯汇总 ominiai.cn </span></p>'
        )

        return main_title, digest, jue_jin_img, full_content

    def post_to_zhi_hu(self, selected_news, platform):

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
        cookies = {
            "z_c0": self.config["zhi_hu"]["z_c0"]
        }
        session.cookies.update(cookies)

        main_title, digest, jue_jin_img, full_content = self.format_zhi_hu_content(selected_news, platform)

        url = "https://zhuanlan.zhihu.com/api/articles/drafts"
        headers = {"Content-Type": "application/json"}

        draft_request = {
            "title": main_title,
            "delta_time": 0
        }
        response = session.post(url, headers=headers, data=json.dumps(draft_request))
        if response.status_code == 200:
            json_data = response.json()
            draft_id = json_data.get("id")
            logger.info(f"知乎-创建草稿完成，草稿ID{draft_id}")
            update_draft = f"https://zhuanlan.zhihu.com/api/articles/{draft_id}/draft"

            update_draft_request = {
                "content": full_content,
                "table_of_contents": False,
                "delta_time": 3
            }
            update_draft_img_request = {
                "titleImage": 'https://picx.zhimg.com/v2-939b3f1a399d8d7ea898710fd42bccee.png',
                "isTitleImageFullScreen": False,
                "delta_time": 40
            }
            session.patch(update_draft, data=json.dumps(update_draft_request))
            session.patch(update_draft, data=json.dumps(update_draft_img_request))
            logger.info(f"知乎-更新草稿完成")
            tag_url = f"https://zhuanlan.zhihu.com/api/articles/{draft_id}/topics"
            tags = [
                {
                    "introduction": "",
                    "avatarUrl": "https://pic1.zhimg.com/80/v2-40e779d5c5e6bcebda41e92d50594618_l.jpg?source=4e949a73",
                    "name": "每日资讯",
                    "url": "https://www.zhihu.com/topic/25535388",
                    "type": "topic",
                    "excerpt": "",
                    "id": "25535388"
                },
                {
                    "introduction": "",
                    "avatarUrl": "https://picx.zhimg.com/80/v2-abcfc476be997f037b0663f999fd2def_l.jpg?source=4e949a73",
                    "name": "OpenAI",
                    "url": "https://www.zhihu.com/topic/20083046",
                    "type": "topic",
                    "excerpt": "",
                    "id": "20083046"
                },
                {
                    "introduction": "",
                    "avatarUrl": "https://pic1.zhimg.com/80/v2-40e779d5c5e6bcebda41e92d50594618_l.jpg?source=4e949a73",
                    "name": "ChatGРТ",
                    "url": "https://www.zhihu.com/topic/27042831",
                    "type": "topic",
                    "excerpt": "",
                    "id": "27042831"
                }
            ]

            colum = "c_1775927617776308224"

            for tag in tags:
                tag_response = session.post(tag_url, data=json.dumps(tag))
                time.sleep(1)
            logger.info(f"知乎-更新标签完成")
            publish_url = f"https://www.zhihu.com/api/v4/content/publish"
            publish_request = {
                "action": "article",
                "data": {
                    "draft": {
                        "disabled": 1,
                        "id": str(draft_id),
                        "isPublished": False
                    },
                    "column": {
                        "column": [
                            colum
                        ]
                    },
                    "commentsPermission": {
                        "comment_permission": "anyone"
                    },
                    "creationStatement": {
                        "disclaimer_type": "none",
                        "disclaimer_status": "close"
                    },
                    "contentsTables": {
                        "table_of_contents_enabled": False
                    },
                    "commercialReportInfo": {
                        "isReport": 0
                    },
                    "hybridInfo": {
                        "contentSource": {
                            "channel": "newsReport"
                        }
                    }
                }
            }
            publish_response = session.post(publish_url, data=json.dumps(publish_request))
            if publish_response.status_code == 200:
                publish_response_json = publish_response.json()
                if publish_response_json.get('message') == 'success':
                    logger.success("知乎发布文章完成✅ https://www.zhihu.com/creator/manage/creation/article")
                    return True, ''
            else:
                logger.error(f"请求失败，状态码: {publish_response.status_code}, 响应内容: {publish_response.text}")
                return False, publish_response.text

        else:
            return False, response.text
