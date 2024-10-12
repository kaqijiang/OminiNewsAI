import re
import time
import poplib
import imaplib
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_tz

from loguru import logger
from imaplib import IMAP4_SSL
from poplib import POP3_SSL
import email
def get_openai_signup_link(email_name, password, method='IMAP', num_emails=10, display_email=None, target_email='noreply@tm.openai.com',
                    email_service='outlook.office365.com', max_attempts=2, retry_delay=5):
    """
    尝试从指定邮箱中获取注册链接。
    单独指定的链接
    """
    if display_email is None:
        logger.info(f"开始获取邮件」{display_email}")
    else:
        logger.info(f"开始获取邮件」")
    attempts = 0
    link = None

    while attempts < max_attempts:
        print(f"第 {attempts+1} 次获取邮件中...")
        mail = None
        try:
            if method.upper() == 'IMAP':
                mail = imaplib.IMAP4_SSL(email_service)
                mail.login(email_name, password)
                mail.select('inbox')
                result, data = mail.search(None, 'ALL')
                email_ids = data[0].split()[-num_emails:]
            elif method.upper() == 'POP3':
                mail = poplib.POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                _, msg_list, _ = mail.list()
                email_ids = [msg.split(b' ')[0] for msg in msg_list][-num_emails:]
            else:
                print("不受支持的方法。请选择 IMAP 或 POP3.")
                return None

            for i in reversed(email_ids):
                if method.upper() == 'IMAP':
                    _, data = mail.fetch(i, '(RFC822)')
                    raw_email = data[0][1]
                elif method.upper() == 'POP3':
                    index = int(i.decode('utf-8').split(' ')[0])
                    _, lines, _ = mail.retr(index)
                    raw_email = b'\r\n'.join(lines)

                msg = email.message_from_bytes(raw_email)
                email_from = decode_header(msg.get('From'))[0][0]
                email_to = decode_header(msg.get('To'))[0][0]
                if target_email in str(email_from) and (display_email is None or display_email in str(email_to)):
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                url_pattern = r'(https?://\S+)'
                                urls = re.findall(url_pattern, body)

                                if urls:
                                    link = urls[0]
                                    print(f"找到链接: ", {"url": link, "email": email_to})

                    else:
                        body = msg.get_payload(decode=True).decode()
                        urls = re.findall(r'(https?://\S+)', body)
                        if urls:
                            link = urls[0]
                            print(f"找到链接: ", {"url": link, "email": email_to})

                    # Delete the email after extracting the link
                    if method.upper() == 'IMAP':
                        mail.store(i, '+FLAGS', '\\Deleted')
                    elif method.upper() == 'POP3':
                        mail.dele(index)

        except Exception as e:
            print(f"错误发生，{e}秒后将重试...")
        finally:

            if mail:
                if method.upper() == 'IMAP':
                    mail.expunge()
                    mail.logout()
                elif method.upper() == 'POP3':
                    mail.quit()
        attempts += 1
        if not link and attempts < max_attempts:
            print(f"错误发生，{retry_delay}秒后将重试...")
            time.sleep(retry_delay)
        else:
            break
    return link



