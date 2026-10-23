"""统一异常与退出码（架构 §4.0）。"""
OK, UNEXPECTED, USAGE, MISSING_CONFIG, AUTH, BAD_INPUT, SERVICE, CHECK_FAILED = 0, 1, 2, 3, 4, 5, 6, 7


class SkillError(Exception):
    code = UNEXPECTED
    kind = "error"


class UsageError(SkillError):
    code = USAGE; kind = "usage"


class MissingKeyError(SkillError):
    code = MISSING_CONFIG; kind = "missing_env"

    def __init__(self, msg, *, kind="missing_env", env_path=None, var="DOUBAO_TTS_API_KEY"):
        super().__init__(msg)
        self.kind, self.env_path, self.var = kind, env_path, var


class TtsAuthError(SkillError):
    code = AUTH; kind = "auth"


class TtsTransientError(SkillError):
    code = SERVICE; kind = "transient"


class TtsBadRequest(SkillError):
    code = BAD_INPUT; kind = "bad_request"


class TtsServiceError(SkillError):
    """重试耗尽（退出码 6）。"""
    code = SERVICE; kind = "service_failed"


class SchemaError(SkillError):
    code = BAD_INPUT; kind = "schema"


class CheckFailed(SkillError):
    code = CHECK_FAILED; kind = "check_failed"
