from request import http
from twocaptcha import TwoCaptcha
from loghelper import log
import json
import config


def game_captcha(gt: str, challenge: str, url: str) -> dict:
    # challenge不要直接用传入的，老格式也还支持，但是建议优先使用新格式
    # 失败返回None 成功返回{"challenge":challenge,"validate":validate}
    return geetest(gt, challenge, url)


def bbs_captcha(gt: str, challenge: str, url: str) -> dict:
    return geetest(gt, challenge, url)


def geetest(gt: str, challenge: str, url: str):
    if "captcha" not in config.config:
        log.info('No captcha configured')
        return None
    if "api_key" not in config.config["captcha"]:
        log.info('No API key configured for captcha')
        return None

    log.info(f"[Captcha] 开始求解验证码, gt={gt}, challenge={challenge}, url={url}")

    api_key = config.config["captcha"]["api_key"]
    solver = TwoCaptcha(api_key, defaultTimeout=60, recaptchaTimeout=120)

    try:
        solver_response = solver.geetest(gt=gt, challenge=challenge, url=url)
        log.info(f"[Captcha] solver 返回: {solver_response}")

        if solver_response:
            code_json_str = solver_response["code"]
            if code_json_str:
                try:
                    parsed_code = json.loads(code_json_str)
                except json.JSONDecodeError:
                    log.warning(f"[Captcha] JSON 解析失败, 原始内容: {code_json_str}")
                    return None
                if parsed_code:
                    result = {
                        "challenge": parsed_code["geetest_challenge"],
                        "validate": parsed_code["geetest_validate"]
                    }
                    log.info(f"[Captcha] 求解成功, challenge={result['challenge']}, validate={result['validate']}")
                    return result
            else:
                log.warning("[Captcha] solver 返回的 code 为空")
        else:
            log.warning("[Captcha] solver 返回为空")
        return None
    except Exception as e:
        log.exception("[Captcha] 求解异常")
        return None