def get_claude_signup_link(email_name, password, method='IMAP', num_emails=10, display_email=None, target_email='support@mail.anthropic.com',
                    email_service='outlook.office365.com', max_attempts=2, retry_delay=5):
    """
    尝试从指定邮箱中获取注册链接。

    :param email_name: 邮箱用户名
    :param password: 邮箱密码
    :param method: 使用的方法，'IMAP' 或 'POP3'
    :param num_emails: 要检查的邮件数量
    :param display_email: 收件人邮箱
    :param target_email: 目标发件人邮箱
    :param email_service: 邮箱服务的IMAP/POP3服务器地址，默认为Hotmail
    :param max_attempts: 最大尝试次数
    :param retry_delay: 尝试之间的延迟时间（秒）
    :return: 找到的注册链接或None
    """
    if display_email is None:
        logger.info(f"开始获取邮件」{display_email}")
    else:
        logger.info(f"开始获取邮件」")
    attempts = 0
    mail = None
    while attempts < max_attempts:
        logger.info(f"第「{attempts+1}」次获取邮件中...")
        try:
            if method.upper() == 'IMAP':
                mail = IMAP4_SSL(email_service)
                mail.login(email_name, password)
                mail.select('inbox')
                result, data = mail.search(None, 'ALL')
                email_ids = data[0].split()[-num_emails:]

            elif method.upper() == 'POP3':
                mail = POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                _, email_ids, _ = mail.list()
                email_ids = email_ids[-num_emails:]
            else:
                logger.debug(f"不受支持的方法。请选择 IMAP or POP3.")
                return None
            links = []
            for i in reversed(email_ids):
                if method.upper() == 'IMAP':
                    _, data = mail.fetch(i, '(RFC822)')
                    raw_email = data[0][1]
                elif method.upper() == 'POP3':
                    index = int(i.decode('utf-8').split(' ')[0])
                    _, lines, _ = mail.retr(index)
                    raw_email = b'\r\n'.join(lines)

                msg = email.message_from_bytes(raw_email)
                email_from = decode_header(msg.get('From'))[0][0]
                email_to = decode_header(msg.get('To'))[0][0]
                if target_email in str(email_from) and (display_email is None or display_email in str(email_to)):
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                # 提取链接地址的正则表达式
                                url_pattern = r'(https?://\S+)'
                                urls = re.findall(url_pattern, body)
                                if len(urls) > 0:
                                    link = urls[0]
                                    links.append({"url": link, "email": email_to})
                                    print(f"找到链接: ", {"url": link, "email": email_to})

                    else:
                        body = msg.get_payload(decode=True).decode()
                        # 提取链接地址的正则表达式
                        url_pattern = r'(https?://\S+)'
                        urls = re.findall(url_pattern, body)
                        if len(urls) > 0:
                            link = urls[0]
                            links.append({"url": link, "email": email_to})
                            print(f"找到链接: ", {"url": link, "email": email_to})
                    # Delete the email after extracting the link
                    if method.upper() == 'IMAP':
                        mail.store(i, '+FLAGS', '\\Deleted')
                        print(f"删除中")
                    elif method.upper() == 'POP3':
                        mail.dele(index)
                        print(f"删除中{index}")

            return links
        except Exception as e:
            logger.debug(f"获取失败!{e}")
        finally:
            attempts += 1
            if attempts < max_attempts:
                time.sleep(retry_delay)
            if mail is not None:
                if method.upper() == 'IMAP':
                    mail.logout()
                elif method.upper() == 'POP3':
                    mail.quit()

    logger.debug(f"获取邮件失败，{max_attempts}秒后重试.")
    return None

def get_llama_signup_link(email_name, password, method='IMAP', num_emails=10, display_email=None, target_email='code-verification@site-members.com',
                    email_service='outlook.office365.com', max_attempts=2, retry_delay=5):
    """
    尝试从指定邮箱中获取注册链接。

    :param email_name: 邮箱用户名
    :param password: 邮箱密码
    :param method: 使用的方法，'IMAP' 或 'POP3'
    :param num_emails: 要检查的邮件数量
    :param display_email: 收件人邮箱
    :param target_email: 目标发件人邮箱
    :param email_service: 邮箱服务的IMAP/POP3服务器地址，默认为Hotmail
    :param max_attempts: 最大尝试次数
    :param retry_delay: 尝试之间的延迟时间（秒）
    :return: 找到的注册链接或None
    """
    if display_email is None:
        logger.info(f"开始获取邮件」{display_email}")
    else:
        logger.info(f"开始获取邮件」")
    attempts = 0
    mail = None
    while attempts < max_attempts:
        logger.info(f"第「{attempts+1}」次获取邮件中...")
        try:
            if method.upper() == 'IMAP':
                mail = IMAP4_SSL(email_service)
                mail.login(email_name, password)
                mail.select('inbox')
                result, data = mail.search(None, 'ALL')
                email_ids = data[0].split()[-num_emails:]

            elif method.upper() == 'POP3':
                mail = POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                _, email_ids, _ = mail.list()
                email_ids = email_ids[-num_emails:]
            else:
                logger.debug(f"不受支持的方法。请选择 IMAP or POP3.")
                return None
            numbers = None
            for i in reversed(email_ids):
                if method.upper() == 'IMAP':
                    _, data = mail.fetch(i, '(RFC822)')
                    raw_email = data[0][1]
                elif method.upper() == 'POP3':
                    index = int(i.decode('utf-8').split(' ')[0])
                    _, lines, _ = mail.retr(index)
                    raw_email = b'\r\n'.join(lines)

                msg = email.message_from_bytes(raw_email)
                email_from = decode_header(msg.get('From'))[0][0]
                email_to = decode_header(msg.get('To'))[0][0]
                if target_email in str(email_from) and (display_email is None or display_email in str(email_to)):
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                # 提取链接地址的正则表达式
                                pattern = r'<b>\s*(\d+)\s*</b>'
                                match = re.search(pattern, body)
                                if match:
                                    numbers = match.group(1)
                                    # Delete the email after extracting the link
                                    if method.upper() == 'IMAP':
                                        mail.store(i, '+FLAGS', '\\Deleted')
                                    elif method.upper() == 'POP3':
                                        mail.dele(index)
                                    print(f"获取验证码成功: 「{numbers}」")
                                    return numbers

            return numbers
        except Exception as e:
            logger.debug(f"获取失败!{e}")
        finally:
            attempts += 1
            if attempts < max_attempts:
                time.sleep(retry_delay)
            if mail is not None:
                if method.upper() == 'IMAP':
                    mail.logout()
                elif method.upper() == 'POP3':
                    mail.quit()
    logger.debug(f"获取邮件失败，{max_attempts}秒后重试.")
    return None

