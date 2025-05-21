from playwright.sync_api import sync_playwright
import os
import requests
# from dotenv import load_dotenv
import time


def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def  login_koyeb(email, password):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
#         browser = p.chromium.launch(
#     executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
#     channel="chrome",  # 明确指定渠道
#     headless=False
# )
        incognito_context = browser.new_context()

        page = incognito_context.new_page()

        # 访问登录页面  
        page.goto("https://freecloud.ltd/login", timeout=60000)
        page.wait_for_selector("text=点击登录", timeout=60000)


        # 输入邮箱和密码
        page.get_by_placeholder("用户名/邮箱/手机号").click()
        page.get_by_placeholder("用户名/邮箱/手机号").fill(email)
        page.get_by_placeholder("请输入登录密码").click()
        page.get_by_placeholder("请输入登录密码").fill(password)
        checkbox_selector = "input[name='agree']"
        # 检查是否选中
        is_checked = page.is_checked(checkbox_selector)

        if is_checked:
            print("复选框已选中")
        else:
            # 点击复选框
            page.click(checkbox_selector)
            print("复选框未选中")
    
        # 点击登录按钮
        # 等待按钮出现并点击
        page.click("text=点击登录")

        # 等待可能出现的错误消息或成功登录后的页面
        try:
            # 等待可能的错误消息
            error_message = page.wait_for_selector('//div[contains(@class, "jq-icon-error") and contains(@style, "display: block")]',timeout=30000)
            if error_message:
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息,检查是否已经跳转到仪表板页面
            try:
                page.wait_for_url("https://freecloud.ltd/member/index", timeout=30000)
                page.locator('a[href="https://freecloud.ltd/server/lxc"]').all()[0].click()
                time.sleep(5)
                page.wait_for_selector('a[data-modal*="/server/detail/"][data-modal*="/renew"]').click()
                # page.wait_for_selector('a[data-modal="https://freecloud.ltd/server/detail/2128/renew?type=list"]').click()
                page.wait_for_selector("#submitRenew").click()
                full_html =  page.content()  # 获取完整页面 HTML
                print(full_html)
                time.sleep(5)
                return f"账号 {email} 登录成功!"
            except Exception  as e:
                print(f"发生异常{e}")
                full_html =  page.content()  # 获取完整页面 HTML
                print(full_html)
                page.screenshot(path="failure_screenshot.png")
                with open("failure_page.html", "w", encoding="utf-8") as f:f.write(page.content())
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        finally:
            browser.close()

if __name__ == "__main__":
    # load_dotenv()
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_koyeb(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "WEBHOST登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
    else:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        print(error_message)
