import cdk_auth
from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition


@AgentServer.custom_recognition("cdk_gate")
class CdkGateRecognition(CustomRecognition):
    """授权门闩。通过时命中一个 1×1 占位框，失败时不命中。

    ``custom_recognition_param``：``{"feature": "base"}`` 或 ``activity``。
    开发模式默认通过，方便在没有模板图时先把节点跑通。
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        del context

        param = cdk_auth.load_param(argv.custom_recognition_param)
        if param is None:
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={"error": "custom_recognition_param 需要是 JSON 对象"},
            )

        feature = param.get("feature", "base")
        ok = cdk_auth.check_license(feature)
        detail = {
            "feature": feature,
            "ok": ok,
            "dev_skip": cdk_auth.dev_skip_enabled(),
            "cdk_present": cdk_auth.cdk_is_present(),
        }
        print(f"cdk_gate {detail}")
        if not ok:
            return CustomRecognition.AnalyzeResult(box=None, detail=detail)
        return CustomRecognition.AnalyzeResult(box=[0, 0, 1, 1], detail=detail)