def get_groq_signup_link(email_name, password, method='IMAP', num_emails=5, display_email=None, target_email='noreply@groq.com',
                    email_service='outlook.office365.com', max_attempts=2, retry_delay=5):
    """
    尝试从指定邮箱中获取注册链接。
    单独指定的链接
    """
    if display_email is None:
        logger.info(f"开始获取邮件」")
    else:
        logger.info(f"开始获取邮件」{display_email}")

    attempts = 0
    link = None

    while attempts < max_attempts:
        print(f"第 {attempts+1} 次获取邮件中...")
        mail = None
        index = 0
        try:
            if method.upper() == 'IMAP':
                mail = imaplib.IMAP4_SSL(email_service)
                mail.login(email_name, password)
                mail.select('inbox')
                result, data = mail.search(None, 'ALL')
                email_ids = data[0].split()[-num_emails:]
            elif method.upper() == 'POP3':
                mail = poplib.POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                _, msg_list, _ = mail.list()
                email_ids = [msg.split(b' ')[0] for msg in msg_list][-num_emails:]
            else:
                print("不受支持的方法。请选择 IMAP 或 POP3.")
                return None

            for i in reversed(email_ids):
                if method.upper() == 'IMAP':
                    _, data = mail.fetch(i, '(RFC822)')
                    raw_email = data[0][1]
                elif method.upper() == 'POP3':
                    index = int(i.decode('utf-8').split(' ')[0])
                    _, lines, _ = mail.retr(index)
                    raw_email = b'\r\n'.join(lines)

                msg = email.message_from_bytes(raw_email)
                email_from = decode_header(msg.get('From'))[1][0]
                email_to = decode_header(msg.get('To'))[1][0]
                if target_email in str(email_from) and (display_email is None or display_email in str(email_to)):
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                url_pattern = r'(https?://\S+)'
                                urls = re.findall(url_pattern, body)

                                if urls:
                                    link = urls[0]
                                    print(f"找到链接: ", {"url": link, "email": email_to})

                    else:
                        body = msg.get_payload(decode=True).decode()
                        urls = re.findall(r'(https?://\S+)', body)
                        if urls:
                            link = urls[0]
                            print(f"找到链接: ", {"url": link, "email": email_to})

                    # Delete the email after extracting the link
                    if method.upper() == 'IMAP':
                        mail.store(i, '+FLAGS', '\\Deleted')
                    elif method.upper() == 'POP3':
                        mail.dele(index)


        except Exception as e:
            logger.error(f"错误发生，{e}，{retry_delay}秒后将重试...")
            if mail and method.upper() == 'IMAP':
                mail.expunge()
                mail.logout()
            elif mail and method.upper() == 'POP3':
                mail.quit()
            time.sleep(retry_delay)
        finally:

            if mail:
                if method.upper() == 'IMAP':
                    mail.expunge()
                    mail.logout()
                elif method.upper() == 'POP3':
                    mail.quit()
        attempts += 1
        if not link and attempts < max_attempts:
            print(f"错误发生，{retry_delay}秒后将重试...")
            time.sleep(retry_delay)
        else:
            break
    return link


