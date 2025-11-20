from mcp.server.fastmcp import FastMCP
import requests as req
import json
import os

from .config import api_url as ApiUrl

"""
打造自动调用yapi的mcp服务
"""
mcp = FastMCP('yapi')


@mcp.tool('yapi')
def get_iterface_info(id: int) -> str:

    """
    获取yapi接口基本信息
    :param login_password:
    :param login_email:
    :param id:
    :return:
    """

    email = os.getenv("login_email")
    password = os.getenv("login_password")

    data = {'email':email,'password':password}
    resp = req.post(ApiUrl.LOGIN_URL, json = data)

    # 获取 cookies
    cookies = resp.cookies

    interface_req = {'id': id}
    interface_info = req.get(ApiUrl.INTERFACE_INFO_URL, params=interface_req, cookies=cookies)
    if interface_info is None or interface_info.status_code != 200:
        print("接口信息获取失败")
        err_data = {'errcode':1,'errmsg':'接口信息获取失败'}
        return json.dumps(err_data)
    return interface_info.text


def main() -> None:
    print("启动yapi mcp服务")
    mcp.run()

if __name__ == '__main__':
    main()
    # print(get_iterface_info(5480, "jinghui.yu@ishansong.com", "YJHyjh123!@#"))
