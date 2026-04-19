from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class ReportRequest:
    raw_text: str
    force_template: str | None = None
    include_chief_version: bool = False
    include_council_version: bool = False
    preserve_verbatim: bool = False


class TiaochenBot:
    """萬華分局條陳生成器：預設輸出康定所報告＋萬華分局報告。"""

    CASE_ROUTER: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
        ("fraud", ("165案號", "165", "面交", "投資", "詐欺", "匯款")),
        ("drug", ("毒駕", "毒品", "愷他命", "安非他命", "K他命")),
        ("dui", ("酒駕", "公共危險")),
        ("group_brawl", ("鬥毆", "聚眾")),
        ("fight", ("打架", "口角", "推拉", "傷害")),
        ("theft", ("竊盜", "失竊", "遭竊", "監視器")),
        ("death", ("死亡", "行政相驗", "OHCA")),
        ("fire_or_signal", ("119", "火災", "誤報火災", "號誌")),
    )

    PREFERRED_REPLACEMENTS = {
        "然後": "嗣經",
        "後來": "嗣經",
        "看到": "見",
        "沒有": "未見",
        "好像": "疑似",
        "帶回去": "帶返所",
        "做筆錄": "製作筆錄",
        "後續": "嗣經",
    }

    def generate(self, req: ReportRequest) -> Dict[str, str]:
        template = req.force_template or self._classify(req.raw_text)
        if req.preserve_verbatim:
            station_body = self._strip_blank_lines(req.raw_text.strip())
            precinct_body = station_body
        else:
            station_body = self._render_station(template, req.raw_text)
            precinct_body = self._render_precinct(template, req.raw_text)

        reports: Dict[str, str] = {
            "康定所報告": f"康定所報告：\n{station_body}",
            "萬華分局報告": f"萬華分局報告：\n{precinct_body}",
        }

        if req.include_chief_version:
            reports["報局長版本"] = self._render_chief(template, req.raw_text)
        if req.include_council_version:
            reports["回覆議座版本"] = self._render_council(req.raw_text)
        return reports

    def _classify(self, text: str) -> str:
        for case_type, keywords in self.CASE_ROUTER:
            if any(keyword in text for keyword in keywords):
                return case_type
        return "generic"

    def _render_station(self, template: str, text: str) -> str:
        t = self._sanitize(text)
        if template == "fraud":
            lines = [
                "一、案由：詐欺案（偵辦中）",
                "二、發生時間：待查",
                "三、發生地點：待查",
                "四、報案時間：待查",
                "五、現住地點：待查",
                f"六、案情摘要：{self._fraud_summary(t)}",
                "七、偵辦情形：經查已調閱相關資料釐清金流與涉案對象，依法移請偵辦。",
                "八、受理案號：E化案號待補、165案號待補。",
                "九、心理諮商：依規定辦理。",
                "十、媒體關注：尚無。",
                "十一、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "drug":
            lines = [
                "一、案由：查獲毒品（含毒駕）案",
                "二、查獲時間：待查",
                "三、查獲地點：待查",
                f"四、查處情形：{t}；經查毒品級別待鑑驗確認，依法舉發並製作生理平衡觀測表。",
                "五、溯源情形：嗣經溯源釐清上手與供應來源，續函請偵辦。",
                "六、處理員警：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "theft":
            lines = [
                "一、案由：竊盜案（已掌握身分並製發通知書）",
                "二、發生時間：待查",
                "三、發生地點：待查",
                f"四、案情摘要：{t}",
                "五、偵辦情形：經調閱監視器畫面比對，查知涉案對象，嗣經通知到案說明並函請偵辦。",
                "六、媒體關注：尚無。",
                "七、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "group_brawl":
            lines = [
                "一、案由：聚眾鬥毆案",
                "二、報案時間：待查",
                "三、地點：待查",
                f"四、案情摘要：{t}",
                "五、處置情形：經查現場參與人數待清查；到場前離去人員另通知到案；現行犯依法逮捕移送；其餘涉案對象函送偵辦；傷害告訴併案處理。",
                "六、媒體關注：尚無。",
                "七、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "fight":
            lines = [
                "一、案由：打架（傷害）案",
                "二、時間：待查",
                "三、地點：待查",
                f"四、案情摘要：{t}",
                "五、處置情形：（一）到場未見持續打架情事，經查係口角衍生肢體衝突。（二）警方已告知權利並通知到案說明，依法移請偵辦。",
                "六、媒體關注：尚無。",
                "七、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "death":
            lines = [
                "一、案由：死亡案（行政相驗）",
                "二、時間：待查",
                "三、地點：待查",
                "四、查處情形：（一）接獲通報後派員到場，家屬表示放棄急救。（二）經查死者有相關病史，尚無外力介入情事，家屬並無疑義。（三）現場未見打鬥或破壞跡象，已通知偵查隊及鑑識人員知悉。",
                "五、媒體關注：尚無。",
                "六、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "dui":
            lines = [
                "一、案由：查獲公共危險案（酒後駕車）",
                "二、查獲時間：待查",
                "三、查獲地點：待查",
                f"四、查獲情形：{t}",
                "五、處置：依法舉發、告知權利、帶返所製作筆錄，涉案車輛移置保管，並移請偵辦。",
                "六、處理員警：康定所員警。",
            ]
            return self._join_lines(lines)

        if template == "fire_or_signal":
            lines = [
                "一、案由：火災／誤報火災／號誌異常案（結報）",
                "二、時間：待查",
                "三、地點：待查",
                f"四、查處情形：（一）勤務指揮中心轉報後派員到場。（二）經查現場狀況為：{t}。（三）確認無危害且已通知權責機關處置完成。",
                "五、媒體關注：尚無。",
                "六、處理人員：康定所員警。",
            ]
            return self._join_lines(lines)

        lines = [
            "一、案由：一般案件",
            "二、時間：待查",
            "三、地點：待查",
            f"四、案情摘要：{t}",
            "五、處置情形：經查相關事證後，依法續辦。",
            "六、媒體關注：尚無。",
            "七、處理人員：康定所員警。",
        ]
        return self._join_lines(lines)

    def _render_precinct(self, template: str, text: str) -> str:
        # 分局版與所版同事實，語句更短
        station = self._render_station(template, text)
        short = station.replace("康定所員警", "分局員警")
        short = short.replace("依法移請偵辦", "依法偵辦")
        return self._join_lines(short.splitlines())

    def _render_chief(self, template: str, raw_text: str) -> str:
        t = self._sanitize(raw_text)
        lines = [
            "萬華分局報告（時間碼）：",
            f"1. 案由：{template}",
            "2. 時間：待查",
            "3. 地點：待查",
            f"4. 案情摘要：{t}",
            "5. 偵處情形：經查已責由相關單位依法處置並持續管制。",
            "6. 涉警／廉政檢核：尚無。",
            "7. 媒體情形：尚無。",
            "8. 職○○○謹陳",
        ]
        return self._join_lines(lines)

    def _render_council(self, raw_text: str) -> str:
        t = self._sanitize(raw_text)
        lines = [
            "報告議座：",
            "一、警方接獲報案後即派員到場查處，並掌握重要事實。",
            f"二、警方已聯繫當事人釐清案情，重點如下：{t}",
            "三、另聯繫家屬說明病況或實情，並轉達議座關切。",
            "以上說明。",
        ]
        return self._join_lines(lines)

    def _sanitize(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        text = self._normalize_time(text)
        for bad, good in self.PREFERRED_REPLACEMENTS.items():
            text = text.replace(bad, good)
        return text

    def _normalize_time(self, text: str) -> str:
        # 115年04月02日 -> 115年4月2日
        text = re.sub(r"(\d+)年0?(\d{1,2})月0?(\d{1,2})日", lambda m: f"{m.group(1)}年{int(m.group(2))}月{int(m.group(3))}日", text)
        # 23時05分 -> 23時5分
        text = re.sub(r"(\d{1,2})時0?(\d{1,2})分", lambda m: f"{int(m.group(1))}時{int(m.group(2))}分", text)
        return text

    @staticmethod
    def _fraud_summary(text: str) -> str:
        # 詐欺摘要盡量壓縮，只保留詐術與金額
        amount_match = re.search(r"(\d+[萬千百十]?[元塊]?|新台幣\d+[萬千百十]?元?)", text)
        amount = amount_match.group(0) if amount_match else "金額待查"
        if "投資" in text:
            method = "誤信網路投資廣告"
        elif "網拍" in text:
            method = "遭假網拍手法詐騙"
        elif "面交" in text:
            method = "遭詐團以面交投資款手法詐騙"
        else:
            method = "遭詐欺手法誘騙"
        return f"被害人{method}，損失{amount}。"

    @staticmethod
    def _strip_blank_lines(text: str) -> str:
        return "\n".join(line for line in text.splitlines() if line.strip())

    def _join_lines(self, lines: List[str]) -> str:
        compact = [line.strip() for line in lines if line and line.strip()]
        return "\n".join(compact)


def _read_input(raw_arg: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if raw_arg:
        return raw_arg
    raise ValueError("請提供案件內容（參數或 --input-file）。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="康定所／萬華分局條陳生成器")
    parser.add_argument("input", nargs="?", help="原始案情文字")
    parser.add_argument("--input-file", help="從 UTF-8 檔案讀取原始案情")
    parser.add_argument("--template", help="強制指定案型（fraud/drug/theft/fight/group_brawl/death/dui）")
    parser.add_argument("--chief", action="store_true", help="輸出報局長版本")
    parser.add_argument("--council", action="store_true", help="輸出回覆議座版本")
    parser.add_argument("--verbatim", action="store_true", help="原文照登，不作修改")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_text = _read_input(args.input, args.input_file)
    req = ReportRequest(
        raw_text=raw_text,
        force_template=args.template,
        include_chief_version=args.chief,
        include_council_version=args.council,
        preserve_verbatim=args.verbatim,
    )
    reports = TiaochenBot().generate(req)
    for name, content in reports.items():
        print(f"\n===== {name} =====")
        print(content)


if __name__ == "__main__":
    main()