def get_new_email(email_name, password, method='POP3', num_emails=100, display_email=None,
                  target_email='googlealerts-noreply@google.com',
                  email_service='outlook.office365.com', max_attempts=2, retry_delay=5):
    """
    尝试从指定邮箱中获取注册链接。
    """
    if display_email is None:
        logger.info("开始获取邮件")
    else:
        logger.info(f"开始获取邮件 {display_email}")

    attempts = 0
    new_items = []

    while attempts < max_attempts:
        print(f"第 {attempts + 1} 次获取邮件中...")
        mail = None
        try:
            if method.upper() == 'POP3':
                mail = poplib.POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                resp, items, octets = mail.list()
                email_ids = [item.split()[0] for item in items][-num_emails:]
            else:
                print("不受支持的方法。请选择 POP3。")
                return None

            for i in reversed(email_ids):
                i = i.decode() if isinstance(i, bytes) else i
                resp, lines, octets = mail.retr(i)
                msg_data = b"\r\n".join(lines)
                msg = email.message_from_bytes(msg_data)

                email_from = decode_header(msg.get('From'))[0][0]
                email_date = msg.get('Date')
                date_tuple = parsedate_tz(email_date)
                logger.info(f"处理邮件中「{email_from}----{email_date}」")
                if date_tuple:
                    date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                    formatted_date = date.strftime("%Y-%m-%d")

                if target_email in str(email_from):
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    pattern = r'=== News.*?\[(.*?)\].*?\r\n\r\n(.*?)\r\n.*?\r\n.*?\r\n.*?\r\n<(.*?)>'
                    matches = re.findall(pattern, body, re.DOTALL)

                    for match in matches:
                        gpt_keyword, title, url = match
                        url_pattern = r'(?<=url=)(.*?)(?=&ct=ga&)'
                        url_match = re.search(url_pattern, url)
                        extracted_url = url_match.group(1) if url_match else url
                        new_items.append(
                            {"keyword": gpt_keyword.strip(), "title": title.strip(), "url": extracted_url.strip(),
                             "date": formatted_date})

                mail.dele(i)
            if mail:
                mail.quit()

            # 成功获取到链接时跳出循环
            if new_items:
                logger.info("成功获取到邮件中的链接，停止重试。")
                break

        except Exception as e:
            logger.error(f"错误发生，{e}，{retry_delay}秒后将重试...")
            time.sleep(retry_delay)

        attempts += 1  # 移到 try/except 块之外，确保在出错和成功后都计数

    return new_items


def del_all_email(email_name, password, method='IMAP', num_emails=2000, target_email=None,
                    email_service='outlook.office365.com', max_attempts=2, retry_delay=5):

    logger.info(f"开始获取邮件」")
    attempts = 0
    mail = None
    while attempts < max_attempts:
        logger.info(f"第「{attempts+1}」次获取邮件中...")
        try:
            if method.upper() == 'IMAP':
                mail = IMAP4_SSL(email_service)
                mail.login(email_name, password)
                mail.select('inbox')
                result, data = mail.search(None, 'ALL')
                email_ids = data[0].split()[-num_emails:]

            elif method.upper() == 'POP3':
                mail = POP3_SSL(email_service)
                mail.user(email_name)
                mail.pass_(password)
                _, email_ids, _ = mail.list()
                email_ids = email_ids[-num_emails:]
            else:
                logger.debug(f"不受支持的方法。请选择 IMAP or POP3.")
                return None
            links = []
            for i in reversed(email_ids):
                if method.upper() == 'IMAP':
                    _, data = mail.fetch(i, '(RFC822)')
                    raw_email = data[0][1]
                elif method.upper() == 'POP3':
                    index = int(i.decode('utf-8').split(' ')[0])
                    _, lines, _ = mail.retr(index)
                    raw_email = b'\r\n'.join(lines)

                msg = email.message_from_bytes(raw_email)
                email_from = decode_header(msg.get('From'))[0][0]

                if target_email is None or target_email in str(email_from) :
                    # Delete the email after extracting the link
                    if method.upper() == 'IMAP':
                        mail.store(i, '+FLAGS', '\\Deleted')
                        print(f"{i}删除中")
                    elif method.upper() == 'POP3':
                        mail.dele(index)
                        print(f"删除中{index}")

            return links
        except Exception as e:
            logger.debug(f"获取失败!{e}")
        finally:
            attempts += 1
            if attempts < max_attempts:
                time.sleep(retry_delay)
            if mail is not None:
                if method.upper() == 'IMAP':
                    mail.logout()
                elif method.upper() == 'POP3':
                    mail.quit()

    logger.debug(f"获取邮件失败，{max_attempts}秒后重试.")
    return None



if __name__ == '__main__':

    # 设置你的邮箱和密码
    # email_service = 'outlook.office365.com'
    username = 'cgravely279@hotmail.com'
    password = 'y:7tq=IVhS+#'
    get_new_email(username,password)
