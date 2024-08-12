from request import http
from twocaptcha import TwoCaptcha
from loghelper import log
import json
import config


def game_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge,
                       "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                       "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    return validate  # 失败返回None 成功返回validate


def bbs_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
    return validate  # 失败返回None 成功返回validate


def geetest(gt: str, challenge: str, referer: str):
    if "captcha" not in config.config:
        log.info('No captcha configured')
        return None
    if "api_key" not in config.config["captcha"]:
        log.info('No API key configured for captcha')
        return None

    api_key = config.config["captcha"]["api_key"]
    solver = TwoCaptcha(api_key, defaultTimeout=60, recaptchaTimeout=120)

    try:
        result = solver.geetest(gt=gt, challenge=challenge, url=referer)

        if result:
            result_code = result["code"]
            if result_code:
                json_result_code = json.loads(result_code)
                if json_result_code:
                    geetest_validate = json_result_code["geetest_validate"]
                    return geetest_validate
        return None
    except Exception as e:
        log.exception("captcha error")
        log.exception(e)
        return None
