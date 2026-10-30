import cdk_auth
from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction


@AgentServer.custom_action("check_cdk")
class CheckCdkAction(CustomAction):
    """按 ``custom_action_param.feature`` 调用 ``check_license``。

    参数示例：``{"feature": "base"}`` 或 ``{"feature": "activity"}``。
    缺省档位是 ``base``。返回 False 时节点动作失败。
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        del context  # 桩不操作控制器

        param = cdk_auth.load_param(argv.custom_action_param)
        if param is None:
            print("check_cdk: custom_action_param 需要是 JSON 对象")
            return False

        feature = param.get("feature", "base")
        ok = cdk_auth.check_license(feature)
        print(
            "check_cdk"
            f" feature={feature!r}"
            f" ok={ok}"
            f" dev_skip={cdk_auth.dev_skip_enabled()}"
            f" cdk_present={cdk_auth.cdk_is_present()}"
        )
        return ok
